from typing import Tuple


def get_shard(total: int, shards: int, shard: int) -> Tuple[int, int]:
    assert 0 < total, total
    assert 0 < shard <= shards, (shard, shards)
    assert shards <= total, (shards, total)

    shard_size = total // shards
    shard_size_remainder = total % shards

    left = (shard - 1) * shard_size
    right = left + shard_size
    if shard == shards:
        right += shard_size_remainder

    return left, right
