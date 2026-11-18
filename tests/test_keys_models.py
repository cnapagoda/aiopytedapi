"""Key helpers and the data models."""

from __future__ import annotations

import base64
import math

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from aiopytedapi import (
    AuthorizedClients,
    NetworkStatus,
    RsaKey,
    SiteLimits,
    fingerprint,
    public_key_bytes,
    rsa_public_key_der,
)
from aiopytedapi._proto import tedapi_pb2 as pb
from aiopytedapi.models import (
    CalibrationDelayStatus,
    enum_name,
    export_limit_value,
    format_ipv4,
    format_mac,
    import_limit_value,
    validate_site_limit,
)

# ── Keys ────────────────────────────────────────────────────────────


def test_rsa_key_roundtrip(key: RsaKey) -> None:
    again = RsaKey.from_pem(key.private_pem())
    assert again.public_key_der == key.public_key_der
    assert again.fingerprint == fingerprint(key.public_key_der)
    assert key.fingerprint[:16] in repr(key)
    assert "PRIVATE" not in repr(key)


def test_rsa_key_rejects_bad_input() -> None:
    with pytest.raises(ValueError, match="PEM private key"):
        RsaKey.from_pem(b"nonsense")
    ec_pem = ec.generate_private_key(ec.SECP256R1()).private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    with pytest.raises(ValueError, match="RSA"):
        RsaKey.from_pem(ec_pem)


def test_rsa_public_key_der_forms(key: RsaKey) -> None:
    private = serialization.load_pem_private_key(key.private_pem(), password=None)
    public = private.public_key()
    spki_der = public.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    public_pem = public.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    expected = key.public_key_der
    assert rsa_public_key_der(key) == expected
    assert rsa_public_key_der(key.private_pem()) == expected
    assert rsa_public_key_der(public_pem) == expected
    assert rsa_public_key_der(public_pem.decode()) == expected
    assert rsa_public_key_der(spki_der) == expected
    assert rsa_public_key_der(expected) == expected
    assert rsa_public_key_der(base64.b64encode(expected).decode()) == expected


@pytest.mark.parametrize("value", [b"", "", "not base64!", b"\x00\x01", "é", 42])
def test_rsa_public_key_der_rejects(value: object) -> None:
    with pytest.raises(ValueError, match="key"):
        rsa_public_key_der(value)  # type: ignore[arg-type]


def test_rsa_public_key_der_rejects_ec() -> None:
    ec_pem = (
        ec.generate_private_key(ec.SECP256R1())
        .public_key()
        .public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    )
    with pytest.raises(ValueError, match="only RSA"):
        rsa_public_key_der(ec_pem)


def test_public_key_bytes(key: RsaKey) -> None:
    der = key.public_key_der
    assert public_key_bytes(key) == der
    assert public_key_bytes(der) == der
    assert public_key_bytes(base64.b64encode(der).decode()) == der
    assert public_key_bytes(key.private_pem()) == der
    assert public_key_bytes(b"\x01\x02") == b"\x01\x02"
    with pytest.raises(ValueError, match="empty"):
        public_key_bytes(b"")
    with pytest.raises(ValueError, match="base64"):
        public_key_bytes("!!")


# ── Network status ──────────────────────────────────────────────────


def network_response() -> pb.CommonAPIGetNetworkingStatusResponse:
    response = pb.CommonAPIGetNetworkingStatusResponse()
    response.wifi_config.ssid = "HomeNet"
    response.wifi.enabled = True
    response.wifi.mac_address = bytes.fromhex("a1b2c3d4e5f6")
    response.wifi.connectivity_status.rssi.value = -61
    response.wifi.connectivity_status.snr.value = 0
    response.wifi.ipv4_config.dhcp_enabled = True
    response.wifi.ipv4_config.address = 0xC0A80102
    response.wifi.device_state = 99
    response.gsm.enabled = False
    return response


def test_network_status_details_and_privacy() -> None:
    status = NetworkStatus.from_proto(network_response())
    assert status.interfaces == ["wifi", "gsm"]
    assert status.active is None
    assert status.wifi is not None
    assert status.wifi.rssi == -61 and status.wifi.snr == 0
    assert status.wifi.signal_strength_percent is None
    assert status.wifi.device_state == "UNKNOWN (99)"
    plain = status.to_dict()
    assert "mac_address" not in plain["wifi"] and "wifi_config" not in plain
    assert plain["eth"] is None
    full = status.to_dict(details=True)
    assert full["wifi"]["mac_address"] == "a1:b2:c3:d4:e5:f6"
    assert full["wifi"]["ipv4"]["address"] == "192.168.1.2"
    assert full["gsm"]["ipv4"] is None
    assert full["wifi_config"] == {"ssid": "HomeNet", "security_type": "WIFI_NETWORK_SECURITY_TYPE_INVALID"}
    text = repr(status)
    assert "HomeNet" not in text and "a1:b2" not in text and "192.168" not in text


