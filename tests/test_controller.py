from pathlib import Path
import pytest

from foogle.engine.controller import Controller
from foogle.engine.query_parser import Query
from foogle.engine.search_engine import SearchByManyQueriesResult, \
    SearchByOneQueryResult


@pytest.fixture
def controller():
    return Controller()


def test_controller(controller):
    test_files_path = Path.cwd() / 'test_files'
    res = controller.execute('build_index', str(test_files_path))
    assert res == f'Index built for "{test_files_path}"'
    res = controller.execute('save_index')
    assert res == f'Index for {test_files_path} saved'
    index_path = Path.cwd() / 'search_index'
    assert index_path.exists()
    res = controller.execute('load_index')
    assert res == f'Index for {test_files_path} loaded'
    index_path.unlink()
    res = controller.execute('search', 'lorem')
    expected = SearchByManyQueriesResult([
        SearchByOneQueryResult(Query({'lorem'}, set()),
                               [test_files_path / 'a.txt'])])
    assert res == expected
