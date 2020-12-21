from typing import Union

from foogle.engine.search_engine import SearchEngine, \
    SearchByManyQueriesResult
from foogle.errors.errors import SearcherError


class Controller:

    def __init__(self):
        self.engine = SearchEngine()
        self.commands = {
            'search': self.__search,
            'build_index': self.__build_index,
            'load_index': self.__load_index,
            'save_index': self.__save_index
        }

    def execute(self, command: str, *args) -> \
            Union[SearchByManyQueriesResult, str]:
        try:
            return self.commands[command](*args)
        except SearcherError as e:
            return e.message

    def __search(self, query: str) -> SearchByManyQueriesResult:
        return self.engine.search(query)

    def __build_index(self, root_dir: str, robot_txt: str = '') -> str:
        self.engine.build_index(root_dir, robot_txt)
        return f'Index built for "{self.engine.index.root_path}"'

    def __load_index(self) -> str:
        self.engine.load_index()
        return f'Index for {self.engine.index.root_path} loaded'

    def __save_index(self) -> str:
        self.engine.save_index()
        return f'Index for {self.engine.index.root_path} saved'
