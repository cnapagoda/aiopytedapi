"""Transports: how a request envelope reaches the gateway.

* :class:`SignedTransport` (``/tedapi/v1r``) wraps each envelope in a
  RoutableMessage signed with the client's registered RSA key. It works on the
  gateway's home-network address and on its Wi-Fi address (192.168.91.1), and
  is the only transport that can send commands that change settings.
* :class:`WifiTransport` (``/tedapi/v1``) uses the Gateway Wi-Fi password
  over HTTP Basic auth. It works only on the gateway's own Wi-Fi network and
  can only read.

Both take an :class:`aiohttp.ClientSession` from the caller and never close
it. Each transport sends one request at a time: the gateway copes badly with
several at once.

The gateway's HTTPS certificate is self-signed, so it is not verified. That is
only done for the gateway's address, never for another host.
"""

from __future__ import annotations

import asyncio
import base64
import gzip
import json
import logging
import math
import struct
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any

import aiohttp
from google.protobuf.message import DecodeError

from ._proto import tedapi_pb2 as pb
from .exceptions import (
    GatewayAuthError,
    GatewayBusyError,
    GatewayConnectionError,
    KeyNotAuthorizedError,
    KeyPendingVerificationError,
    MessageFaultError,
    UnexpectedResponseError,
)
from .keys import RsaKey

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10.0
WIFI_HOST = "192.168.91.1"
# How long a signature stays valid after signing (seconds).
SIGNATURE_LIFETIME = 12
_BUSY = (429, 503)
_DENIED = (401, 403)
_KEY_FAULTS = (pb.MESSAGEFAULT_ERROR_UNKNOWN_KEY_ID, pb.MESSAGEFAULT_ERROR_INACTIVE_KEY)


def decompress(content: bytes) -> bytes:
    """Gunzip a response when it is gzip compressed (firmware 25.42.2 and
    later compress some answers); anything else is returned unchanged."""
    if content[:2] == b"\x1f\x8b":
        try:
            return gzip.decompress(content)
        except (OSError, EOFError):
            return content
    return content


def signature_payload(din: str, expires_at: int, message: bytes) -> bytes:
    """The bytes the RSA signature covers: a tag-length-value header
    (signature type RSA, domain ENERGY_DEVICE, the DIN, the expiry), the end
    tag, then the signed message."""

    def tlv(tag: int, value: bytes) -> bytes:
        return bytes([tag, len(value)]) + value

    return b"".join(
        [
            tlv(pb.TAG_SIGNATURE_TYPE, bytes([pb.SIGNATURE_TYPE_RSA])),
            tlv(pb.TAG_DOMAIN, bytes([pb.DOMAIN_ENERGY_DEVICE])),
            tlv(pb.TAG_PERSONALIZATION, din.encode()),
            tlv(pb.TAG_EXPIRES_AT, struct.pack(">I", expires_at)),
            bytes([pb.TAG_END]),
            message,
        ]
    )


class Transport(ABC):
    """Sends a request :class:`MessageEnvelope` and returns the gateway's
    answer envelope."""

    #: True when the transport can send signed commands (settings changes).
    signed: bool = False

    def __init__(self, session: aiohttp.ClientSession, host: str, timeout: float) -> None:
        self._session = session
        self.host = host
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._lock = asyncio.Lock()
        self._cookies: dict[str, str] = {}

    @property
    def public_key_der(self) -> bytes | None:
        """PKCS#1 DER of the key this transport signs with, if it signs."""
        return None

    @abstractmethod
    async def get_din(self) -> str:
        """The gateway's DIN (Device Identification Number)."""

    @abstractmethod
    async def send(self, envelope: pb.MessageEnvelope, din: str) -> pb.MessageEnvelope:
        """Send ``envelope`` to the gateway ``din`` and return its answer."""

    async def _request(self, method: str, path: str, **kwargs: Any) -> tuple[int, bytes]:
        """One HTTPS request to the gateway: (status, body). Connection
        errors and timeouts become GatewayConnectionError; rate limiting
        becomes GatewayBusyError. Cookies the gateway sets are kept on the
        transport and sent back (a shared session's cookie jar ignores cookies
        from an IP address)."""
        url = f"https://{self.host}{path}"
        if self._cookies:
            headers = dict(kwargs.pop("headers", None) or {})
            headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in self._cookies.items())
            kwargs["headers"] = headers
        try:
            async with self._session.request(method, url, ssl=False, timeout=self._timeout, **kwargs) as resp:
                body = await resp.read()
                status = resp.status
                for name, morsel in resp.cookies.items():
                    self._cookies[name] = morsel.value
        except asyncio.TimeoutError as err:
            raise GatewayConnectionError(f"no answer from the gateway within {self._timeout.total} s") from err
        except aiohttp.ClientError as err:
            raise GatewayConnectionError(f"could not reach the gateway: {type(err).__name__}") from err
        if status in _BUSY:
            raise GatewayBusyError(f"the gateway is rate limiting requests (HTTP {status})")
        return status, body


