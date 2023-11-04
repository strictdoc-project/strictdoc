from strictdoc.helpers.shard import get_shard


def test_get_shard():
    assert get_shard(10, 10, 1) == (0, 1)
    assert get_shard(10, 10, 10) == (9, 10)

    assert get_shard(11, 10, 10) == (9, 11)

    assert get_shard(15, 10, 9) == (8, 9)
    assert get_shard(15, 10, 10) == (9, 15)

    assert get_shard(180, 5, 1) == (0, 36)
    assert get_shard(180, 5, 2) == (36, 72)
    assert get_shard(180, 5, 3) == (72, 108)
    assert get_shard(180, 5, 4) == (108, 144)
    assert get_shard(180, 5, 5) == (144, 180)

    assert get_shard(181, 5, 1) == (0, 36)
    assert get_shard(181, 5, 2) == (36, 72)
    assert get_shard(181, 5, 3) == (72, 108)
    assert get_shard(181, 5, 4) == (108, 144)
    assert get_shard(181, 5, 5) == (144, 181)
