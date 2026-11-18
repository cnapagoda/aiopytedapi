"""TedapiClient against a fake transport: the request envelopes it builds
(pinned to the bytes pypowerwall sends, where pypowerwall pins them) and how
it reads the answers."""

from __future__ import annotations

import json
import logging

import pytest

from aiopytedapi import (
    GatewayRejectedError,
    NotSupportedError,
    RsaKey,
    SignedConnectionRequired,
    TedapiClient,
    UnexpectedResponseError,
)
from aiopytedapi._proto import tedapi_pb2 as pb

from .conftest import DIN, FakeTransport, error_answer

# The envelope prefix of a signed command to TEST_DIN: deliveryChannel
# HERMES_COMMAND, sender authorizedClient 1, recipient din TEST_DIN.
COMMAND_PREFIX = "0802120220011a0a0a08544553545f44494e"
# A read request: deliveryChannel LOCAL_HTTPS, sender local INSTALLER.
READ_PREFIX = "0801120218011a0a0a08544553545f44494e"


def answer_with(build) -> pb.MessageEnvelope:  # type: ignore[no-untyped-def]
    envelope = pb.MessageEnvelope()
    build(envelope)
    return envelope


def config_answer(config: dict, config_hash: bytes = b"HASH1") -> pb.MessageEnvelope:
    def build(envelope: pb.MessageEnvelope) -> None:
        envelope.filestore.readFileResponse.file.name = "config.json"
        envelope.filestore.readFileResponse.file.blob = json.dumps(config).encode()
        envelope.filestore.readFileResponse.hash = config_hash

    return answer_with(build)


def update_ack() -> pb.MessageEnvelope:
    return answer_with(lambda e: e.filestore.updateFileResponse.SetInParent())


# ── Connection ──────────────────────────────────────────────────────


async def test_connect_fetches_din_once() -> None:
    transport = FakeTransport(answer_with(lambda e: e.common.get_networking_status_response.SetInParent()))
    client = TedapiClient(transport)
    assert client.din is None
    await client.get_network_status()
    assert client.din == DIN
    assert transport.din_requests == 1


async def test_given_din_skips_lookup() -> None:
    transport = FakeTransport(answer_with(lambda e: e.common.get_networking_status_response.SetInParent()))
    client = TedapiClient(transport, din=DIN)
    await client.get_network_status()
    assert transport.din_requests == 0


def test_factories(session, key: RsaKey) -> None:  # type: ignore[no-untyped-def]
    signed = TedapiClient.signed(session, "192.0.2.10", key, password="ABCDE", din=DIN)
    assert signed.signed_connection and signed.din == DIN
    assert signed.current_key == key.public_key_der
    wifi = TedapiClient.wifi(session, "PASSWORD")
    assert not wifi.signed_connection and wifi.current_key is None
    assert wifi.transport.host == "192.168.91.1"


# ── Network status ──────────────────────────────────────────────────


async def test_network_status_request_and_answer() -> None:
    def build(envelope: pb.MessageEnvelope) -> None:
        response = envelope.common.get_networking_status_response
        response.wifi_config.ssid = "HomeNet"
        response.wifi_config.security_type = pb.WIFI_NETWORK_SECURITY_TYPE_WPA2_PERSONAL
        response.wifi.enabled = True
        response.wifi.active_route = True
        response.wifi.mac_address = bytes.fromhex("a1b2c3d4e5f6")
        response.wifi.connectivity_status.connected_internet = True
        response.wifi.connectivity_status.rssi.signal_strength_percent.value = 58
        response.wifi.device_state = pb.NETWORK_DEVICE_STATE_READY
        response.eth.enabled = True
        response.eth.ipv4_config.address = 0xC0A80102
        response.eth.ipv4_config.dns.extend([0x08080808, 0])

    transport = FakeTransport(answer_with(build), signed=False)
    status = await TedapiClient(transport).get_network_status()

    assert transport.sent[0].SerializeToString().hex() == READ_PREFIX + "2203b20100"
    assert status.interfaces == ["wifi", "eth"]
    assert status.active == "wifi"
    assert status.wifi is not None and status.wifi.signal_strength_percent == 58
    assert status.wifi.device_state == "NETWORK_DEVICE_STATE_READY"
    assert status.eth is not None and status.eth.ipv4 is not None
    assert status.eth.ipv4.address == "192.168.1.2"
    assert status.eth.ipv4.dns == ("8.8.8.8",)
    assert status.wifi_security_type == "WIFI_NETWORK_SECURITY_TYPE_WPA2_PERSONAL"


