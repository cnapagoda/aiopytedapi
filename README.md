# aiopytedapi

An async Python client for the Tesla Powerwall gateway's local TEDAPI.

- **Async only**, built on [aiohttp](https://docs.aiohttp.org/). You pass in the `ClientSession`, so it fits Home Assistant and other asyncio apps.
- **Typed** (`py.typed`, checked with `mypy --strict`).
- **Local**: talks to the gateway on your network. Nothing goes to Tesla's servers.
- **Errors are exceptions**, never `None`: every one derives from `TedapiError`.

> **Status: alpha (0.x).** The API may change between minor versions. Pin `aiopytedapi>=0.1,<0.2`.

## Connections

| Connection | Endpoint | Authenticates with | Can change settings |
|---|---|---|---|
| **Signed** | `/tedapi/v1r` on the gateway's home-network address or its Wi-Fi address (192.168.91.1) | An RSA key registered with the gateway | Yes |
| **Gateway Wi-Fi** | `/tedapi/v1` on 192.168.91.1 | The Wi-Fi password printed on the gateway | No (read-only) |

Registering a key needs Tesla's cloud once (for example `python -m pypowerwall register`). This library doesn't do that step.

## Features

| Feature | Methods | Signed | Gateway Wi-Fi |
|---|---|---|---|
| Network status (Wi-Fi, Ethernet, cellular) | `get_network_status()` | ✅ Powerwall 3 | ✅ Powerwall 3 and 2 |
| Site import/export limits | `get_site_limits()`, `set_import_limit()`, `set_export_limit()` | ✅ read and write | ✅ read |
| Battery calibration delay | `get_battery_calibration_delay_status()`, `delay_battery_calibration()` | ✅ | — |
| Registered keys | `get_authorized_clients()`, `add_authorized_client()`, `remove_authorized_client()` | ✅ list, add, remove | ✅ list |
| Gateway configuration | `get_config()` | ✅ | ✅ |
| Battery inventory (Powerwalls, expansion packs) | `get_battery_inventory()`, `BatteryInventory.from_payloads()` | ✅ | ✅ |

What has been seen on hardware so far:

- **Network status:** Powerwall 3 (firmware 26.34.3) on both connections; Powerwall 2 (26.42.0) on Gateway Wi-Fi only. Over the signed connection a Powerwall 2 answers `MessageFaultError` (`MESSAGEFAULT_ERROR_TIMEOUT`).
- **Registered keys:** listing, adding and removing on a Powerwall 3 (26.34.3).
- **Site limits:** reading on a Powerwall 3 (26.34.3). Writing has not been tried on hardware.
- **Battery inventory:** built from config.json plus the component readings you pass in (keyed by each Powerwall's DIN); this library doesn't read components itself yet. Tested against recorded payload shapes only.
- **Calibration delay:** a Powerwall 3 on 26.34.3 answers `NotSupportedError` (the firmware doesn't implement it). The delay command has not been sent to hardware.

## Example

```python
import asyncio
from pathlib import Path

import aiohttp

from aiopytedapi import RsaKey, TedapiClient


async def main() -> None:
    key = RsaKey.from_pem(Path("tedapi_rsa_private.pem").read_bytes())
    async with aiohttp.ClientSession() as session:
        client = TedapiClient.signed(session, "192.168.1.50", key, password="ABCDE")
        await client.connect()

        status = await client.get_network_status()
        print(status.active, status.to_dict())

        limits = await client.get_site_limits()
        print(limits.import_limit_kw, limits.export_limit_kw)

        for c in (await client.get_authorized_clients()).clients:
            print(c.fingerprint[:16], c.type, c.state)


asyncio.run(main())
```

`password` is the customer login password (the last 5 characters of the Gateway Wi-Fi password on most gateways). It's used to fetch the DIN. Pass `din=` instead if you already know it.

For the Gateway Wi-Fi connection:

```python
client = TedapiClient.wifi(session, "WIFI_PASSWORD")
```

## Safety

Some commands change how your Powerwall and your site behave.

- **Site limits:** an installer may have set the import or export limit to meet your grid connection agreement (for example a network export limit). Don't raise or remove one unless you're allowed to.
- **Calibration delay:** the gateway allows a limited number of delays, and each may use one.
- **Removing a key** stops that client sending commands. Removing the key you sign with is refused unless you pass `allow_current_key=True`.

Every command that changes something logs a WARNING. You use these commands at your own risk; check your warranty and your grid connection agreement first.

## Privacy

Models keep values that identify a home or a person (Wi-Fi SSID, MAC and IP addresses, key descriptions, DINs and serial numbers) out of `repr`, and `to_dict()` only includes them with `details=True`. The gateway's Wi-Fi password is never parsed. `get_config()` returns the gateway's full configuration, which includes identifiers: don't log or publish it.

## Credits

The wire schema and the request formats come from [pypowerwall](https://github.com/jasonacox/pypowerwall) (MIT), which in turn credits Matthew1471's Tesla-API, Nexarian's TEDAPI work and [Teslemetry/tesla-protocol](https://github.com/Teslemetry/tesla-protocol). See [NOTICE](NOTICE).

This project is not affiliated with or endorsed by Tesla.

## Development

```bash
pip install -e . pytest pytest-asyncio pytest-cov mypy ruff types-protobuf
ruff check . && mypy && pytest --cov
```

The protobuf bindings are generated: change `src/aiopytedapi/_proto/tedapi.proto`, then run `bash tools/gen_proto.sh`. Never edit `tedapi_pb2.py` by hand.

## Licence

MIT. See [LICENSE](LICENSE).
