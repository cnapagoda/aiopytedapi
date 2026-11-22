"""BatteryInventory: which Powerwalls and expansion packs a site has, and
where each one is in its Powerwall's component readings."""

from __future__ import annotations

from typing import Any

from aiopytedapi import BatteryInventory, BatteryUnit, TedapiClient, UnitRole, split_din

from .conftest import DIN, FakeTransport
from .test_client import config_answer

LEADER = "1707000-11-J--TG1200000001AA"
FOLLOWER = "1707000-11-J--TG1200000002BB"
EXPANSION = "1807000-10-B--TG1250000003CC"
MISSING = "1807000-10-B--TG1250000004DD"


def bms(remaining: Any = 10.0, full: Any = 13.5) -> dict[str, Any]:
    return {
        "signals": [
            {"name": "BMS_nominalEnergyRemaining", "value": remaining},
            {"name": "BMS_nominalFullPackEnergy", "value": full},
        ]
    }


def hvp(din: str | None) -> dict[str, Any]:
    part, serial = split_din(din)
    return {"partNumber": part or "", "serialNumber": serial or "", "signals": []}


def readings(*rows: tuple[str | None, dict[str, Any]]) -> dict[str, Any]:
    return {"components": {"hvp": [hvp(din) for din, _ in rows], "bms": [b for _, b in rows], "pch": [{}]}}


def config(*blocks: dict[str, Any]) -> dict[str, Any]:
    return {"battery_blocks": list(blocks)}


def block(din: str, *expansions: str, kind: str = "Powerwall3") -> dict[str, Any]:
    return {"vin": din, "type": kind, "battery_expansions": [{"din": e} for e in expansions]}


def test_single_powerwall() -> None:
    inventory = BatteryInventory.from_payloads(
        config(block(LEADER)), gateway_din=LEADER, components={LEADER: readings((LEADER, bms()))}
    )
    assert len(inventory) == 1
    unit = inventory.leader
    assert unit is not None and unit is inventory[0]
    assert (unit.role, unit.slot, unit.model, unit.part_number) == (UnitRole.LEADER, 0, "Powerwall3", "1707000-11-J")
    assert (unit.din, unit.serial, unit.powerwall_din) == (LEADER, "TG1200000001AA", LEADER)
    assert unit.is_powerwall and unit.configured and unit.reporting
    assert inventory.expansions == () and inventory.expansions_of(unit) == ()


def test_leader_expansion_and_follower_without_readings() -> None:
    inventory = BatteryInventory.from_payloads(
        config(block(LEADER, EXPANSION), block(FOLLOWER, kind="Powerwall3Follower")),
        gateway_din=LEADER,
        components={LEADER: readings((LEADER, bms()), (EXPANSION, bms(9.0)))},
    )
    assert [u.role for u in inventory] == [UnitRole.LEADER, UnitRole.EXPANSION, UnitRole.FOLLOWER]
    expansion = inventory[1]
    assert (expansion.slot, expansion.part_number, expansion.powerwall_din) == (1, "1807000-10-B", LEADER)
    assert inventory.expansions_of(LEADER) == (expansion,)
    assert inventory.expansions_of(inventory[0]) == (expansion,)
    follower = inventory[2]
    assert follower.slot is None and not follower.reporting
    assert inventory.expansions_of(follower) == ()
    assert inventory.powerwalls == (inventory[0], follower)


def test_follower_with_its_own_readings() -> None:
    inventory = BatteryInventory.from_payloads(
        config(block(LEADER), block(FOLLOWER, EXPANSION)),
        gateway_din=LEADER,
        components={LEADER: readings((LEADER, bms())), FOLLOWER: readings((FOLLOWER, bms()), (EXPANSION, bms()))},
    )
    assert [(u.role, u.slot) for u in inventory] == [
        (UnitRole.LEADER, 0),
        (UnitRole.FOLLOWER, 0),
        (UnitRole.EXPANSION, 1),
    ]
    assert inventory.expansions_of(FOLLOWER) == (inventory[2],)


def test_configured_expansion_not_reporting() -> None:
    inventory = BatteryInventory.from_payloads(
        config(block(LEADER, MISSING)), gateway_din=LEADER, components={LEADER: readings((LEADER, bms()))}
    )
    missing = inventory[1]
    assert missing.role is UnitRole.EXPANSION and missing.slot is None and missing.configured
    assert missing.part_number == "1807000-10-B"


def test_pack_missing_from_the_config_is_listed() -> None:
    inventory = BatteryInventory.from_payloads(
        config(block(LEADER)), gateway_din=LEADER, components={LEADER: readings((LEADER, bms()), (EXPANSION, bms()))}
    )
    pack = inventory[1]
    assert (pack.role, pack.slot, pack.din, pack.serial) == (UnitRole.EXPANSION, 1, None, "TG1250000003CC")
    assert not pack.configured and pack.part_number == "1807000-10-B"