async def test_network_status_not_supported() -> None:
    transport = FakeTransport(error_answer(12, "not implemented"))
    with pytest.raises(NotSupportedError) as err:
        await TedapiClient(transport).get_network_status()
    assert err.value.code == 12


async def test_other_error_code() -> None:
    transport = FakeTransport(error_answer(3, "denied"))
    with pytest.raises(GatewayRejectedError) as err:
        await TedapiClient(transport).get_network_status()
    assert not isinstance(err.value, NotSupportedError)
    assert err.value.message == "denied"
    assert "denied" in str(err.value)


async def test_unexpected_answer() -> None:
    transport = FakeTransport(answer_with(lambda e: e.teg.dispatch_battery_power_response.SetInParent()))
    with pytest.raises(UnexpectedResponseError):
        await TedapiClient(transport).get_network_status()


# ── Configuration and site limits ───────────────────────────────────


async def test_config_read_signed_uses_command_envelope() -> None:
    transport = FakeTransport(config_answer({"site_info": {}}))
    assert await TedapiClient(transport).get_config() == {"site_info": {}}
    request = transport.sent[0]
    assert request.SerializeToString().hex().startswith(COMMAND_PREFIX)
    assert request.filestore.readFileRequest.domain == pb.FILE_STORE_API_DOMAIN_CONFIG_JSON
    assert request.filestore.readFileRequest.name == "config.json"


async def test_config_read_wifi_matches_legacy_config_send() -> None:
    # Over Gateway Wi-Fi the request must be wire-identical to the legacy
    # config.send fetch pypowerwall sends (num 1, file "config.json").
    transport = FakeTransport(config_answer({"a": 1}), signed=False)
    await TedapiClient(transport).get_config()
    assert transport.sent[0].SerializeToString().hex() == (READ_PREFIX + "7a110a0f0801120b636f6e6669672e6a736f6e")


@pytest.mark.parametrize("blob", [b"\xff", b"not json", b"[1, 2]"])
async def test_config_undecodable(blob: bytes) -> None:
    answer = config_answer({})
    answer.filestore.readFileResponse.file.blob = blob
    with pytest.raises(UnexpectedResponseError):
        await TedapiClient(FakeTransport(answer)).get_config()


async def test_site_limits_read() -> None:
    config = {"site_info": {"max_site_meter_power_ac": 1000000000, "min_site_meter_power_ac": -5}}
    limits = await TedapiClient(FakeTransport(config_answer(config), signed=False)).get_site_limits()
    assert limits.import_limit_kw is None
    assert limits.export_limit_kw == 5


async def test_set_export_limit_writes_with_hash(caplog: pytest.LogCaptureFixture) -> None:
    config = {"site_info": {"max_site_meter_power_ac": 1000000000, "other": 1}, "vin": "X"}
    transport = FakeTransport(config_answer(config, b"H"), update_ack())
    with caplog.at_level(logging.WARNING):
        limits = await TedapiClient(transport).set_export_limit(5)
    assert limits.export_limit_kw == 5 and limits.import_limit_kw is None
    write = transport.sent[1]
    assert write.SerializeToString().hex().startswith(COMMAND_PREFIX)
    request = write.filestore.updateFileRequest
    assert request.hash == b"H"
    assert request.domain == pb.FILE_STORE_API_DOMAIN_CONFIG_JSON
    written = json.loads(request.file.blob)
    assert written == {
        "site_info": {"max_site_meter_power_ac": 1000000000, "other": 1, "min_site_meter_power_ac": -5},
        "vin": "X",
    }
    assert "export limit to 5 kW" in caplog.text


async def test_set_import_limit_none_and_missing_site_info() -> None:
    transport = FakeTransport(config_answer({"site_info": "bad"}), update_ack())
    limits = await TedapiClient(transport).set_import_limit(None)
    assert limits.import_limit_kw is None
    written = json.loads(transport.sent[1].filestore.updateFileRequest.file.blob)
    assert written["site_info"] == {"max_site_meter_power_ac": 1000000000}


async def test_set_import_limit_value() -> None:
    transport = FakeTransport(config_answer({}), update_ack())
    limits = await TedapiClient(transport).set_import_limit(7.5)
    assert limits.import_limit_kw == 7.5


async def test_limit_write_needs_signed_connection(caplog: pytest.LogCaptureFixture) -> None:
    transport = FakeTransport(signed=False)
    client = TedapiClient(transport)
    with caplog.at_level(logging.WARNING), pytest.raises(SignedConnectionRequired):
        await client.set_export_limit(5)
    with pytest.raises(SignedConnectionRequired):
        await client.set_import_limit(5)
    assert transport.sent == []
    assert "Setting" not in caplog.text  # nothing is announced that isn't sent


