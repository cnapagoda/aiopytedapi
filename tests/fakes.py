"""A stand-in for aiohttp.ClientSession: the transports only call
``session.request()``. Tests queue answers per (method, url) and read back
what was sent."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from http.cookies import SimpleCookie
from types import TracebackType
from typing import Any, Awaitable, Callable, Optional


@dataclass
class Call:
    kwargs: dict[str, Any]


@dataclass
class Answer:
    status: int = 200
    body: bytes = b""
    cookies: dict[str, str] = field(default_factory=dict)
    exception: Optional[BaseException] = None
    callback: Optional[Callable[[], Awaitable[Answer]]] = None
    repeat: bool = False


class FakeResponse:
    def __init__(self, answer: Answer) -> None:
        self.status = answer.status
        self._body = answer.body
        self.cookies: SimpleCookie = SimpleCookie()
        for name, value in answer.cookies.items():
            self.cookies[name] = value

    async def read(self) -> bytes:
        return self._body


class _RequestContext:
    def __init__(self, answer: Answer) -> None:
        self._answer = answer

    async def __aenter__(self) -> FakeResponse:
        answer = self._answer
        if answer.callback is not None:
            answer = await answer.callback()
        if answer.exception is not None:
            raise answer.exception
        return FakeResponse(answer)

    async def __aexit__(
        self, exc_type: Optional[type[BaseException]], exc: Optional[BaseException], tb: Optional[TracebackType]
    ) -> None:
        return None


class FakeSession:
    def __init__(self) -> None:
        self._answers: dict[tuple[str, str], list[Answer]] = defaultdict(list)
        self.requests: dict[tuple[str, str], list[Call]] = defaultdict(list)

    def add(
        self,
        method: str,
        url: str,
        *,
        status: int = 200,
        body: bytes = b"",
        payload: Any = None,
        cookies: Optional[dict[str, str]] = None,
        exception: Optional[BaseException] = None,
        callback: Optional[Callable[[], Awaitable[Answer]]] = None,
        repeat: bool = False,
    ) -> None:
        if payload is not None:
            body = json.dumps(payload).encode()
        self._answers[(method, url)].append(Answer(status, body, cookies or {}, exception, callback, repeat))

    def post(self, url: str, **kwargs: Any) -> None:
        self.add("POST", url, **kwargs)

    def get(self, url: str, **kwargs: Any) -> None:
        self.add("GET", url, **kwargs)

    def request(self, method: str, url: str, **kwargs: Any) -> _RequestContext:
        self.requests[(method, url)].append(Call(kwargs))
        queue = self._answers[(method, url)]
        if not queue:
            raise AssertionError(f"unexpected request: {method} {url}")
        answer = queue[0] if queue[0].repeat else queue.pop(0)
        return _RequestContext(answer)

    def sent(self, method: str, url: str, index: int = 0) -> dict[str, Any]:
        return self.requests[(method, url)][index].kwargs
