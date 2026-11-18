"""The signed and Gateway Wi-Fi transports against a mocked gateway."""

from __future__ import annotations

import asyncio
import gzip
import struct

import aiohttp
import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from aiopytedapi import (
    GatewayAuthError,
    GatewayBusyError,
    GatewayConnectionError,
    KeyNotAuthorizedError,
    KeyPendingVerificationError,
    MessageFaultError,
    RsaKey,
    SignedTransport,
    UnexpectedResponseError,
    WifiTransport,
)
from aiopytedapi._proto import tedapi_pb2 as pb
from aiopytedapi.transport import decompress, signature_payload

from .conftest import DIN, HOST
from .fakes import Answer, FakeSession

V1R = f"https://{HOST}/tedapi/v1r"
DIN_URL = f"https://{HOST}/tedapi/din"
LOGIN = f"https://{HOST}/api/login/Basic"
WIFI = "https://192.168.91.1/tedapi/v1"
WIFI_DIN = "https://192.168.91.1/tedapi/din"


def request_envelope() -> pb.MessageEnvelope:
    envelope = pb.MessageEnvelope()
    envelope.deliveryChannel = pb.DELIVERY_CHANNEL_LOCAL_HTTPS
    envelope.recipient.din = DIN
    envelope.common.get_networking_status_request.SetInParent()
    return envelope


def answer_envelope() -> pb.MessageEnvelope:
    envelope = pb.MessageEnvelope()
    envelope.common.get_networking_status_response.wifi.enabled = True
    return envelope


def routable(inner: bytes = b"", fault: int = pb.MESSAGEFAULT_ERROR_NONE) -> bytes:
    message = pb.RoutableMessage()
    message.protobuf_message_as_bytes = inner
    message.signed_message_status.message_fault = fault
    return message.SerializeToString()


def sent_body(mock_http: FakeSession, method: str, url: str, index: int = 0) -> bytes:
    return mock_http.sent(method, url, index)["data"]


# ── Signing ─────────────────────────────────────────────────────────


def test_signature_payload_layout() -> None:
    payload = signature_payload("DIN1", 0x01020304, b"MSG")
    assert payload == (
        b"\x00\x01\x07"
        + b"\x01\x01\x07"
        + b"\x02\x04DIN1"
        + b"\x04\x04"
        + struct.pack(">I", 0x01020304)
        + b"\xff"
        + b"MSG"
    )


