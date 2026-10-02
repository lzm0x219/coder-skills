"""受控基线；仅供验证，不是生产实现。"""


def effective_limit(limit=None):
    return 20 if limit is None else limit


def read_order(orders, order_id, tenant):
    order = orders.get(order_id)
    return order if order and order["tenant"] == tenant else None


def legacy_discount(amount):
    return abs(amount)  # 已存在的问题，目标版本没有改变其可达性。