async def test_invalid_limit_before_any_io() -> None:
    transport = FakeTransport()
    with pytest.raises(ValueError, match="kilowatts"):
        await TedapiClient(transport).set_import_limit(-1)
    assert transport.sent == []


async def test_limit_write_not_acknowledged() -> None:
    transport = FakeTransport(config_answer({}), config_answer({}))
    with pytest.raises(UnexpectedResponseError):
        await TedapiClient(transport).set_export_limit(5)


async def test_limit_write_rejected() -> None:
    transport = FakeTransport(config_answer({}), error_answer(5, "hash mismatch"))
    with pytest.raises(GatewayRejectedError, match="hash mismatch"):
        await TedapiClient(transport).set_export_limit(5)


# ── Battery calibration delay ───────────────────────────────────────


async def test_calibration_status_pinned_bytes() -> None:
    def build(envelope: pb.MessageEnvelope) -> None:
        reply = envelope.teg.get_delay_battery_calibration_status_response
        reply.calibration_delays_left = 2
        reply.calibration_delay_remaining_seconds = 3600
        reply.max_calibration_delays = 3

    transport = FakeTransport(answer_with(build))
    status = await TedapiClient(transport).get_battery_calibration_delay_status()
    # Same bytes as pypowerwall's pinned test (test_v1r_calibration_delay.py).
    assert transport.sent[0].SerializeToString().hex() == COMMAND_PREFIX + "2a03ea0400"
    assert status.to_dict() == {
        "calibration_delays_left": 2,
        "calibration_delay_remaining_seconds": 3600,
        "max_calibration_delays": 3,
    }


async def test_calibration_status_not_implemented() -> None:
    # A Powerwall 3 on firmware 26.34.3 answers this (pypowerwall's capture).
    answer = pb.MessageEnvelope()
    answer.ParseFromString(bytes.fromhex("22170a150a13080c120f6e6f7420696d706c656d656e746564"))
    with pytest.raises(NotSupportedError):
        await TedapiClient(FakeTransport(answer)).get_battery_calibration_delay_status()


async def test_delay_calibration_pinned_bytes(caplog: pytest.LogCaptureFixture) -> None:
    answer = pb.MessageEnvelope()
    answer.ParseFromString(bytes.fromhex("2a03e20400"))  # delay_battery_calibration_response
    transport = FakeTransport(answer)
    with caplog.at_level(logging.WARNING):
        await TedapiClient(transport).delay_battery_calibration(24)
    assert transport.sent[0].SerializeToString().hex() == COMMAND_PREFIX + "2a05da04020818"
    assert "24 h" in caplog.text


@pytest.mark.parametrize("hours", [0, -1, 2**32, 1.5, True, "24"])
async def test_delay_calibration_invalid(hours: object) -> None:
    transport = FakeTransport()
    with pytest.raises(ValueError, match="positive integer"):
        await TedapiClient(transport).delay_battery_calibration(hours)  # type: ignore[arg-type]
    assert transport.sent == []


async def test_calibration_needs_signed_connection() -> None:
    client = TedapiClient(FakeTransport(signed=False))
    with pytest.raises(SignedConnectionRequired):
        await client.get_battery_calibration_delay_status()
    with pytest.raises(SignedConnectionRequired):
        await client.delay_battery_calibration(24)


async def test_delay_calibration_wrong_answer() -> None:
    transport = FakeTransport(answer_with(lambda e: e.teg.dispatch_battery_power_response.SetInParent()))
    with pytest.raises(UnexpectedResponseError):
        await TedapiClient(transport).delay_battery_calibration(24)


# ── Registered keys ─────────────────────────────────────────────────


def clients_answer(*keys: bytes) -> pb.MessageEnvelope:
    def build(envelope: pb.MessageEnvelope) -> None:
        response = envelope.authorization.list_authorized_clients_response
        for index, key in enumerate(keys):
            record = response.clients.add()
            record.public_key = key
            record.type = pb.AUTHORIZED_CLIENT_TYPE_CUSTOMER_MOBILE_APP
            record.key_type = pb.AUTHORIZED_KEY_TYPE_RSA
            record.state = pb.AUTHORIZED_STATE_VERIFIED
            record.description = f"client {index}"
        response.enable_line_switch_off = True

    return answer_with(build)


