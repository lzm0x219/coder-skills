"""可达性反证：内部真假值变化不能改变外部合法零值行为。"""


def list_items(items, limit=None):
    if limit is not None and limit <= 0:
        return []
    return _slice(items, limit)


def _slice(items, limit):
    return items[: limit or 20]
