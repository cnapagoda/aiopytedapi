"""Which battery units a site has, and where each one is in the readings.

:meth:`BatteryInventory.from_payloads` combines the gateway's ``config.json``
(the units the site is set up with) with each Powerwall's component readings
(the units that actually report) into one immutable inventory:

    inventory = BatteryInventory.from_payloads(
        config, gateway_din=client.din, components={leader_din: payload})
    for unit in inventory.powerwalls:
        print(unit.role, unit.part_number, len(inventory.expansions_of(unit)))

Each Powerwall's component readings come from that Powerwall alone (the
leader over the signed connection, a follower over its own Gateway Wi-Fi
query), so a unit's ``slot`` is its index in *its Powerwall's* ``bms`` and
``hvp`` lists: 0 for the Powerwall itself, 1 and up for its expansion packs.

DINs and serial numbers identify a site: they're kept out of ``repr``, and
``to_dict`` only includes them with ``details=True``.
"""

from __future__ import annotations

import enum
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union, overload

#: A component row without a serial number and with less energy than this
#: (kWh) is a registered pack that isn't there, not a real one: a real pack
#: never reads below its hidden 5 % reserve (about 0.7 kWh).
PHANTOM_ENERGY_KWH = 0.5

_DIN_SEPARATOR = "--"


class UnitRole(str, enum.Enum):
    """What a battery unit is on its site."""

    #: The Powerwall that is also the site's gateway (Powerwall 3).
    LEADER = "leader"
    #: Another Powerwall on a site whose gateway is a Powerwall.
    FOLLOWER = "follower"
    #: A Powerwall on a site with a separate gateway (Backup Gateway, Gateway 3).
    POWERWALL = "powerwall"
    #: An expansion pack: a battery without an inverter, part of a Powerwall.
    EXPANSION = "expansion"

    def __str__(self) -> str:
        return self.value


