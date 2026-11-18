"""What the gateway reports, as plain frozen dataclasses.

Each model is built from the gateway's protobuf answer (``from_proto``) and
renders a JSON-safe dict (``to_dict``). Values that identify a home or a
person (Wi-Fi SSID, MAC and IP addresses, key descriptions) are kept out of
``repr`` so they don't end up in debug logs, and ``to_dict`` only includes
them with ``details=True``. The gateway's Wi-Fi password is never parsed: the
schema doesn't model that field.
"""

from __future__ import annotations

import base64
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from ipaddress import IPv4Address
from typing import Any, Dict, List, Optional, Tuple, Union

from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper

from ._proto import tedapi_pb2 as pb
from .keys import fingerprint

Number = Union[int, float]


def enum_name(enum_type: EnumTypeWrapper, value: int, prefix: str = "") -> str:
    """The name of a protobuf enum value without ``prefix``, or
    ``"UNKNOWN (<value>)"`` for a value this schema doesn't define, so newer
    firmware can't break the output."""
    try:
        name = enum_type.Name(value)
    except ValueError:
        return f"UNKNOWN ({value})"
    return name[len(prefix) :] if prefix and name.startswith(prefix) else name


# ── Network status ───────────────────────────────────────────────────

#: Interface keys in the order the gateway reports them.
INTERFACES = ("wifi", "eth", "gsm")


def format_ipv4(value: int) -> Optional[str]:
    """Dotted quad for a fixed32 IPv4 value (first octet in the most
    significant byte), or None when unset (0)."""
    return str(IPv4Address(value)) if value else None


def format_mac(value: bytes) -> Optional[str]:
    """``aa:bb:cc:dd:ee:ff`` for MAC address bytes, or None when there is
    none (the cellular interface has no MAC)."""
    return ":".join(f"{octet:02x}" for octet in value) if value else None


@dataclass(frozen=True)
class IPv4Settings:
    """An interface's IPv4 settings."""

    dhcp_enabled: bool
    address: Optional[str]
    subnet_mask: Optional[str]
    gateway: Optional[str]
    dns: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dhcp_enabled": self.dhcp_enabled,
            "address": self.address,
            "subnet_mask": self.subnet_mask,
            "gateway": self.gateway,
            "dns": list(self.dns),
        }


@dataclass(frozen=True)
class NetworkInterfaceStatus:
    """Status of one gateway network interface.

    ``signal_strength_percent``, ``rssi`` and ``snr`` are None when the
    gateway doesn't report them (a Powerwall 3 on firmware 26.34.3 reports
    only the percentage)."""

    enabled: bool = False
    active_route: bool = False  # carries the default route
    connected_physical: bool = False  # link / association is up
    connected_internet: bool = False
    connected_tesla: bool = False  # can reach Tesla's servers
    signal_strength_percent: Optional[int] = None
    rssi: Optional[int] = None  # dBm
    snr: Optional[int] = None  # dB
    device_state: str = "NETWORK_DEVICE_STATE_INVALID"
    device_state_reason: str = "NETWORK_DEVICE_STATE_REASON_INVALID"
    mac_address: Optional[str] = field(default=None, repr=False)
    ipv4: Optional[IPv4Settings] = field(default=None, repr=False)

    @classmethod
    def from_proto(cls, interface: pb.NetworkInterface) -> NetworkInterfaceStatus:
        status = interface.connectivity_status
        rssi = status.rssi
        ipv4 = None
        if interface.HasField("ipv4_config"):
            config = interface.ipv4_config
            ipv4 = IPv4Settings(
                dhcp_enabled=config.dhcp_enabled,
                address=format_ipv4(config.address),
                subnet_mask=format_ipv4(config.subnet_mask),
                gateway=format_ipv4(config.gateway),
                dns=tuple(str(IPv4Address(dns)) for dns in config.dns if dns),
            )
        return cls(
            enabled=interface.enabled,
            active_route=interface.active_route,
            connected_physical=status.connected_physical,
            connected_internet=status.connected_internet,
            connected_tesla=status.connected_tesla,
            # A wrapper type: presence is explicit, so a real 0 % is kept.
            signal_strength_percent=(
                rssi.signal_strength_percent.value if rssi.HasField("signal_strength_percent") else None
            ),
            # A plain sint32 can't tell unset from 0, and 0 dBm is not a
            # reading a radio reports: 0 means "not reported".
            rssi=rssi.value or None,
            snr=status.snr.value if status.HasField("snr") else None,
            device_state=enum_name(pb.NetworkDeviceState, interface.device_state),
            device_state_reason=enum_name(pb.NetworkDeviceStateReason, interface.device_state_reason),
            mac_address=format_mac(interface.mac_address),
            ipv4=ipv4,
        )

    def to_dict(self, details: bool = False) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "enabled": self.enabled,
            "active_route": self.active_route,
            "connected_physical": self.connected_physical,
            "connected_internet": self.connected_internet,
            "connected_tesla": self.connected_tesla,
            "signal_strength_percent": self.signal_strength_percent,
            "rssi": self.rssi,
            "snr": self.snr,
            "device_state": self.device_state,
            "device_state_reason": self.device_state_reason,
        }
        if details:
            data["mac_address"] = self.mac_address
            data["ipv4"] = self.ipv4.to_dict() if self.ipv4 else None
        return data


