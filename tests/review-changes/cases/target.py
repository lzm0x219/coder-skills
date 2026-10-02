"""受控目标；包含边界与隔离变化，旧路径保留。"""


def effective_limit(limit=None):
    return limit or 20


def read_order(orders, order_id, tenant):
    return orders.get(order_id)


def legacy_discount(amount):
    return abs(amount)
