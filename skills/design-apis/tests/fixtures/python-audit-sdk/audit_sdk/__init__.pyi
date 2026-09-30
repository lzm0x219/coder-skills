"""虚构审计服务的候选公开类型；仅用于设计期静态检查。"""

from datetime import datetime
from types import TracebackType
from typing import Literal, final

AuditErrorCode = Literal[
    "invalid_input",
    "unauthorized",
    "rate_limited",
    "transport_failure",
]


class AuditError(Exception):
    code: AuditErrorCode
    operation: Literal["open", "list_page"]
    retry_after_seconds: float | None


@final
class Event:
    id: str
    kind: str
    created_at: datetime


@final
class EventPage:
    items: tuple[Event, ...]
    next_cursor: str | None


@final
class AuditClient:
    def __init__(
        self,
        *,
        endpoint: str,
        token: str,
        timeout_seconds: float = 10.0,
    ) -> None: ...

    def __enter__(self) -> AuditClient: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]: ...

    def list_page(
        self,
        *,
        page_size: int = 50,
        cursor: str | None = None,
    ) -> EventPage: ...

    def close(self) -> None: ...