async def test_list_clients(key: RsaKey) -> None:
    transport = FakeTransport(clients_answer(key.public_key_der, b"\x01\x02"), signed=False)
    clients = await TedapiClient(transport).get_authorized_clients()
    assert transport.sent[0].SerializeToString().hex() == READ_PREFIX + "62022a00"
    assert [c.state for c in clients.clients] == ["VERIFIED", "VERIFIED"]
    assert clients.clients[0].fingerprint == key.fingerprint
    assert clients.enable_line_switch_off


async def test_add_client(key: RsaKey, caplog: pytest.LogCaptureFixture) -> None:
    other = RsaKey.generate(2048)

    def build(envelope: pb.MessageEnvelope) -> None:
        record = envelope.authorization.add_authorized_client_response.client
        record.public_key = other.public_key_der
        record.state = pb.AUTHORIZED_STATE_PENDING_VERIFICATION
        record.verification = pb.AUTHORIZED_VERIFICATION_TYPE_HERMES_COMMAND

    transport = FakeTransport(answer_with(build), public_key_der=key.public_key_der)
    with caplog.at_level(logging.WARNING):
        client = await TedapiClient(transport).add_authorized_client(other.private_pem(), "test")
    request = transport.sent[0]
    assert request.SerializeToString().hex().startswith(COMMAND_PREFIX)
    add = request.authorization.add_authorized_client_request
    assert add.public_key == other.public_key_der
    assert add.description == "test"
    assert add.type == pb.AUTHORIZED_CLIENT_TYPE_CUSTOMER_MOBILE_APP
    assert add.key_type == pb.AUTHORIZED_KEY_TYPE_RSA
    assert client.state == "PENDING_VERIFICATION"
    assert client.verification == "HERMES_COMMAND"
    assert other.fingerprint[:16] in caplog.text


async def test_add_client_bad_key_before_io() -> None:
    transport = FakeTransport()
    with pytest.raises(ValueError, match="could not be read"):
        await TedapiClient(transport).add_authorized_client(b"\x00\x01")
    assert transport.sent == []


async def test_key_commands_need_signed_connection(key: RsaKey) -> None:
    client = TedapiClient(FakeTransport(signed=False))
    with pytest.raises(SignedConnectionRequired):
        await client.add_authorized_client(key)
    with pytest.raises(SignedConnectionRequired):
        await client.remove_authorized_client(key)


async def test_remove_client_by_key(key: RsaKey) -> None:
    other = RsaKey.generate(2048)
    ack = answer_with(lambda e: e.authorization.remove_authorized_client_response.SetInParent())
    transport = FakeTransport(ack, public_key_der=key.public_key_der)
    await TedapiClient(transport).remove_authorized_client(other)
    assert transport.sent[0].authorization.remove_authorized_client_request.public_key == other.public_key_der


async def test_remove_client_by_fingerprint_prefix(key: RsaKey) -> None:
    other = RsaKey.generate(2048)
    ack = answer_with(lambda e: e.authorization.remove_authorized_client_response.SetInParent())
    transport = FakeTransport(
        clients_answer(key.public_key_der, other.public_key_der), ack, public_key_der=key.public_key_der
    )
    await TedapiClient(transport).remove_authorized_client(other.fingerprint[:12].upper())
    assert transport.sent[1].authorization.remove_authorized_client_request.public_key == other.public_key_der


async def test_remove_client_prefix_must_match_one(key: RsaKey) -> None:
    transport = FakeTransport(clients_answer(key.public_key_der), public_key_der=key.public_key_der)
    with pytest.raises(ValueError, match="matches 0 clients"):
        await TedapiClient(transport).remove_authorized_client("00000000")


async def test_remove_current_key_refused(key: RsaKey) -> None:
    transport = FakeTransport(public_key_der=key.public_key_der)
    with pytest.raises(ValueError, match="signs with"):
        await TedapiClient(transport).remove_authorized_client(key)
    assert transport.sent == []


async def test_remove_current_key_allowed(key: RsaKey) -> None:
    ack = answer_with(lambda e: e.authorization.remove_authorized_client_response.SetInParent())
    transport = FakeTransport(ack, public_key_der=key.public_key_der)
    await TedapiClient(transport).remove_authorized_client(key, allow_current_key=True)
    assert len(transport.sent) == 1


async def test_remove_client_pinned_bytes(key: RsaKey) -> None:
    ack = answer_with(lambda e: e.authorization.remove_authorized_client_response.SetInParent())
    transport = FakeTransport(ack, public_key_der=key.public_key_der)
    await TedapiClient(transport).remove_authorized_client(b"\x01\x02")
    # Same bytes as pypowerwall's remove_authorized_client builds.
    assert transport.sent[0].SerializeToString().hex() == COMMAND_PREFIX + "62061a040a020102"