@dataclass(frozen=True)
class NetworkStatus:
    """The gateway's networking status: one entry per interface (None when
    the gateway left it out), and the configured Wi-Fi network's SSID and
    security type (never its password)."""

    wifi: Optional[NetworkInterfaceStatus] = None
    eth: Optional[NetworkInterfaceStatus] = None
    gsm: Optional[NetworkInterfaceStatus] = None
    wifi_ssid: Optional[str] = field(default=None, repr=False)
    wifi_security_type: Optional[str] = None

    @classmethod
    def from_proto(cls, response: pb.CommonAPIGetNetworkingStatusResponse) -> NetworkStatus:
        has_config = response.HasField("wifi_config")
        return cls(
            wifi=NetworkInterfaceStatus.from_proto(response.wifi) if response.HasField("wifi") else None,
            eth=NetworkInterfaceStatus.from_proto(response.eth) if response.HasField("eth") else None,
            gsm=NetworkInterfaceStatus.from_proto(response.gsm) if response.HasField("gsm") else None,
            wifi_ssid=(response.wifi_config.ssid or None) if has_config else None,
            wifi_security_type=(
                enum_name(pb.WifiNetworkSecurityType, response.wifi_config.security_type) if has_config else None
            ),
        )

    @property
    def interfaces(self) -> List[str]:
        """Names of the interfaces the gateway reported."""
        return [name for name in INTERFACES if getattr(self, name) is not None]

    @property
    def active(self) -> Optional[str]:
        """The interface carrying the default route, if any."""
        for name in INTERFACES:
            interface: Optional[NetworkInterfaceStatus] = getattr(self, name)
            if interface is not None and interface.active_route:
                return name
        return None

    def to_dict(self, details: bool = False) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for name in INTERFACES:
            interface: Optional[NetworkInterfaceStatus] = getattr(self, name)
            data[name] = None if interface is None else interface.to_dict(details=details)
        if details:
            data["wifi_config"] = (
                None
                if self.wifi_security_type is None
                else {"ssid": self.wifi_ssid, "security_type": self.wifi_security_type}
            )
        return data


# ── Battery calibration delay ────────────────────────────────────────

MAX_UINT32 = 2**32 - 1


def validate_calibration_delay(delay_hours: int) -> None:
    """Reject an invalid delay before any I/O. ``delay_hours`` is a uint32 on
    the wire; the gateway's own limit is not documented."""
    if type(delay_hours) is not int or not 1 <= delay_hours <= MAX_UINT32:
        raise ValueError("delay_hours must be a positive integer")