def test_phantom_and_unidentified_rows() -> None:
    components = readings(
        (LEADER, bms()),
        (None, bms(remaining=0.1)),  # registered, not there
        (None, bms(full=0)),  # no capacity
        (None, {"signals": [{"name": "BMS_nominalFullPackEnergy", "value": "n/a"}]}),  # no number
        (None, bms()),  # a real pack that can't be told apart
        (None, bms(remaining=None)),  # no remaining reading: kept
    )
    inventory = BatteryInventory.from_payloads(
        config(block(LEADER)), gateway_din=LEADER, components={LEADER: components}
    )
    assert len(inventory) == 1
    assert inventory[0].unassigned_slots == (4, 5)


def test_separate_gateway() -> None:
    # Powerwall 2s with a Backup Gateway: the gateway's DIN is no Powerwall's.
    inventory = BatteryInventory.from_payloads(
        config(block(LEADER, kind="acpw"), block(FOLLOWER, kind="acpw")), gateway_din="1232100-00-E--TG1"
    )
    assert [u.role for u in inventory] == [UnitRole.POWERWALL, UnitRole.POWERWALL]
    assert inventory.leader is None
    assert all(u.slot is None for u in inventory)
    unknown = BatteryInventory.from_payloads(config(block(LEADER)), gateway_din=None)
    assert unknown[0].role is UnitRole.POWERWALL


def test_untidy_payloads() -> None:
    blocks = config(
        {"din": "NOSEPARATOR", "battery_expansions": ["junk", {"din": ""}, {"vin": EXPANSION}]},
        "not a block",  # type: ignore[arg-type]
        {"type": "Powerwall3"},  # no DIN
    )
    components = {
        # The inner dict, a row that isn't a dict, and a serial on BMS only.
        "NOSEPARATOR": {
            "hvp": ["junk"],
            "bms": [{"serialNumber": " TGOWN ", "partNumber": "P1"}, {**bms(), **hvp(EXPANSION)}],
        },
        "": readings(),  # readings for no known Powerwall
    }
    inventory = BatteryInventory.from_payloads(blocks, gateway_din="NOSEPARATOR", components=components)
    own, expansion, other = inventory
    assert (own.role, own.din, own.serial, own.part_number, own.model) == (
        UnitRole.LEADER,
        "NOSEPARATOR",
        "TGOWN",
        "P1",
        None,
    )
    assert expansion.slot == 1
    assert (other.role, other.din, other.slot) == (UnitRole.FOLLOWER, None, None)
    assert inventory.expansions_of(other) == ()
    assert BatteryInventory.from_payloads({}, gateway_din=None, components={"x": "junk"}) == BatteryInventory()
    weird = BatteryInventory.from_payloads(
        config(block(LEADER)), gateway_din=LEADER, components={LEADER: {"components": {"bms": "junk"}}}
    )
    assert weird[0].slot is None
    junk = BatteryInventory.from_payloads(config(block(LEADER)), gateway_din=LEADER, components={LEADER: 3})
    assert junk[0].slot is None


def test_lookups_and_sequence() -> None:
    inventory = BatteryInventory.from_payloads(
        config(block(LEADER, EXPANSION)), gateway_din=LEADER, components={LEADER: readings((LEADER, bms()))}
    )
    assert inventory.find("tg1200000001aa") is inventory[0]
    assert inventory.find(f" {EXPANSION} ") is inventory[1]
    assert inventory.find("") is None and inventory.find("TG9") is None
    assert inventory[0:1] == (inventory[0],)
    assert list(inventory) == list(inventory.units)
    assert inventory[1] in inventory


def test_privacy() -> None:
    inventory = BatteryInventory.from_payloads(
        config(block(LEADER, EXPANSION)), gateway_din=LEADER, components={LEADER: readings((LEADER, bms()))}
    )
    assert "TG12" not in repr(inventory)
    plain = inventory.to_dict()
    assert "TG12" not in str(plain)
    assert plain["units"][0] == {
        "role": "leader",
        "model": "Powerwall3",
        "part_number": "1707000-11-J",
        "slot": 0,
        "configured": True,
        "unassigned_slots": [],
    }
    assert "unassigned_slots" not in plain["units"][1]
    detailed = inventory.to_dict(details=True)["units"][1]
    assert (detailed["din"], detailed["serial"], detailed["powerwall_din"]) == (EXPANSION, "TG1250000003CC", LEADER)


def test_split_din_and_role() -> None:
    assert split_din(LEADER) == ("1707000-11-J", "TG1200000001AA")
    assert split_din(None) == split_din("") == split_din("TG1") == (None, None)
    assert split_din("--TG1") == (None, "TG1") and split_din("P--") == ("P", None)
    assert str(UnitRole.LEADER) == "leader" and UnitRole("expansion") is UnitRole.EXPANSION
    assert BatteryUnit(UnitRole.EXPANSION, None, None).to_dict()["configured"] is False


async def test_client_reads_config_and_din() -> None:
    transport = FakeTransport(config_answer(config(block(DIN))))
    inventory = await TedapiClient(transport).get_battery_inventory({DIN: readings((DIN, bms()))})
    assert inventory.leader is not None and inventory.leader.slot == 0
    known = FakeTransport(config_answer(config(block(LEADER))))
    assert (await TedapiClient(known, din=DIN).get_battery_inventory())[0].role is UnitRole.POWERWALL
    assert known.din_requests == 0
