import re

from dataclasses import dataclass, field
from typing import Set, List, Optional

from foogle.errors.errors import QueryError


@dataclass
class Query:
    good_terms: Set[str] = field(default_factory=set)
    bad_terms: Set[str] = field(default_factory=set)

    def __eq__(self, other: 'Query'):
        return self.good_terms == other.good_terms and \
               self.bad_terms == other.bad_terms

    def __hash__(self):
        hsh = 0
        for term in self.good_terms | self.bad_terms:
            hsh += hash(term)
        return hsh

    def __str__(self):
        good_terms_str = ' && '.join(self.good_terms)
        bad_terms_str = ' && -'.join(self.bad_terms)
        query = []
        if good_terms_str:
            query.append(good_terms_str)
        if bad_terms_str:
            bad_terms_str = '-' + bad_terms_str
            query.append(bad_terms_str)
        query_str = ' && '.join(query)
        return f'Query(transformed): {query_str}'

    def is_empty(self):
        return not self.bad_terms and not self.good_terms


class QueryParser:
    @staticmethod
    def parse_query(raw_query: str) -> Set[Query]:
        if not raw_query:
            raise QueryError(raw_query)
        query_parts = raw_query.lower().split(' ')
        stack = []
        united_terms = []
        queries = set()
        for token in query_parts:
            if len(stack) > 1:
                raise QueryError(raw_query)
            if token == '||':
                united_terms.extend(stack)
                if not united_terms:
                    continue
                query = QueryParser.create_query(united_terms)
                if query:
                    queries.add(query)
                stack.clear()
                united_terms.clear()
            elif token == '&&':
                united_terms.extend(stack)
                stack.clear()
            else:
                stack.append(token)
        if len(stack) > 1:
            raise QueryError(raw_query)
        if stack:
            united_terms.extend(stack)
        if united_terms:
            query = QueryParser.create_query(united_terms)
            if query:
                queries.add(query)
        queries = set([query for query in queries if not query.is_empty()])
        if not queries:
            raise QueryError(raw_query)
        return queries

    @staticmethod
    def create_query(terms: List[str]) -> Optional[Query]:
        good_terms = set()
        bad_terms = set()
        pattern = re.compile(r'[\W_]+')
        for term in terms:
            if term.startswith('-'):
                term = pattern.sub('', term[1:])
                bad_terms.add(term)
            else:
                term = pattern.sub('', term)
                good_terms.add(term)
        if not good_terms & bad_terms:
            return Query(good_terms, bad_terms)
        return None