async def test_signed_request_verifies(session, mock_http, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(V1R, body=routable(answer_envelope().SerializeToString()))
    transport = SignedTransport(mock_http, HOST, key)
    answer = await transport.send(request_envelope(), DIN)
    assert answer.common.get_networking_status_response.wifi.enabled

    message = pb.RoutableMessage()
    message.ParseFromString(sent_body(mock_http, "POST", V1R))
    assert message.to_destination.domain == pb.DOMAIN_ENERGY_DEVICE
    assert message.protobuf_message_as_bytes == request_envelope().SerializeToString()
    assert message.signature_data.signer_identity.public_key == key.public_key_der
    assert len(message.uuid) == 36
    rsa = message.signature_data.rsa_data
    public_key = load_pem_private_key(key.private_pem(), password=None).public_key()
    public_key.verify(
        rsa.signature,  # type: ignore[union-attr,call-arg]
        signature_payload(DIN, rsa.expires_at, message.protobuf_message_as_bytes),
        padding.PKCS1v15(),
        hashes.SHA512(),
    )  # type: ignore[arg-type]


# ── Signed transport: answers ───────────────────────────────────────


@pytest.mark.parametrize("fault", [pb.MESSAGEFAULT_ERROR_UNKNOWN_KEY_ID, pb.MESSAGEFAULT_ERROR_INACTIVE_KEY])
async def test_key_faults(session, mock_http, key: RsaKey, fault: int) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(V1R, body=routable(fault=fault))
    with pytest.raises(KeyNotAuthorizedError) as err:
        await SignedTransport(mock_http, HOST, key).send(request_envelope(), DIN)
    assert err.value.fingerprint == key.fingerprint


async def test_timeout_fault(session, mock_http, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(V1R, body=routable(fault=pb.MESSAGEFAULT_ERROR_TIMEOUT))
    with pytest.raises(MessageFaultError) as err:
        await SignedTransport(mock_http, HOST, key).send(request_envelope(), DIN)
    assert err.value.fault == "MESSAGEFAULT_ERROR_TIMEOUT"


async def test_unknown_fault_number(session, mock_http, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(V1R, body=routable(fault=99))
    with pytest.raises(MessageFaultError, match=r"UNKNOWN \(99\)"):
        await SignedTransport(mock_http, HOST, key).send(request_envelope(), DIN)


async def test_pending_verification(session, mock_http, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(V1R, body=routable(b"v1r: client authorization not verified"))
    with pytest.raises(KeyPendingVerificationError):
        await SignedTransport(mock_http, HOST, key).send(request_envelope(), DIN)


async def test_empty_answer(session, mock_http, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(V1R, body=routable())
    with pytest.raises(KeyNotAuthorizedError, match="no data"):
        await SignedTransport(mock_http, HOST, key).send(request_envelope(), DIN)


@pytest.mark.parametrize("body", [b"\xff\xff\xff", routable(b"\xff\xff\xff")])
async def test_undecodable(session, mock_http, key: RsaKey, body: bytes) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(V1R, body=body)
    with pytest.raises(UnexpectedResponseError):
        await SignedTransport(mock_http, HOST, key).send(request_envelope(), DIN)


@pytest.mark.parametrize(
    ("status", "error"),
    [(429, GatewayBusyError), (503, GatewayBusyError), (500, UnexpectedResponseError), (403, GatewayAuthError)],
)
async def test_http_status(session, mock_http, key: RsaKey, status: int, error: type) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(V1R, status=status)
    with pytest.raises(error):
        await SignedTransport(mock_http, HOST, key).send(request_envelope(), DIN)


async def test_relogin_and_resign(session, mock_http, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(V1R, status=401)
    mock_http.post(LOGIN, payload={"token": "T1"}, cookies={"AuthCookie": "C1"})
    mock_http.post(V1R, body=routable(answer_envelope().SerializeToString()))
    transport = SignedTransport(mock_http, HOST, key, password="ABCDE")
    await transport.send(request_envelope(), DIN)
    login = mock_http.sent("POST", LOGIN, 0)["json"]
    assert login["username"] == "customer" and login["password"] == "ABCDE"
    second = mock_http.sent("POST", V1R, 1)
    assert second["headers"]["Cookie"] == "AuthCookie=C1"
    assert "Authorization" not in second["headers"]


async def test_connection_error(session, mock_http, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(V1R, exception=aiohttp.ClientConnectionError())
    with pytest.raises(GatewayConnectionError, match="ClientConnectionError"):
        await SignedTransport(mock_http, HOST, key).send(request_envelope(), DIN)


async def test_timeout(session, mock_http, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(V1R, exception=asyncio.TimeoutError())
    with pytest.raises(GatewayConnectionError, match=r"within 10\.0 s"):
        await SignedTransport(mock_http, HOST, key).send(request_envelope(), DIN)


# ── Signed transport: login and DIN ─────────────────────────────────


async def test_din_with_login(session, mock_http, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(LOGIN, payload={"token": "T1"})
    mock_http.get(DIN_URL, body=gzip.compress(b"1232100-00-E--TG000000000000\n"))
    transport = SignedTransport(mock_http, HOST, key, password="ABCDE")
    assert await transport.get_din() == "1232100-00-E--TG000000000000"
    headers = mock_http.sent("GET", DIN_URL, 0)["headers"]
    assert headers["Authorization"] == "Bearer T1"


async def test_din_relogin_on_expired_token(session, mock_http, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(LOGIN, payload={"token": "T1"})
    mock_http.get(DIN_URL, status=401)
    mock_http.post(LOGIN, payload={"token": "T2"})
    mock_http.get(DIN_URL, body=b"DIN2")
    transport = SignedTransport(mock_http, HOST, key, password="ABCDE")
    assert await transport.get_din() == "DIN2"


async def test_din_without_password(session, mock_http, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    mock_http.get(DIN_URL, status=403)
    with pytest.raises(GatewayAuthError):
        await SignedTransport(mock_http, HOST, key).get_din()


@pytest.mark.parametrize(
    ("status", "body", "error"),
    [
        (500, b"", UnexpectedResponseError),
        (200, b"", UnexpectedResponseError),
        (200, b"\xff\xfe", UnexpectedResponseError),
    ],
)
async def test_din_failures(session, mock_http, key: RsaKey, status: int, body: bytes, error: type) -> None:  # type: ignore[no-untyped-def]
    mock_http.get(DIN_URL, status=status, body=body)
    with pytest.raises(error):
        await SignedTransport(mock_http, HOST, key).get_din()


@pytest.mark.parametrize(
    ("status", "kwargs", "error"),
    [
        (401, {}, GatewayAuthError),
        (500, {}, UnexpectedResponseError),
        (200, {"body": b"not json"}, UnexpectedResponseError),
        (200, {"payload": {"token": ""}}, UnexpectedResponseError),
        (200, {"payload": ["x"]}, UnexpectedResponseError),
    ],
)
async def test_login_failures(session, mock_http, key: RsaKey, status: int, kwargs: dict, error: type) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(LOGIN, status=status, **kwargs)
    with pytest.raises(error):
        await SignedTransport(mock_http, HOST, key, password="ABCDE").get_din()


# ── Gateway Wi-Fi transport ─────────────────────────────────────────


def wifi_answer(envelope: pb.MessageEnvelope) -> bytes:
    message = pb.Message()
    message.message.CopyFrom(envelope)
    message.tail.value = 1
    return message.SerializeToString()


async def test_wifi_send(session, mock_http) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(WIFI, body=gzip.compress(wifi_answer(answer_envelope())))
    transport = WifiTransport(mock_http, "PASSWORD")
    answer = await transport.send(request_envelope(), DIN)
    assert answer.common.get_networking_status_response.wifi.enabled
    call = mock_http.sent("POST", WIFI, 0)
    assert call["headers"]["Authorization"] == "Basic VGVzbGFfRW5lcmd5X0RldmljZTpQQVNTV09SRA=="
    sent = pb.Message()
    sent.ParseFromString(call["data"])
    assert sent.message == request_envelope()
    assert sent.tail.value == 1
    assert not transport.signed and transport.public_key_der is None


@pytest.mark.parametrize(
    ("status", "body", "error"),
    [
        (401, b"", GatewayAuthError),
        (500, b"", UnexpectedResponseError),
        (200, b"\xff\xff", UnexpectedResponseError),
        (200, b"", UnexpectedResponseError),
    ],
)
async def test_wifi_send_failures(session, mock_http, status: int, body: bytes, error: type) -> None:  # type: ignore[no-untyped-def]
    mock_http.post(WIFI, status=status, body=body)
    with pytest.raises(error):
        await WifiTransport(mock_http, "PASSWORD").send(request_envelope(), DIN)


async def test_wifi_din(session, mock_http) -> None:  # type: ignore[no-untyped-def]
    mock_http.get(WIFI_DIN, body=b"DIN-W\n")
    assert await WifiTransport(mock_http, "PASSWORD").get_din() == "DIN-W"


@pytest.mark.parametrize(
    ("status", "body", "error"),
    [
        (403, b"", GatewayAuthError),
        (500, b"", UnexpectedResponseError),
        (200, b"  ", UnexpectedResponseError),
        (200, b"\xff\xfe", UnexpectedResponseError),
    ],
)
async def test_wifi_din_failures(session, mock_http, status: int, body: bytes, error: type) -> None:  # type: ignore[no-untyped-def]
    mock_http.get(WIFI_DIN, status=status, body=body)
    with pytest.raises(error):
        await WifiTransport(mock_http, "PASSWORD").get_din()


def test_wifi_needs_password(mock_http: FakeSession) -> None:
    with pytest.raises(ValueError, match="password"):
        WifiTransport(mock_http, "")  # type: ignore[arg-type]


async def test_login_needs_password(mock_http: FakeSession, key: RsaKey) -> None:
    with pytest.raises(GatewayAuthError, match="no password"):
        await SignedTransport(mock_http, HOST, key)._login()  # type: ignore[arg-type]


# ── Helpers ─────────────────────────────────────────────────────────


def test_decompress() -> None:
    assert decompress(gzip.compress(b"abc")) == b"abc"
    assert decompress(b"abc") == b"abc"
    assert decompress(b"\x1f\x8bbroken") == b"\x1f\x8bbroken"


async def test_requests_are_serialised(session, mock_http, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    active = 0
    peak = 0

    async def slow() -> Answer:
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.01)
        active -= 1
        return Answer(body=routable(answer_envelope().SerializeToString()))

    mock_http.post(V1R, callback=slow, repeat=True)
    transport = SignedTransport(mock_http, HOST, key)
    await asyncio.gather(*(transport.send(request_envelope(), DIN) for _ in range(3)))
    assert peak == 1
