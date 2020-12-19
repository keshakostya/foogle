import pytest

from searcher.engine.query_parser import QueryParser, Query


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