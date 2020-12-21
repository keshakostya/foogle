import dataclasses
import os
from pathlib import Path

import pytest

from foogle.engine.query_parser import Query
from foogle.engine.search_engine import SearchEngine, \
    SearchByManyQueriesResult, SearchByOneQueryResult
from foogle.errors.errors import IndexNotExistError, IndexEmptyError, \
    RobotTxtNotFound, InvalidRootDirectory


@pytest.fixture
def norm_cwd() -> Path:
    cwd = Path.cwd()
    if not cwd.name == 'test':
        os.chdir('test')
    return Path.cwd()


@pytest.fixture
def search_engine():
    engine = SearchEngine()
    return engine


def test_search(search_engine, norm_cwd):
    test_files = norm_cwd / 'test_files'
    search_engine.build_index(str(test_files), '')
    results = search_engine.search('lorem || lingues')
    expected = SearchByManyQueriesResult([
        SearchByOneQueryResult(Query({'lorem'}, set()),
                               [test_files / 'a.txt']),
        SearchByOneQueryResult(Query({'lingues'}, set()),
                               [test_files / 'b.txt',
                                test_files / 'c.txt'])])
    assert results == expected


def test_search_with_robot_txt(search_engine, norm_cwd):
    test_files = norm_cwd / 'test_files'
    search_engine.build_index(str(test_files), 'robot.txt')
    expected_files = {test_files / 'c.txt', test_files / 'd.txt'}
    assert set(search_engine.index.documents) == expected_files


def test_save_load(search_engine, norm_cwd):
    test_files = norm_cwd / 'test_files'
    search_engine.build_index(str(test_files), '')
    search_engine.save_index()
    index_path = norm_cwd / 'search_index'
    assert index_path.exists()
    index = dataclasses.replace(search_engine.index)
    search_engine.index = None
    search_engine.load_index()
    assert index == search_engine.index
    index_path.unlink()


def test_engine_load_error(search_engine):
    with pytest.raises(IndexNotExistError):
        search_engine.load_index()


def test_engine_search_error(search_engine):
    with pytest.raises(IndexEmptyError):
        search_engine.search('a')


@pytest.mark.parametrize(
    'search_arg, expected_error',
    [
        (('./', 'wrong_path'), RobotTxtNotFound),
        (('wrong_path', 'robot.txt'), InvalidRootDirectory)
    ]
)
def test_engine_search_build(search_engine, search_arg, expected_error):
    with pytest.raises(expected_error):
        search_engine.build_index(*search_arg)