@dataclass(frozen=True)
class CalibrationDelayStatus:
    """The gateway's battery calibration delay counters, as reported."""

    calibration_delays_left: int = 0
    calibration_delay_remaining_seconds: int = 0
    max_calibration_delays: int = 0

    @classmethod
    def from_proto(cls, response: pb.TEGAPIGetDelayBatteryCalibrationStatusResponse) -> CalibrationDelayStatus:
        return cls(
            calibration_delays_left=response.calibration_delays_left,
            calibration_delay_remaining_seconds=response.calibration_delay_remaining_seconds,
            max_calibration_delays=response.max_calibration_delays,
        )

    def to_dict(self) -> Dict[str, int]:
        return {
            "calibration_delays_left": self.calibration_delays_left,
            "calibration_delay_remaining_seconds": self.calibration_delay_remaining_seconds,
            "max_calibration_delays": self.max_calibration_delays,
        }


# ── Site import / export limits ──────────────────────────────────────

IMPORT_LIMIT_KEY = "max_site_meter_power_ac"
EXPORT_LIMIT_KEY = "min_site_meter_power_ac"
#: The magnitude the gateway stores when the site has no limit (kW).
UNLIMITED_KW = 1000000000


def validate_site_limit(kilowatts: Optional[Number]) -> None:
    """Reject an invalid limit before any I/O: a number of kilowatts from 0
    up to (not including) the gateway's "no limit" value, or None for no
    limit. NaN and infinity fail the range check."""
    if kilowatts is None:
        return
    if isinstance(kilowatts, bool) or not isinstance(kilowatts, (int, float)) or not 0 <= kilowatts < UNLIMITED_KW:
        raise ValueError("limit must be None or a number of kilowatts, 0 or more")


def _normalize(kilowatts: Number) -> Number:
    """Whole numbers as int, the way the gateway stores them; never -0.0."""
    return int(kilowatts) if float(kilowatts).is_integer() else float(kilowatts)


def import_limit_value(kilowatts: Optional[Number]) -> Number:
    """The stored ``max_site_meter_power_ac`` for an import limit (None: no limit)."""
    validate_site_limit(kilowatts)
    return UNLIMITED_KW if kilowatts is None else _normalize(kilowatts)


def export_limit_value(kilowatts: Optional[Number]) -> Number:
    """The stored ``min_site_meter_power_ac`` for an export limit (None: no
    limit). The gateway stores it as a negative site meter power."""
    validate_site_limit(kilowatts)
    return -UNLIMITED_KW if kilowatts is None else -_normalize(kilowatts)


