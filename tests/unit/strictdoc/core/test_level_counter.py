from strictdoc.core.level_counter import LevelCounter


def test_01():
    level_counter = LevelCounter()
    assert level_counter.get_string() == ""

    level_counter.adjust(1)
    assert level_counter.get_string() == "1"

    level_counter.adjust(1)
    assert level_counter.get_string() == "2"

    level_counter.adjust(2)
    assert level_counter.get_string() == "2.1"

    level_counter.adjust(3)
    assert level_counter.get_string() == "2.1.1"

    level_counter.adjust(2)
    assert level_counter.get_string() == "2.2"

    level_counter.adjust(1)
    assert level_counter.get_string() == "3"
