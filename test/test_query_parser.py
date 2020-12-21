import pytest

from foogle.engine.query_parser import QueryParser, Query
from foogle.engine.errors import QueryError


@pytest.mark.parametrize(
    ('raw_query', 'expected_queries'), [
        ('Hello || world', [Query({'hello', }),
                            Query({'world', })]),
        ('ruby || python && -java', [Query({'ruby', }),
                                     Query({'python', }, {'java', })])
    ]
)
def test_queries(raw_query, expected_queries):
    assert set(QueryParser.parse_query(raw_query)) == set(expected_queries)


@pytest.mark.parametrize(
    'query',
    [
        'Hello world',
        'hello && -hello'
     ]
)
def test_query_error(query):
    with pytest.raises(QueryError):
        QueryParser.parse_query(query)
