"""aiopytedapi: an async client for the Tesla Powerwall gateway's local TEDAPI.

Talks to the gateway over the signed connection (an RSA key registered with
the gateway) or the Gateway Wi-Fi connection (the Wi-Fi password). Uses an
aiohttp session the caller provides.
"""

from __future__ import annotations

from .client import NOT_IMPLEMENTED, TedapiClient
from .exceptions import (
    GatewayAuthError,
    GatewayBusyError,
    GatewayConnectionError,
    GatewayRejectedError,
    KeyNotAuthorizedError,
    KeyPendingVerificationError,
    MessageFaultError,
    NotSupportedError,
    SignedConnectionRequired,
    TedapiError,
    UnexpectedResponseError,
)
from .keys import RsaKey, fingerprint, public_key_bytes, rsa_public_key_der
from .models import (
    AuthorizedClient,
    AuthorizedClients,
    CalibrationDelayStatus,
    IPv4Settings,
    NetworkInterfaceStatus,
    NetworkStatus,
    SiteLimits,
)
from .transport import WIFI_HOST, SignedTransport, Transport, WifiTransport

try:
    from ._version import __version__
except ImportError:  # pragma: no cover - only in an unbuilt checkout
    __version__ = "0.0.0"

__all__ = [
    "NOT_IMPLEMENTED",
    "WIFI_HOST",
    "AuthorizedClient",
    "AuthorizedClients",
    "CalibrationDelayStatus",
    "GatewayAuthError",
    "GatewayBusyError",
    "GatewayConnectionError",
    "GatewayRejectedError",
    "IPv4Settings",
    "KeyNotAuthorizedError",
    "KeyPendingVerificationError",
    "MessageFaultError",
    "NetworkInterfaceStatus",
    "NetworkStatus",
    "NotSupportedError",
    "RsaKey",
    "SignedConnectionRequired",
    "SignedTransport",
    "SiteLimits",
    "TedapiClient",
    "TedapiError",
    "Transport",
    "UnexpectedResponseError",
    "WifiTransport",
    "__version__",
    "fingerprint",
    "public_key_bytes",
    "rsa_public_key_der",
]