class SignedTransport(Transport):
    """The signed connection: RSA-signed requests to ``/tedapi/v1r``.

    ``password`` is the customer login password, used to log in for the DIN
    and when the gateway asks for a fresh session (HTTP 401/403). Pass
    ``din`` to skip the DIN lookup.
    """

    signed = True

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        key: RsaKey,
        *,
        password: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(session, host, timeout)
        self.key = key
        self._password = password
        self._token: str | None = None

    @property
    def public_key_der(self) -> bytes:
        return self.key.public_key_der

    async def _login(self) -> None:
        """Customer login (``/api/login/Basic``) for a session token."""
        if not self._password:
            raise GatewayAuthError("the gateway asked for a login and no password was given")
        status, body = await self._request(
            "POST",
            "/api/login/Basic",
            json={
                "username": "customer",
                "password": self._password,
                "email": "customer@customer.domain",
                "clientInfo": {"timezone": "UTC"},
            },
        )
        if status in _DENIED:
            raise GatewayAuthError("the gateway refused the password")
        if status != 200:
            raise UnexpectedResponseError(f"login failed (HTTP {status})")
        try:
            token = json.loads(body).get("token")
        except (ValueError, AttributeError) as err:
            raise UnexpectedResponseError("the login answer could not be decoded") from err
        if not isinstance(token, str) or not token:
            raise UnexpectedResponseError("the login answer has no token")
        self._token = token

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"} if self._token else {}

    async def get_din(self) -> str:
        async with self._lock:
            if self._token is None and self._password:
                await self._login()
            status, body = await self._request("GET", "/tedapi/din", headers=self._auth_headers())
            if status in _DENIED and self._password:
                await self._login()
                status, body = await self._request("GET", "/tedapi/din", headers=self._auth_headers())
        if status in _DENIED:
            raise GatewayAuthError("the gateway refused the DIN request")
        if status != 200:
            raise UnexpectedResponseError(f"DIN request failed (HTTP {status})")
        try:
            din = decompress(body).decode().strip()
        except UnicodeDecodeError as err:
            raise UnexpectedResponseError("the DIN could not be decoded") from err
        if not din:
            raise UnexpectedResponseError("the gateway returned an empty DIN")
        return din

    def _signed_request(self, envelope_bytes: bytes, din: str) -> bytes:
        """The RoutableMessage for ``envelope_bytes``: a fresh uuid and a
        signature that expires SIGNATURE_LIFETIME seconds from now."""
        routable = pb.RoutableMessage()
        routable.to_destination.domain = pb.DOMAIN_ENERGY_DEVICE
        routable.protobuf_message_as_bytes = envelope_bytes
        routable.uuid = str(uuid.uuid4()).encode()
        expires_at = math.ceil(time.time()) + SIGNATURE_LIFETIME
        signature = self.key.sign(signature_payload(din, expires_at, envelope_bytes))
        routable.signature_data.signer_identity.public_key = self.key.public_key_der
        routable.signature_data.rsa_data.expires_at = expires_at
        routable.signature_data.rsa_data.signature = signature
        return routable.SerializeToString()

    async def _post(self, envelope_bytes: bytes, din: str) -> tuple[int, bytes]:
        return await self._request(
            "POST",
            "/tedapi/v1r",
            data=self._signed_request(envelope_bytes, din),
            headers={"Content-Type": "application/octet-stream"},
        )

    async def send(self, envelope: pb.MessageEnvelope, din: str) -> pb.MessageEnvelope:
        envelope_bytes = envelope.SerializeToString()
        async with self._lock:
            status, body = await self._post(envelope_bytes, din)
            if status in _DENIED and self._password:
                # The session expired: log in again and re-sign (the first
                # signature may have expired meanwhile).
                await self._login()
                status, body = await self._post(envelope_bytes, din)
        if status in _DENIED:
            raise GatewayAuthError(f"the gateway refused the signed request (HTTP {status})")
        if status != 200:
            raise UnexpectedResponseError(f"signed request failed (HTTP {status})")
        return self._parse(body)

    def _parse(self, body: bytes) -> pb.MessageEnvelope:
        routable = pb.RoutableMessage()
        try:
            routable.ParseFromString(body)
        except DecodeError as err:
            raise UnexpectedResponseError("the signed answer could not be decoded") from err
        fault = routable.signed_message_status.message_fault
        if fault in _KEY_FAULTS:
            raise KeyNotAuthorizedError(
                f"the gateway does not accept this key ({pb.MessageFault_E.Name(fault)})", self.key.fingerprint
            )
        if fault != pb.MESSAGEFAULT_ERROR_NONE:
            try:
                name = pb.MessageFault_E.Name(fault)
            except ValueError:
                name = f"UNKNOWN ({fault})"
            raise MessageFaultError(name)
        inner = routable.protobuf_message_as_bytes
        if b"authorization not verified" in body.lower():
            raise KeyPendingVerificationError(
                "the key is registered but not verified yet: toggle the Powerwall's On/Off switch", self.key.fingerprint
            )
        if not inner:
            raise KeyNotAuthorizedError("the gateway answered with no data (key not accepted?)", self.key.fingerprint)
        envelope = pb.MessageEnvelope()
        try:
            envelope.ParseFromString(inner)
        except DecodeError as err:
            raise UnexpectedResponseError("the gateway's answer could not be decoded") from err
        return envelope


