from searcher.engine.search_engine import SearchEngine
from searcher.errors.errors import SearcherError


class Controller:

    def __init__(self):
        self.engine = SearchEngine()
        self.commands = {
            'search': self._search,
            'build_index': self._build_index,
            'load_index': self._load_index,
            'save_index': self._save_index
        }

    def execute(self, command: str, *args):
        try:
            return self.commands[command](*args)
        except SearcherError as e:
            return e.message

    def _search(self, query: str):
        return self.engine.search(query)

    def _build_index(self, root_dir: str, robot_txt: str = ''):
        self.engine.build_index(root_dir, robot_txt)
        return f'Index built for "{self.engine.index.root_path}"'

    def _load_index(self):
        self.engine.load_index()
        return f'Index for {self.engine.index.root_path} loaded'

    def _save_index(self):
        self.engine.save_index()
        return f'Index for {self.engine.index.root_path} saved'
