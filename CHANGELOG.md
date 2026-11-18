# Changelog

## 0.1.0 (unreleased)

First release.

- Async client (`TedapiClient`) over an aiohttp session you provide, with two connections: signed (`/tedapi/v1r`, RSA key) and Gateway Wi-Fi (`/tedapi/v1`, Wi-Fi password, read-only).
- Network status: each interface's state, connectivity and signal strength.
- Site import/export limits: read on both connections, set over the signed connection.
- Battery calibration delay: status and delay, over the signed connection.
- Registered keys: list on both connections; add and remove over the signed connection.
- Gateway configuration (config.json) read.
- Typed exceptions for every failure (`TedapiError` and subclasses).