class WifiTransport(Transport):
    """The Gateway Wi-Fi connection: ``/tedapi/v1`` with the Wi-Fi password
    (HTTP Basic auth), reachable only on the gateway's own Wi-Fi network.
    Read-only: it can't send signed commands."""

    def __init__(
        self, session: aiohttp.ClientSession, password: str, *, host: str = WIFI_HOST, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        super().__init__(session, host, timeout)
        if not password:
            raise ValueError("the Wi-Fi connection needs the gateway Wi-Fi password")
        credentials = base64.b64encode(f"Tesla_Energy_Device:{password}".encode()).decode()
        self._auth_header = {"Authorization": f"Basic {credentials}"}

    async def get_din(self) -> str:
        async with self._lock:
            status, body = await self._request("GET", "/tedapi/din", headers=dict(self._auth_header))
        if status in _DENIED:
            raise GatewayAuthError("the gateway refused the Wi-Fi password")
        if status != 200:
            raise UnexpectedResponseError(f"DIN request failed (HTTP {status})")
        try:
            din = decompress(body).decode().strip()
        except UnicodeDecodeError as err:
            raise UnexpectedResponseError("the DIN could not be decoded") from err
        if not din:
            raise UnexpectedResponseError("the gateway returned an empty DIN")
        return din

    async def send(self, envelope: pb.MessageEnvelope, din: str) -> pb.MessageEnvelope:
        message = pb.Message()
        message.message.CopyFrom(envelope)
        message.tail.value = 1
        async with self._lock:
            status, body = await self._request(
                "POST",
                "/tedapi/v1",
                data=message.SerializeToString(),
                headers={"Content-Type": "application/octet-stream", **self._auth_header},
            )
        if status in _DENIED:
            raise GatewayAuthError("the gateway refused the Wi-Fi password")
        if status != 200:
            raise UnexpectedResponseError(f"request failed (HTTP {status})")
        answer = pb.Message()
        try:
            answer.ParseFromString(decompress(body))
        except DecodeError as err:
            raise UnexpectedResponseError("the gateway's answer could not be decoded") from err
        if not answer.HasField("message"):
            raise UnexpectedResponseError("the gateway's answer has no message")
        return answer.message


__all__ = [
    "DEFAULT_TIMEOUT",
    "WIFI_HOST",
    "SignedTransport",
    "Transport",
    "WifiTransport",
    "decompress",
    "signature_payload",
]
