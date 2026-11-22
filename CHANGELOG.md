# Changelog

## 0.2.0 (unreleased)

- Battery inventory: `BatteryInventory` lists each Powerwall (leader, follower, or behind a separate gateway) and its expansion packs, with DIN, serial and part number, and each unit's slot in its Powerwall's component readings. Built by `TedapiClient.get_battery_inventory()` or `BatteryInventory.from_payloads()`. Configured packs that don't report have no slot; unlisted packs found in the readings are included; phantom rows (no serial, almost no energy) are skipped.

## 0.1.0 (2026-11-19)

First release.

- Async client (`TedapiClient`) over an aiohttp session you provide, with two connections: signed (`/tedapi/v1r`, RSA key) and Gateway Wi-Fi (`/tedapi/v1`, Wi-Fi password, read-only).
- Network status: each interface's state, connectivity and signal strength.
- Site import/export limits: read on both connections, set over the signed connection.
- Battery calibration delay: status and delay, over the signed connection.
- Registered keys: list on both connections; add and remove over the signed connection.
- Gateway configuration (config.json) read.
- Typed exceptions for every failure (`TedapiError` and subclasses).
