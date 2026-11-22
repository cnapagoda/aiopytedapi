"""The gateway client.

:class:`TedapiClient` sends TEDAPI requests over one :class:`Transport`:

    async with aiohttp.ClientSession() as session:
        key = RsaKey.from_pem(pem_bytes)
        client = TedapiClient.signed(session, "192.168.1.50", key, password="ABCDE")
        await client.connect()
        status = await client.get_network_status()

Every method raises a :class:`~aiopytedapi.exceptions.TedapiError` subclass on
failure; none returns None to mean "it failed". Commands that change settings
need the signed connection and log a WARNING when they're sent.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Mapping, Optional, Tuple

import aiohttp

from ._proto import tedapi_pb2 as pb
from .exceptions import (
    GatewayRejectedError,
    NotSupportedError,
    SignedConnectionRequired,
    UnexpectedResponseError,
)
from .inventory import BatteryInventory
from .keys import KeyInput, RsaKey, fingerprint, public_key_bytes, rsa_public_key_der
from .models import (
    EXPORT_LIMIT_KEY,
    IMPORT_LIMIT_KEY,
    AuthorizedClient,
    AuthorizedClients,
    CalibrationDelayStatus,
    NetworkStatus,
    Number,
    SiteLimits,
    export_limit_value,
    import_limit_value,
    validate_calibration_delay,
)
from .transport import DEFAULT_TIMEOUT, WIFI_HOST, SignedTransport, Transport, WifiTransport

_LOGGER = logging.getLogger(__name__)

#: The error code a gateway answers for a request its firmware doesn't implement.
NOT_IMPLEMENTED = 12
_FINGERPRINT_PREFIX = re.compile(r"[0-9a-fA-F]{8,64}")


class TedapiClient:
    """A TEDAPI client for one gateway, over one transport."""

    def __init__(self, transport: Transport, *, din: Optional[str] = None) -> None:
        self.transport = transport
        self._din = din

    @classmethod
    def signed(
        cls,
        session: aiohttp.ClientSession,
        host: str,
        key: RsaKey,
        *,
        password: Optional[str] = None,
        din: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> TedapiClient:
        """A client on the signed connection (``/tedapi/v1r``), on the
        gateway's home-network address or its Wi-Fi address. ``password`` is
        the customer login password, needed for the DIN unless ``din`` is
        given."""
        return cls(SignedTransport(session, host, key, password=password, timeout=timeout), din=din)

    @classmethod
    def wifi(
        cls,
        session: aiohttp.ClientSession,
        password: str,
        *,
        host: str = WIFI_HOST,
        din: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> TedapiClient:
        """A read-only client on the Gateway Wi-Fi connection (``/tedapi/v1``)
        with the gateway's Wi-Fi password."""
        return cls(WifiTransport(session, password, host=host, timeout=timeout), din=din)

    # ── Connection ───────────────────────────────────────────────────

    @property
    def din(self) -> Optional[str]:
        """The gateway's DIN, once known."""
        return self._din

    @property
    def signed_connection(self) -> bool:
        """True when this client can send commands that change settings."""
        return self.transport.signed

    async def connect(self) -> str:
        """Fetch the gateway's DIN (needed by every request) and return it."""
        self._din = await self.transport.get_din()
        return self._din

    async def _send(self, envelope: pb.MessageEnvelope) -> pb.MessageEnvelope:
        din = self._din if self._din is not None else await self.connect()
        envelope.recipient.din = din
        return await self.transport.send(envelope, din)

    @staticmethod
    def _read_envelope() -> pb.MessageEnvelope:
        """A read request: delivered over local HTTPS from the installer. The
        gateway answers it on both transports."""
        envelope = pb.MessageEnvelope()
        envelope.deliveryChannel = pb.DELIVERY_CHANNEL_LOCAL_HTTPS
        envelope.sender.local = pb.LOCAL_PARTICIPANT_INSTALLER
        return envelope

    @staticmethod
    def _command_envelope() -> pb.MessageEnvelope:
        """A signed command: delivered as a Hermes command from the customer
        app client the signing key is registered as."""
        envelope = pb.MessageEnvelope()
        envelope.deliveryChannel = pb.DELIVERY_CHANNEL_HERMES_COMMAND
        envelope.sender.authorizedClient = pb.AUTHORIZED_CLIENT_TYPE_CUSTOMER_MOBILE_APP
        return envelope

    def _require_signed(self, what: str) -> None:
        if not self.transport.signed:
            raise SignedConnectionRequired(f"{what} needs the signed connection")

    @staticmethod
    def _check_error(envelope: pb.MessageEnvelope, what: str) -> None:
        """Raise for a ``common.error_response`` answer."""
        if envelope.WhichOneof("payload") == "common" and envelope.common.WhichOneof("message") == "error_response":
            status = envelope.common.error_response.status
            if status.code == NOT_IMPLEMENTED:
                raise NotSupportedError(status.code, f"{what} is not supported by this gateway's firmware")
            raise GatewayRejectedError(status.code, status.message)

    @classmethod
    def _reply(cls, envelope: pb.MessageEnvelope, payload: str, field: str, what: str) -> Any:
        """The ``<payload>.<field>`` answer message, or raise."""
        cls._check_error(envelope, what)
        if envelope.WhichOneof("payload") == payload:
            group = getattr(envelope, payload)
            if group.WhichOneof("message") == field:
                return getattr(group, field)
        raise UnexpectedResponseError(f"{what}: the gateway's answer was not {field}")

    # ── Configuration (config.json) ──────────────────────────────────

    async def _read_config(self) -> Tuple[Dict[str, Any], bytes]:
        """config.json and its hash (the write's optimistic lock)."""
        envelope = self._command_envelope() if self.transport.signed else self._read_envelope()
        request = envelope.filestore.readFileRequest
        request.domain = pb.FILE_STORE_API_DOMAIN_CONFIG_JSON
        request.name = "config.json"
        reply = self._reply(await self._send(envelope), "filestore", "readFileResponse", "config read")
        try:
            config = json.loads(reply.file.blob.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as err:
            raise UnexpectedResponseError("config.json could not be decoded") from err
        if not isinstance(config, dict):
            raise UnexpectedResponseError("config.json is not an object")
        return config, bytes(reply.hash)

    async def get_config(self) -> Dict[str, Any]:
        """The gateway's configuration (config.json). Read-only. It holds the
        site's settings and identifiers: don't log or publish it."""
        config, _ = await self._read_config()
        return config

    async def _update_config(self, updates: Dict[str, Any], what: str) -> Dict[str, Any]:
        """Read-modify-write config.json over the signed connection. The
        write carries the hash of the config that was read, so the gateway
        refuses it if the config changed in between. ``updates`` maps dotted
        paths (``site_info.max_site_meter_power_ac``) to values."""
        self._require_signed(what)
        config, config_hash = await self._read_config()
        for path, value in updates.items():
            *parents, leaf = path.split(".")
            node = config
            for key in parents:
                child = node.get(key)
                if not isinstance(child, dict):
                    child = node[key] = {}
                node = child
            node[leaf] = value
        envelope = self._command_envelope()
        request = envelope.filestore.updateFileRequest
        request.domain = pb.FILE_STORE_API_DOMAIN_CONFIG_JSON
        request.file.name = "config.json"
        request.file.blob = json.dumps(config).encode("utf-8")
        request.hash = config_hash
        answer = await self._send(envelope)
        self._check_error(answer, what)
        if answer.WhichOneof("payload") != "filestore" or answer.filestore.WhichOneof("message") not in (
            None,
            "updateFileResponse",
        ):
            raise UnexpectedResponseError(f"{what}: the gateway did not acknowledge the config write")
        return config

    # ── Battery inventory ────────────────────────────────────────────

    async def get_battery_inventory(self, components: Optional[Mapping[str, Any]] = None) -> BatteryInventory:
        """The site's Powerwalls and expansion packs, from config.json, with
        each one's slot in ``components``: component readings (ComponentsQuery
        payloads) keyed by the DIN of the Powerwall they came from. Without
        readings every unit is listed with ``slot`` None. Read-only; both
        connections. See :class:`~aiopytedapi.inventory.BatteryInventory`."""
        config = await self.get_config()
        din = self._din if self._din is not None else await self.connect()
        return BatteryInventory.from_payloads(config, gateway_din=din, components=components)

    # ── Network status ───────────────────────────────────────────────

    async def get_network_status(self) -> NetworkStatus:
        """Each network interface's state (Wi-Fi, Ethernet, cellular):
        enabled, active route, link / internet / Tesla connectivity and
        signal strength. Read-only.

        A Powerwall 3 answers on both connections. A Powerwall 2 answers only
        on the Gateway Wi-Fi connection: over the signed connection it raises
        MessageFaultError (``MESSAGEFAULT_ERROR_TIMEOUT``)."""
        envelope = self._read_envelope()
        envelope.common.get_networking_status_request.SetInParent()
        reply = self._reply(await self._send(envelope), "common", "get_networking_status_response", "network status")
        return NetworkStatus.from_proto(reply)

    # ── Site import / export limits ──────────────────────────────────

    async def get_site_limits(self) -> SiteLimits:
        """The site's import and export limits (kW). Read-only."""
        return SiteLimits.from_config(await self.get_config())

    async def set_import_limit(self, kilowatts: Optional[Number]) -> SiteLimits:
        """Set the most power the site may import from the grid (kW); None
        removes the limit. Signed connection only.

        An installer may have set this limit to meet the grid connection
        agreement: don't raise or remove it unless you're allowed to."""
        value = import_limit_value(kilowatts)
        self._require_signed("setting the import limit")
        _LOGGER.warning("Setting the site import limit to %s kW", "none" if kilowatts is None else kilowatts)
        config = await self._update_config({f"site_info.{IMPORT_LIMIT_KEY}": value}, "setting the import limit")
        return SiteLimits.from_config(config)

    async def set_export_limit(self, kilowatts: Optional[Number]) -> SiteLimits:
        """Set the most power the site may export to the grid (kW); None
        removes the limit. Signed connection only.

        An installer may have set this limit to meet the grid connection
        agreement (a network export limit): don't raise or remove it unless
        you're allowed to."""
        value = export_limit_value(kilowatts)
        self._require_signed("setting the export limit")
        _LOGGER.warning("Setting the site export limit to %s kW", "none" if kilowatts is None else kilowatts)
        config = await self._update_config({f"site_info.{EXPORT_LIMIT_KEY}": value}, "setting the export limit")
        return SiteLimits.from_config(config)

    # ── Battery calibration delay ────────────────────────────────────

    async def get_battery_calibration_delay_status(self) -> CalibrationDelayStatus:
        """How many calibration delays are left, and the time left on the
        current one. Read-only; signed connection only.

        A Powerwall 3 on firmware 26.34.3 raises NotSupportedError."""
        self._require_signed("the calibration delay status")
        envelope = self._command_envelope()
        envelope.teg.get_delay_battery_calibration_status_request.SetInParent()
        reply = self._reply(
            await self._send(envelope),
            "teg",
            "get_delay_battery_calibration_status_response",
            "the calibration delay status",
        )
        return CalibrationDelayStatus.from_proto(reply)

    async def delay_battery_calibration(self, delay_hours: int) -> None:
        """Postpone the gateway's next battery calibration by ``delay_hours``.
        The gateway allows a limited number of delays, and each accepted
        request may use one. Signed connection only.

        A calibration can't be started locally: this only postpones one. An
        acknowledgement is not proof the calibration moved."""
        validate_calibration_delay(delay_hours)
        self._require_signed("delaying the battery calibration")
        envelope = self._command_envelope()
        envelope.teg.delay_battery_calibration_request.delay_hours = delay_hours
        _LOGGER.warning("Delaying the battery calibration by %d h", delay_hours)
        self._reply(
            await self._send(envelope), "teg", "delay_battery_calibration_response", "delaying the battery calibration"
        )

    # ── Authorized clients (registered keys) ─────────────────────────

    async def get_authorized_clients(self) -> AuthorizedClients:
        """The keys that may send the gateway signed commands (the Tesla app,
        vehicles, clients like this one) and each key's state. Read-only;
        both connections."""
        envelope = self._read_envelope()
        envelope.authorization.list_authorized_clients_request.SetInParent()
        reply = self._reply(
            await self._send(envelope),
            "authorization",
            "list_authorized_clients_response",
            "the authorized clients list",
        )
        return AuthorizedClients.from_proto(reply)

    @property
    def current_key(self) -> Optional[bytes]:
        """PKCS#1 DER of the key this client signs with (signed connection)."""
        return self.transport.public_key_der

    async def add_authorized_client(
        self, public_key: KeyInput | RsaKey, description: str = "aiopytedapi"
    ) -> AuthorizedClient:
        """Add an RSA public key as a customer app client. Signed connection
        only (the signing key must be VERIFIED).

        The new key starts in PENDING_VERIFICATION and times out unless it's
        verified within about 10 minutes. A key added this way is not vouched
        for by the signing key, and keys added locally have not been seen to
        verify: registering a key that verifies still needs Tesla's cloud."""
        key_der = rsa_public_key_der(public_key)
        self._require_signed("adding a key")
        envelope = self._command_envelope()
        request = envelope.authorization.add_authorized_client_request
        request.type = pb.AUTHORIZED_CLIENT_TYPE_CUSTOMER_MOBILE_APP
        request.key_type = pb.AUTHORIZED_KEY_TYPE_RSA
        request.public_key = key_der
        request.description = description
        reply = self._reply(
            await self._send(envelope), "authorization", "add_authorized_client_response", "adding a key"
        )
        client = AuthorizedClient.from_proto(reply.client)
        _LOGGER.warning("Added key %s (%s)", client.fingerprint[:16], client.state)
        return client

    async def remove_authorized_client(self, public_key: KeyInput | RsaKey, *, allow_current_key: bool = False) -> None:
        """Remove a client's key. It can no longer send signed commands, and
        re-adding it needs registration and verification again. Signed
        connection only.

        ``public_key`` is the key as listed (DER bytes or the base64
        string), a PEM key, an RsaKey, or a fingerprint prefix of 8 or more
        hex characters that matches exactly one client. Removing the key this
        client signs with would lock it out, so it's refused unless
        ``allow_current_key``."""
        self._require_signed("removing a key")
        key = await self._resolve_key(public_key)
        if key == self.current_key and not allow_current_key:
            raise ValueError("refusing to remove the key this client signs with (pass allow_current_key=True)")
        envelope = self._command_envelope()
        envelope.authorization.remove_authorized_client_request.public_key = key
        self._reply(await self._send(envelope), "authorization", "remove_authorized_client_response", "removing a key")
        _LOGGER.warning("Removed key %s", fingerprint(key)[:16])

    async def _resolve_key(self, public_key: KeyInput | RsaKey) -> bytes:
        if isinstance(public_key, str) and _FINGERPRINT_PREFIX.fullmatch(public_key.strip()):
            matches = (await self.get_authorized_clients()).find(public_key)
            if len(matches) != 1:
                raise ValueError(f"the fingerprint prefix matches {len(matches)} clients (need exactly 1)")
            return matches[0].public_key
        return public_key_bytes(public_key)


__all__ = ["NOT_IMPLEMENTED", "TedapiClient"]
