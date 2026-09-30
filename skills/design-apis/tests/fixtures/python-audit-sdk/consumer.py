"""从拟议包入口导入的设计期调用点；不运行真实服务。"""

from collections.abc import Callable

from audit_sdk import AuditClient, AuditError, Event


def fetch_two_pages(
    endpoint: str,
    token: str,
    on_rate_limited: Callable[[float | None], None],
) -> tuple[Event, ...]:
    try:
        with AuditClient(endpoint=endpoint, token=token) as client:
            first = client.list_page(page_size=25)
            if first.next_cursor is None:
                return first.items
            second = client.list_page(page_size=25, cursor=first.next_cursor)
            return first.items + second.items
    except AuditError as error:
        if error.code == "rate_limited":
            on_rate_limited(error.retry_after_seconds)
        raise
