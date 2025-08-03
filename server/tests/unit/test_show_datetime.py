import datetime

import pytest

from server.main import update_show_date


@pytest.mark.parametrize(
    "num, know_the_word, expected",
    [
        (0, True, None),
        (1, True, 2),
        (2, True, 3),
        (3, True, 4),
        (4, True, 5),
        (5, True, 6),
        (6, True, 7),
        (7, True, None),
        (0, False, 1),
        (1, False, 1),
        (2, False, 1),
        (3, False, 1),
        (4, False, 1),
        (5, False, 1),
        (6, False, 1),
        (7, False, 1),
    ],
)
def test_update_show_date(num, know_the_word, expected):
    result = update_show_date(num, know_the_word)
    if result is None:
        assert expected is None
    else:
        next_show_date, count = result
        if next_show_date is not None:
            assert isinstance(next_show_date, datetime.datetime)
        assert count == expected