def _limit(value: Any, sign: int) -> Optional[Number]:
    """A stored site meter power as a limit in kW: None when absent, not a
    number, or at the "no limit" value. A value on the wrong side of zero
    leaves no room in that direction, so it reads as 0."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or math.isnan(value):
        return None
    limit = sign * value
    if limit >= UNLIMITED_KW:
        return None
    return _normalize(max(0, limit))


@dataclass(frozen=True)
class SiteLimits:
    """The site import and export limits in kW, both positive. None means the
    gateway reports no limit.

    An installer may have set these to meet the site's grid connection
    agreement (for example a network export limit)."""

    import_limit_kw: Optional[Number] = None
    export_limit_kw: Optional[Number] = None

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> SiteLimits:
        site_info = config.get("site_info") if isinstance(config, dict) else None
        if not isinstance(site_info, dict):
            site_info = {}
        return cls(
            import_limit_kw=_limit(site_info.get(IMPORT_LIMIT_KEY), 1),
            export_limit_kw=_limit(site_info.get(EXPORT_LIMIT_KEY), -1),
        )

    def to_dict(self) -> Dict[str, Optional[Number]]:
        return {"import_limit_kw": self.import_limit_kw, "export_limit_kw": self.export_limit_kw}


# ── Authorized clients (registered keys) ─────────────────────────────


def _timestamp(value: Any) -> Optional[datetime]:
    if not value.seconds and not value.nanos:
        return None
    return datetime.fromtimestamp(value.seconds + value.nanos / 1e9, tz=timezone.utc)


@dataclass(frozen=True)
class AuthorizedClient:
    """One authorized client: a public key that may send signed commands.

    ``state`` is ``VERIFIED``, ``PENDING_VERIFICATION``,
    ``PENDING_VERIFICATION_TIMEOUT``, and so on. The description (often a
    person's or device's name), identifier and key are kept out of ``repr``."""

    fingerprint: str
    type: str
    key_type: str
    roles: Tuple[str, ...]
    state: str
    verification: str
    added_time: Optional[datetime]
    authorized_by: Optional[str]  # fingerprint of the key that vouched for it
    public_key: bytes = field(repr=False)
    description: str = field(default="", repr=False)
    identifier: str = field(default="", repr=False)

    @classmethod
    def from_proto(cls, record: pb.AuthorizationRecord) -> AuthorizedClient:
        return cls(
            fingerprint=fingerprint(record.public_key),
            type=enum_name(pb.AuthorizedClientType, record.type, "AUTHORIZED_CLIENT_TYPE_"),
            key_type=enum_name(pb.AuthorizedKeyType, record.key_type, "AUTHORIZED_KEY_TYPE_"),
            roles=tuple(enum_name(pb.AuthorizationRole, role, "AUTHORIZATION_ROLE_") for role in record.roles),
            state=enum_name(pb.AuthorizedState, record.state, "AUTHORIZED_STATE_"),
            verification=enum_name(pb.AuthorizedVerificationType, record.verification, "AUTHORIZED_VERIFICATION_TYPE_"),
            added_time=_timestamp(record.added_time) if record.HasField("added_time") else None,
            authorized_by=fingerprint(record.authorized_by_public_key) if record.authorized_by_public_key else None,
            public_key=bytes(record.public_key),
            description=record.description,
            identifier=record.identifier,
        )

    def to_dict(self, details: bool = False, current_key: Optional[bytes] = None) -> Dict[str, Any]:
        """JSON-safe dict. ``current_key`` (the key this connection signs
        with) sets ``current_key``; ``details`` adds the description,
        identifier and base64 public key."""
        data: Dict[str, Any] = {
            "fingerprint": self.fingerprint,
            "type": self.type,
            "key_type": self.key_type,
            "roles": list(self.roles),
            "state": self.state,
            "verification": self.verification,
            "added_time": self.added_time.isoformat() if self.added_time else None,
            "authorized_by": self.authorized_by,
            "current_key": None if current_key is None else self.public_key == current_key,
        }
        if details:
            data["description"] = self.description or None
            data["identifier"] = self.identifier or None
            data["public_key"] = base64.b64encode(self.public_key).decode("ascii") if self.public_key else None
        return data


@dataclass(frozen=True)
class AuthorizedClients:
    """Every authorized client, in the gateway's order, and its
    ``enable_line_switch_off`` flag (meaning not documented)."""

    clients: Tuple[AuthorizedClient, ...] = ()
    enable_line_switch_off: bool = False

    @classmethod
    def from_proto(cls, response: pb.AuthorizationAPIListAuthorizedClientsResponse) -> AuthorizedClients:
        return cls(
            clients=tuple(AuthorizedClient.from_proto(r) for r in response.clients),
            enable_line_switch_off=response.enable_line_switch_off,
        )

    def find(self, prefix: str) -> List[AuthorizedClient]:
        """Clients whose fingerprint starts with ``prefix`` (case-insensitive)."""
        prefix = prefix.strip().lower()
        return [client for client in self.clients if client.fingerprint.startswith(prefix)]

    def to_dict(self, details: bool = False, current_key: Optional[bytes] = None) -> Dict[str, Any]:
        return {
            "clients": [client.to_dict(details=details, current_key=current_key) for client in self.clients],
            "enable_line_switch_off": self.enable_line_switch_off,
        }
