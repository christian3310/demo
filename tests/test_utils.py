import pytest

from app.utils import split


TEST_LIST = [1] * 20


@pytest.mark.parametrize(
    'list_,chunks,length_of_each_chunk',
    [
        (TEST_LIST, 3, [7, 7, 6]),
        (TEST_LIST, 5, [4, 4, 4, 4, 4]),
        (TEST_LIST, 7, [3, 3, 3, 3, 3, 3, 2]),
        (TEST_LIST, 9, [3, 3, 2, 2, 2, 2, 2, 2, 2]),
        (TEST_LIST, 11, [2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1])
    ]

)
def test_split_func(list_, chunks, length_of_each_chunk):
    result = [len(_) for _ in split(list_, chunks)]
    assert result == length_of_each_chunk
