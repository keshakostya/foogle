import collections
import math
import pickle
import re
import time
from dataclasses import dataclass
from hashlib import md5
from pathlib import Path
from typing import Generator, Set, Dict, List, Tuple, Counter, Optional

import magic

from searcher.engine.query_parser import Query, QueryParser
from searcher.errors.errors import IndexEmptyError, IndexBrokenError, \
    IndexNotExistError, IndexOutDatedError, InvalidRootDirectory, \
    RobotTxtNotFound


@dataclass
class Index:
    root_path: Path
    mtime: float
    documents_to_terms: Dict
    terms_to_documents: Dict
    tf_idf: Dict

    @property
    def unique_terms(self) -> Set:
        return set(self.terms_to_documents.keys())

    @property
    def documents(self) -> Set:
        return set(self.documents_to_terms)

    @property
    def collection_size(self) -> int:
        return len(self.documents_to_terms)

    @property
    def is_empty(self) -> bool:
        return not (self.root_path
                    and self.mtime
                    and self.documents_to_terms
                    and self.terms_to_documents
                    and self.tf_idf)


@dataclass
class SearchByOneQueryResult:
    query: Query
    documents: List

    def __str__(self) -> str:
        string_paths = map(str, self.documents)
        return 'Searched with query {}\n' \
               'Found {} files(s):\n{}\n\n'.format(self.query,
                                                   len(self.documents),
                                                   '\n'.join(string_paths))

    def __eq__(self, other: 'SearchByOneQueryResult') -> bool:
        if len(self.documents) != len(other.documents):
            return False
        for i, doc in enumerate(self.documents):
            if doc != other.documents[i]:
                return False
        return self.query == other.query

    def __hash__(self) -> int:
        hsh = hash(self.query)
        for doc in self.documents:
            hsh += hash(doc)
        return hsh

    def is_empty(self) -> bool:
        return bool(self.documents)


@dataclass
class SearchByManyQueriesResult:
    search_results: List[SearchByOneQueryResult]

    def __str__(self) -> str:
        return 'Performed search by content.\n' \
               'Results:\n{}'.format(''.join(map(str, self.search_results)))

    def __eq__(self, other: 'SearchByManyQueriesResult') -> bool:
        return set(self.search_results) == set(other.search_results)

    def __iter__(self):
        return self.search_results.__iter__()


