"""Shared fixtures. No test reaches a real gateway: transports are tested
against a fake aiohttp session, the client against a fake transport."""

from __future__ import annotations

from collections.abc import AsyncIterator

import aiohttp
import pytest

from aiopytedapi import RsaKey
from aiopytedapi._proto import tedapi_pb2 as pb
from aiopytedapi.transport import Transport

from .fakes import FakeSession

DIN = "TEST_DIN"
HOST = "192.0.2.10"  # TEST-NET-1: never a real gateway


@pytest.fixture(scope="session")
def key() -> RsaKey:
    # 2048 bits keeps the suite fast; the gateway uses 4096.
    return RsaKey.generate(2048)


@pytest.fixture
async def session() -> AsyncIterator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession() as client_session:
        yield client_session


@pytest.fixture
def mock_http() -> FakeSession:
    return FakeSession()


class FakeTransport(Transport):
    """Records each request envelope and answers from a queue."""

    def __init__(self, *answers: pb.MessageEnvelope, signed: bool = True, public_key_der: bytes | None = None) -> None:
        self.signed = signed
        self.sent: list[pb.MessageEnvelope] = []
        self.answers = list(answers)
        self.din_requests = 0
        self._public_key_der = public_key_der

    @property
    def public_key_der(self) -> bytes | None:
        return self._public_key_der

    async def get_din(self) -> str:
        self.din_requests += 1
        return DIN

    async def send(self, envelope: pb.MessageEnvelope, din: str) -> pb.MessageEnvelope:
        assert din == DIN
        copy = pb.MessageEnvelope()
        copy.CopyFrom(envelope)
        self.sent.append(copy)
        return self.answers.pop(0)


def error_answer(code: int, message: str = "") -> pb.MessageEnvelope:
    answer = pb.MessageEnvelope()
    answer.common.error_response.status.code = code
    answer.common.error_response.status.message = message
    return answer