def split_din(din: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """``(part number, serial number)`` of a DIN such as
    ``1707000-11-J--TG12…``; ``(None, None)`` parts when it has no such form."""
    if not din or _DIN_SEPARATOR not in din:
        return None, None
    part, _, serial = din.rpartition(_DIN_SEPARATOR)
    return part or None, serial or None


@dataclass(frozen=True)
class BatteryUnit:
    """One Powerwall or expansion pack.

    ``slot`` is the unit's index in its Powerwall's component lists, or None
    when the unit is configured but not in the readings (no readings for
    that Powerwall, or the pack doesn't report). ``powerwall_din`` is the DIN
    of the Powerwall the unit belongs to (its own for a Powerwall).
    ``unassigned_slots`` (Powerwalls only) lists component rows that match no
    configured unit and have no serial number to tell what they are."""

    role: UnitRole
    slot: Optional[int]
    part_number: Optional[str]
    model: Optional[str] = None  # config.json's block type, e.g. "Powerwall3"
    din: Optional[str] = field(default=None, repr=False)
    serial: Optional[str] = field(default=None, repr=False)
    powerwall_din: Optional[str] = field(default=None, repr=False)
    unassigned_slots: Tuple[int, ...] = ()

    @property
    def is_powerwall(self) -> bool:
        return self.role is not UnitRole.EXPANSION

    @property
    def configured(self) -> bool:
        """Set up in config.json (an expansion found only in the readings is not)."""
        return self.din is not None

    @property
    def reporting(self) -> bool:
        """In the component readings."""
        return self.slot is not None

    def to_dict(self, details: bool = False) -> Dict[str, Any]:
        """JSON-safe dict; ``details`` adds the DINs and the serial number."""
        data: Dict[str, Any] = {
            "role": self.role.value,
            "model": self.model,
            "part_number": self.part_number,
            "slot": self.slot,
            "configured": self.configured,
        }
        if self.is_powerwall:
            data["unassigned_slots"] = list(self.unassigned_slots)
        if details:
            data.update(din=self.din, serial=self.serial, powerwall_din=self.powerwall_din)
        return data


@dataclass(frozen=True)
class _Row:
    """One component slot of a Powerwall's readings."""

    slot: int
    serial: Optional[str]
    part_number: Optional[str]
    full_kwh: Optional[float]
    remaining_kwh: Optional[float]

    @property
    def phantom(self) -> bool:
        if self.serial:
            return False
        if not self.full_kwh or self.full_kwh <= 0:
            return True
        return self.remaining_kwh is not None and self.remaining_kwh < PHANTOM_ENERGY_KWH


def _text(value: Any) -> Optional[str]:
    return value.strip() or None if isinstance(value, str) else None


def _signal(item: Mapping[str, Any], name: str) -> Optional[float]:
    for signal in item.get("signals") or ():
        if isinstance(signal, Mapping) and signal.get("name") == name:
            value = signal.get("value")
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return float(value)
            return None
    return None


def _rows(payload: Any) -> List[_Row]:
    """The battery rows of one Powerwall's component readings: the HVP rows
    carry the serial and part numbers, the BMS rows the energy, index by index."""
    if isinstance(payload, Mapping) and isinstance(payload.get("components"), Mapping):
        payload = payload["components"]
    if not isinstance(payload, Mapping):
        return []

    def items(kind: str) -> List[Mapping[str, Any]]:
        found = payload.get(kind)
        return [i if isinstance(i, Mapping) else {} for i in found] if isinstance(found, list) else []

    bms, hvp = items("bms"), items("hvp")
    rows = []
    for slot in range(max(len(bms), len(hvp))):
        sources = [s[slot] for s in (hvp, bms) if slot < len(s)]
        battery = bms[slot] if slot < len(bms) else {}
        rows.append(
            _Row(
                slot=slot,
                serial=next((v for s in sources if (v := _text(s.get("serialNumber")))), None),
                part_number=next((v for s in sources if (v := _text(s.get("partNumber")))), None),
                full_kwh=_signal(battery, "BMS_nominalFullPackEnergy"),
                remaining_kwh=_signal(battery, "BMS_nominalEnergyRemaining"),
            )
        )
    return rows


def _block_din(block: Mapping[str, Any]) -> Optional[str]:
    return _text(block.get("vin")) or _text(block.get("din"))


def _powerwall_units(block: Mapping[str, Any], role: UnitRole, payload: Any, has_payload: bool) -> List[BatteryUnit]:
    """A Powerwall and its expansion packs, matched to its readings by serial."""
    din = _block_din(block)
    part, serial = split_din(din)
    rows = _rows(payload) if has_payload else []
    own = rows[0] if rows else None
    by_serial = {row.serial: row for row in rows[1:] if row.serial}

    expansions: List[BatteryUnit] = []
    claimed = set()
    for expansion in block.get("battery_expansions") or ():
        exp_din = _block_din(expansion) if isinstance(expansion, Mapping) else None
        if exp_din is None:
            continue
        exp_part, exp_serial = split_din(exp_din)
        row = by_serial.get(exp_serial) if exp_serial else None
        if row is not None:
            claimed.add(row.slot)
        expansions.append(
            BatteryUnit(
                role=UnitRole.EXPANSION,
                slot=None if row is None else row.slot,
                part_number=exp_part or (row.part_number if row else None),
                din=exp_din,
                serial=exp_serial,
                powerwall_din=din,
            )
        )
    unassigned = []
    for row in rows[1:]:
        if row.slot in claimed or row.phantom:
            continue
        if row.serial:
            # A pack the config doesn't list yet (it updates after the readings).
            expansions.append(
                BatteryUnit(
                    role=UnitRole.EXPANSION,
                    slot=row.slot,
                    part_number=row.part_number,
                    serial=row.serial,
                    powerwall_din=din,
                )
            )
        else:
            unassigned.append(row.slot)

    powerwall = BatteryUnit(
        role=role,
        slot=None if own is None else own.slot,
        part_number=part or (own.part_number if own else None),
        model=_text(block.get("type")),
        din=din,
        serial=serial or (own.serial if own else None),
        powerwall_din=din,
        unassigned_slots=tuple(unassigned),
    )
    return [powerwall, *expansions]


@dataclass(frozen=True)
class BatteryInventory(Sequence[BatteryUnit]):
    """Every battery unit of a site: each Powerwall followed by its expansion
    packs, in config.json's order. A read-only sequence of
    :class:`BatteryUnit`."""

    units: Tuple[BatteryUnit, ...] = ()

    @classmethod
    def from_payloads(
        cls,
        config: Mapping[str, Any],
        *,
        gateway_din: Optional[str],
        components: Optional[Mapping[str, Any]] = None,
    ) -> BatteryInventory:
        """Build the inventory from ``config.json`` and, optionally, component
        readings keyed by the DIN of the Powerwall they came from.

        The Powerwall whose DIN is ``gateway_din`` is the leader and the other
        Powerwalls are its followers; when no Powerwall has that DIN, the
        gateway is a separate device and every Powerwall has the role
        ``POWERWALL``. A Powerwall without readings is still listed, with
        ``slot`` None."""
        readings = components or {}
        blocks = [b for b in (config.get("battery_blocks") or ()) if isinstance(b, Mapping)]
        dins = [_block_din(b) for b in blocks]
        led = gateway_din is not None and gateway_din in dins
        units: List[BatteryUnit] = []
        for block, din in zip(blocks, dins):
            if not led:
                role = UnitRole.POWERWALL
            elif din == gateway_din:
                role = UnitRole.LEADER
            else:
                role = UnitRole.FOLLOWER
            has_payload = din is not None and din in readings
            payload = readings[din] if din is not None and has_payload else None
            units.extend(_powerwall_units(block, role, payload, has_payload))
        return cls(tuple(units))

    # ── Sequence ─────────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self.units)

    def __iter__(self) -> Iterator[BatteryUnit]:
        return iter(self.units)

    @overload
    def __getitem__(self, index: int) -> BatteryUnit: ...

    @overload
    def __getitem__(self, index: slice) -> Tuple[BatteryUnit, ...]: ...

    def __getitem__(self, index: Union[int, slice]) -> Union[BatteryUnit, Tuple[BatteryUnit, ...]]:
        return self.units[index]

    # ── Lookups ──────────────────────────────────────────────────────

    @property
    def leader(self) -> Optional[BatteryUnit]:
        """The Powerwall that is the gateway, or None on a site with a separate gateway."""
        return next((u for u in self.units if u.role is UnitRole.LEADER), None)

    @property
    def powerwalls(self) -> Tuple[BatteryUnit, ...]:
        return tuple(u for u in self.units if u.is_powerwall)

    @property
    def expansions(self) -> Tuple[BatteryUnit, ...]:
        return tuple(u for u in self.units if not u.is_powerwall)

    def expansions_of(self, powerwall: Union[BatteryUnit, str]) -> Tuple[BatteryUnit, ...]:
        """The expansion packs of a Powerwall (the unit or its DIN)."""
        din = powerwall.din if isinstance(powerwall, BatteryUnit) else powerwall
        return tuple(u for u in self.expansions if din is not None and u.powerwall_din == din)

    def find(self, identifier: str) -> Optional[BatteryUnit]:
        """The unit with this DIN or serial number (case-insensitive), or None."""
        wanted = identifier.strip().upper()
        return next(
            (u for u in self.units if wanted and wanted in {(u.din or "").upper(), (u.serial or "").upper()}),
            None,
        )

    def to_dict(self, details: bool = False) -> Dict[str, Any]:
        return {"units": [unit.to_dict(details=details) for unit in self.units]}


__all__ = ["PHANTOM_ENERGY_KWH", "BatteryInventory", "BatteryUnit", "UnitRole", "split_din"]
