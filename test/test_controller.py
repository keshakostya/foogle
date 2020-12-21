import os
from pathlib import Path
import pytest

from searcher.controller.controller import Controller
from searcher.engine.query_parser import Query
from searcher.engine.search_engine import SearchByManyQueriesResult, \
    SearchByOneQueryResult


@pytest.fixture
def controller():
    return Controller()


@pytest.fixture
def norm_cwd() -> Path:
    cwd = Path.cwd()
    if not cwd.name == 'test':
        os.chdir('test')
    return Path.cwd()


def test_controller(controller, norm_cwd):
    test_files_path = norm_cwd / 'test_files'
    res = controller.execute('build_index', 'test_files')
    assert res == f'Index built for "{test_files_path}"'
    res = controller.execute('save_index')
    assert res == f'Index for {test_files_path} saved'
    index_path = norm_cwd / 'search_index'
    assert index_path.exists()
    res = controller.execute('load_index')
    assert res == f'Index for {test_files_path} loaded'
    index_path.unlink()
    res = controller.execute('search', 'lorem')
    expected = SearchByManyQueriesResult([
        SearchByOneQueryResult(Query({'lorem'}, set()),
                               [test_files_path / 'a.txt'])])
    assert res == expected