def test_network_status_without_wifi_config() -> None:
    status = NetworkStatus.from_proto(pb.CommonAPIGetNetworkingStatusResponse())
    assert status.to_dict(details=True)["wifi_config"] is None
    assert status.interfaces == []


def test_formatters() -> None:
    assert format_ipv4(0) is None
    assert format_ipv4(0x0A000001) == "10.0.0.1"
    assert format_mac(b"") is None
    assert enum_name(pb.AuthorizedState, 3, "AUTHORIZED_STATE_") == "VERIFIED"
    assert enum_name(pb.AuthorizedState, 3) == "AUTHORIZED_STATE_VERIFIED"


# ── Site limits ─────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("site_info", "expected"),
    [
        ({}, (None, None)),
        ({"max_site_meter_power_ac": 1000000000, "min_site_meter_power_ac": -1000000000}, (None, None)),
        ({"max_site_meter_power_ac": 5, "min_site_meter_power_ac": -2.5}, (5, 2.5)),
        ({"max_site_meter_power_ac": -3, "min_site_meter_power_ac": 4}, (0, 0)),
        ({"max_site_meter_power_ac": True, "min_site_meter_power_ac": "x"}, (None, None)),
        ({"max_site_meter_power_ac": math.nan}, (None, None)),
        ({"max_site_meter_power_ac": 5.0}, (5, None)),
    ],
)
def test_site_limits_from_config(site_info: dict, expected: tuple) -> None:
    limits = SiteLimits.from_config({"site_info": site_info})
    assert (limits.import_limit_kw, limits.export_limit_kw) == expected
    assert limits.to_dict() == {"import_limit_kw": expected[0], "export_limit_kw": expected[1]}


def test_site_limits_from_odd_config() -> None:
    assert SiteLimits.from_config({"site_info": None}) == SiteLimits()
    assert SiteLimits.from_config([]) == SiteLimits()  # type: ignore[arg-type]


def test_limit_values() -> None:
    assert import_limit_value(None) == 1000000000
    assert export_limit_value(None) == -1000000000
    assert import_limit_value(5.0) == 5 and isinstance(import_limit_value(5.0), int)
    assert export_limit_value(2.5) == -2.5
    assert export_limit_value(0) == 0 and str(export_limit_value(0.0)) == "0"


@pytest.mark.parametrize("value", [-1, 1000000000, math.inf, math.nan, True, "5"])
def test_validate_site_limit_rejects(value: object) -> None:
    with pytest.raises(ValueError, match="kilowatts"):
        validate_site_limit(value)  # type: ignore[arg-type]


# ── Calibration delay and authorized clients ────────────────────────


def test_calibration_status_defaults() -> None:
    assert CalibrationDelayStatus().to_dict() == {
        "calibration_delays_left": 0,
        "calibration_delay_remaining_seconds": 0,
        "max_calibration_delays": 0,
    }


def test_authorized_clients_model(key: RsaKey) -> None:
    response = pb.AuthorizationAPIListAuthorizedClientsResponse()
    record = response.clients.add()
    record.public_key = key.public_key_der
    record.type = pb.AUTHORIZED_CLIENT_TYPE_VEHICLE
    record.key_type = pb.AUTHORIZED_KEY_TYPE_ECC
    record.roles.extend([pb.AUTHORIZATION_ROLE_CUSTOMER, 9])
    record.state = pb.AUTHORIZED_STATE_PENDING_VERIFICATION_TIMEOUT
    record.verification = pb.AUTHORIZED_VERIFICATION_TYPE_SIGNED
    record.added_time.seconds = 1700000000
    record.authorized_by_public_key = b"\x01"
    record.description = "Alice's phone"
    record.identifier = "ID-1"
    bare = response.clients.add()
    bare.added_time.SetInParent()

    clients = AuthorizedClients.from_proto(response)
    first = clients.clients[0]
    assert first.type == "VEHICLE" and first.key_type == "ECC"
    assert first.roles == ("CUSTOMER", "UNKNOWN (9)")
    assert first.state == "PENDING_VERIFICATION_TIMEOUT"
    assert first.authorized_by == fingerprint(b"\x01")
    assert clients.clients[1].added_time is None and clients.clients[1].authorized_by is None
    assert "Alice" not in repr(first) and "ID-1" not in repr(first)

    plain = clients.to_dict(current_key=key.public_key_der)
    assert plain["clients"][0]["current_key"] is True
    assert plain["clients"][1]["current_key"] is False
    assert plain["clients"][0]["added_time"] == "2023-11-14T22:13:20+00:00"
    assert "description" not in plain["clients"][0]
    full = clients.to_dict(details=True)
    assert full["clients"][0]["current_key"] is None
    assert full["clients"][0]["description"] == "Alice's phone"
    assert full["clients"][0]["public_key"] == base64.b64encode(key.public_key_der).decode()
    assert full["clients"][1]["public_key"] is None and full["clients"][1]["description"] is None
    assert clients.find(key.fingerprint[:10].upper()) == [first]
