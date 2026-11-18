"""Exceptions raised by aiopytedapi.

Every error the library raises derives from :class:`TedapiError`, so a caller
can catch that one class. The subclasses say what went wrong closely enough
for an application to react: retry later, ask the user for a password, or ask
them to register the key again.
"""

from __future__ import annotations


class TedapiError(Exception):
    """Base class for every aiopytedapi error."""


class GatewayConnectionError(TedapiError):
    """The gateway could not be reached, or did not answer in time."""


class GatewayBusyError(TedapiError):
    """The gateway is rate limiting requests (HTTP 429 or 503). Wait before
    sending more: retrying at once makes it worse."""


class GatewayAuthError(TedapiError):
    """The gateway refused the password (HTTP 401 or 403 after a login)."""


class KeyNotAuthorizedError(TedapiError):
    """The gateway does not accept the signing key: it is not registered, was
    removed, or does not match the registered key.

    ``fingerprint`` is the SHA-256 fingerprint of the key that was used, to
    compare against the gateway's list of authorized clients."""

    def __init__(self, message: str, fingerprint: str) -> None:
        super().__init__(message)
        self.fingerprint = fingerprint


class KeyPendingVerificationError(KeyNotAuthorizedError):
    """The signing key is registered but not verified yet. Toggle the
    Powerwall's On/Off switch within about 10 minutes of registering it."""


class MessageFaultError(TedapiError):
    """The gateway answered a signed request with a message fault, for
    example ``MESSAGEFAULT_ERROR_TIMEOUT`` (a Powerwall 2 answers some
    requests only over the Gateway Wi-Fi)."""

    def __init__(self, fault: str) -> None:
        super().__init__(f"gateway message fault: {fault}")
        self.fault = fault


class GatewayRejectedError(TedapiError):
    """The gateway answered with an error status instead of a result."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"gateway returned error {code}: {message}" if message else f"gateway returned error {code}")
        self.code = code
        self.message = message


class NotSupportedError(GatewayRejectedError):
    """The gateway firmware does not implement the request (error code 12)."""


class SignedConnectionRequired(TedapiError):
    """The command needs the signed (RSA key) connection; the Wi-Fi password
    connection can't send it."""


class UnexpectedResponseError(TedapiError):
    """The gateway's answer could not be decoded, or was not the answer to the
    request that was sent."""
