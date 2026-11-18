"""RSA keys: the signing key a client uses, and public keys as the gateway
lists them.

Keys are DER encoded on the wire; RSA public keys are PKCS#1, the encoding the
gateway registers and lists back. A key's fingerprint is the SHA-256 of that
DER, the same fingerprint pypowerwall prints for a key.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
from typing import Union

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes

KeyInput = Union[bytes, bytearray, str]


def fingerprint(public_key_der: bytes) -> str:
    """SHA-256 hex fingerprint of DER public key bytes."""
    return hashlib.sha256(bytes(public_key_der)).hexdigest()


class RsaKey:
    """The RSA private key a signed connection signs its requests with.

    Load it with :meth:`from_pem` (reading the file is the caller's job, so
    no blocking I/O happens inside the event loop). The key itself is never
    logged or returned; ``repr`` shows only its fingerprint.
    """

    def __init__(self, private_key: rsa.RSAPrivateKey) -> None:
        self._private_key = private_key
        self.public_key_der: bytes = private_key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.PKCS1
        )
        self.fingerprint: str = fingerprint(self.public_key_der)

    @classmethod
    def from_pem(cls, pem: bytes, password: bytes | None = None) -> RsaKey:
        """Load a PEM private key. Raises ValueError if it is not an RSA key."""
        try:
            key = serialization.load_pem_private_key(pem, password=password)
        except (TypeError, ValueError) as err:
            raise ValueError("the key could not be read as a PEM private key") from err
        if not isinstance(key, rsa.RSAPrivateKey):
            raise ValueError("the signed connection needs an RSA key")
        return cls(key)

    @classmethod
    def generate(cls, key_size: int = 4096) -> RsaKey:
        """A new key pair (RSA-4096, as the gateway expects). CPU heavy: run it
        in an executor from async code."""
        return cls(rsa.generate_private_key(public_exponent=65537, key_size=key_size))

    def private_pem(self) -> bytes:
        """The private key as unencrypted PKCS#8 PEM, to store it. Write it
        with owner-only permissions."""
        return self._private_key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        )

    def sign(self, data: bytes) -> bytes:
        """RSA PKCS#1 v1.5 signature with SHA-512, as the gateway verifies."""
        return self._private_key.sign(data, padding.PKCS1v15(), hashes.SHA512())

    def __repr__(self) -> str:
        return f"RsaKey(fingerprint={self.fingerprint[:16]}...)"


def _as_bytes(key: KeyInput) -> bytes:
    if isinstance(key, (bytes, bytearray)):
        return bytes(key)
    if isinstance(key, str):
        try:
            return key.strip().encode("ascii")
        except UnicodeEncodeError as err:
            raise ValueError("public key is not PEM, DER or base64") from err
    raise ValueError("public key must be bytes or str")


def _is_pem(data: bytes) -> bool:
    return data.lstrip().startswith(b"-----BEGIN ")


def _b64decode(data: bytes) -> bytes:
    try:
        return base64.b64decode(data, validate=True)
    except (binascii.Error, ValueError) as err:
        raise ValueError("public key is not PEM, DER or base64") from err


def _load_public_key(data: bytes) -> PublicKeyTypes:
    if _is_pem(data):
        if b"PRIVATE KEY-----" in data:
            return serialization.load_pem_private_key(data, password=None).public_key()
        return serialization.load_pem_public_key(data)
    return serialization.load_der_public_key(data)


def rsa_public_key_der(key: KeyInput | RsaKey) -> bytes:
    """PKCS#1 DER of an RSA public key, the encoding the gateway registers.

    ``key`` may be an :class:`RsaKey`, a PEM public key, a PEM private key
    (only its public half is used; nothing is kept), DER bytes (PKCS#1 or
    SubjectPublicKeyInfo), or a base64 string of the DER. Raises ValueError for
    anything else, including keys that are not RSA."""
    if isinstance(key, RsaKey):
        return key.public_key_der
    data = _as_bytes(key)
    if not data:
        raise ValueError("public key is empty")
    if not _is_pem(data) and isinstance(key, str):
        data = _b64decode(data)
    try:
        public_key = _load_public_key(data)
    except (TypeError, ValueError) as err:
        raise ValueError("public key could not be read (expected an RSA key as PEM, DER or base64)") from err
    if not isinstance(public_key, rsa.RSAPublicKey):
        raise ValueError("only RSA keys can be added")
    return public_key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.PKCS1)


def public_key_bytes(key: KeyInput | RsaKey) -> bytes:
    """The key bytes that identify an existing client: DER bytes as given, a
    base64 string exactly as listed, a PEM key (an RSA key is converted to the
    PKCS#1 DER the gateway lists) or an :class:`RsaKey`. Raises ValueError for
    empty or undecodable input."""
    if isinstance(key, RsaKey):
        return key.public_key_der
    data = _as_bytes(key)
    if not data:
        raise ValueError("public key is empty")
    if _is_pem(data):
        return rsa_public_key_der(data)
    if isinstance(key, str):
        return _b64decode(data)
    return data
