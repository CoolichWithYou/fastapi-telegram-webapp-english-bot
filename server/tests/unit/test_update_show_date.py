from server.main import update_show_date


def test_update_show_date():
    show_time, count = update_show_date(6, True)
    assert count == 7

    show_time, count = update_show_date(1, True)
    assert count == 2

    show_time, count = update_show_date(6, False)
    assert count == 1