class SearchEngine:

    def __init__(self):
        self.index: Optional[Index] = None

    def check_index_exist(self):
        if not self.index:
            raise IndexEmptyError()

    def load_index(self):
        index_path = Path('index').absolute()
        try:
            with index_path.open('rb') as f:
                check_sum = f.read(16)
                raw_index = f.read()
                assert check_sum == self.calc_md5(raw_index)
                self.index: Index = pickle.loads(raw_index)
                if self.index.mtime < self.index.root_path.stat().st_mtime:
                    root_path = self.index.root_path
                    self.index = None
                    index_path.unlink()
                    raise IndexOutDatedError(str(root_path))
        except (AssertionError, pickle.PickleError):
            index_path.unlink()
            raise IndexBrokenError()
        except FileNotFoundError:
            raise IndexNotExistError()

    def save_index(self):
        self.check_index_exist()
        index_path = Path('index').absolute()
        pickled_index = pickle.dumps(self.index)
        check_sum = self.calc_md5(pickled_index)
        with index_path.open('wb') as f:
            f.write(check_sum)
            f.write(pickled_index)

    def search(self, query: str) -> SearchByManyQueriesResult:
        self.check_index_exist()
        queries = QueryParser.parse_query(query)
        results = []
        for query in queries:
            results.append(self.search_by_one_query(query))
        return SearchByManyQueriesResult(results)

    def search_by_one_query(self, query: Query) -> SearchByOneQueryResult:
        documents_score = collections.Counter()
        bad_docs = set()
        for bad_term in query.bad_terms:
            if bad_term in self.index.terms_to_documents:
                bad_docs |= set(
                    self.index.terms_to_documents[bad_term]
                )
        if not query.good_terms:
            found_docs = list(self.index.documents_to_terms.keys() - bad_docs)
            return SearchByOneQueryResult(query, found_docs)
        good_docs = set()
        for term in query.good_terms:
            if term not in self.index.terms_to_documents:
                continue
            if not good_docs:
                good_docs = set(self.index.terms_to_documents[term])
            else:
                good_docs &= set(self.index.terms_to_documents[term])
        good_docs -= bad_docs
        for term in query.good_terms:
            if term not in self.index.terms_to_documents:
                continue
            for doc in good_docs:
                document_tf_idf = self.index.tf_idf[doc]
                documents_score[doc] += document_tf_idf[term]
        return SearchByOneQueryResult(query, sorted(documents_score,
                                                    key=lambda document: -
                                                    documents_score[
                                                        document]))

    def build_index(self, root_dir: str, robot_txt: str):
        ignored = self.collect_ignored(robot_txt) if robot_txt else set()
        documents_to_terms, terms_to_documents = \
            self.collect_documents_and_terms(root_dir, ignored)
        tf = self.compute_tf(documents_to_terms)
        idf = self.compute_idf(documents_to_terms)
        tf_idf = self.compute_tf_idf(tf, idf)
        self.index = Index(Path(root_dir).absolute(),
                           time.time(),
                           documents_to_terms,
                           terms_to_documents,
                           tf_idf)

    def collect_documents_and_terms(self, root_dir: str,
                                    ignored: Set[Path]) -> \
            Tuple[Dict[Path, Counter[str]], Dict[str, List[Path]]]:
        documents_to_terms = {}
        terms_to_documents = collections.defaultdict(list)
        for doc in self.walk_documents(root_dir, ignored):
            doc_size = doc.stat().st_size
            if doc_size == 0:
                continue
            encoding = self.get_file_encoding(str(doc))
            if encoding == 'binary':
                continue
            document_terms = self.read_document(doc, encoding)
            documents_to_terms[doc] = collections.Counter(document_terms)
            for term in document_terms:
                terms_to_documents[term].append(doc)
        return documents_to_terms, terms_to_documents

    @staticmethod
    def compute_tf(documents_to_terms: Dict[Path, Counter[str]]) -> \
            Dict[Path, Dict[str, float]]:
        tf = {}
        for document, terms in documents_to_terms.items():
            tf_by_document = {}
            total_terms = sum(terms.values())
            for term, count in terms.items():
                tf_by_document[term] = count / total_terms
            tf[document] = tf_by_document
        return tf

    @staticmethod
    def compute_idf(documents_to_terms: Dict[Path, Counter[str]]) -> \
            Dict[str, float]:
        idf = {}
        terms_to_docs_count_with_term = collections.Counter()
        for document in documents_to_terms:
            for term in documents_to_terms[document]:
                terms_to_docs_count_with_term[term] += 1
        for term, count in terms_to_docs_count_with_term.items():
            idf[term] = math.log(len(documents_to_terms) / count, math.e)
        return idf

    @staticmethod
    def compute_tf_idf(tf: Dict[Path, Dict[str, float]],
                       idf: Dict[str, float]) -> Dict[Path, Dict[str, float]]:
        tf_idf = {}
        for document, document_tf in tf.items():
            tf_idf[document] = {}
            for term in document_tf:
                tf_idf[document][term] = document_tf.get(term, 0) * idf[term]
        return tf_idf

    @staticmethod
    def walk_documents(root_dir: str, ignored: Set[Path]) -> \
            Generator[Path, None, None]:
        root_path = Path(root_dir).absolute()
        if not root_path.is_dir():
            raise InvalidRootDirectory(root_dir)
        for path in root_path.rglob('*'):
            if path.is_dir() or path in ignored:
                continue
            yield path

    @staticmethod
    def read_document(document: Path, encoding: str) -> List[str]:
        terms = []
        with document.open('r', encoding=encoding) as f:
            while True:
                line = f.readline().lower()
                if not line:
                    return terms
                terms.extend(re.sub(r'[\W_\-]', ' ', line).split())

    @staticmethod
    def collect_ignored(robot_txt: str) -> Set[Path]:
        robot_txt_path = Path(robot_txt).absolute()
        if not robot_txt_path.exists() or robot_txt_path.is_dir():
            raise RobotTxtNotFound(robot_txt)
        ignored = set()
        cwd = Path.cwd()
        with robot_txt_path.open('r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if line[-1] == '\n':
                    line = line[:-1]
                for path in cwd.rglob(line):
                    if not path.is_dir():
                        ignored.add(path)
                    else:
                        for path1 in path.rglob('*'):
                            ignored.add(path1)
        return ignored

    @staticmethod
    def get_file_encoding(file: str) -> str:
        return magic.Magic(mime_encoding=True).from_file(file)

    @staticmethod
    def calc_md5(data: bytes) -> bytes:
        return md5(data).digest()
