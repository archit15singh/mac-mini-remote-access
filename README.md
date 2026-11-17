# Mac mini Remote Access

Use an Android phone to control a dual-display Mac mini over a private Tailscale connection. RustDesk handles screen sharing and input. The setup supports a Mac that is awake with a logged-in user session, including a screen lock once validated.

| Layer | Configuration |
| --- | --- |
| Tailscale | One phone IPv4 address can reach one Mac IPv4 address on TCP 21118. |
| macOS | Packet Filter rules restrict the listener to that source, destination, and tunnel interface. |
| RustDesk | Direct IP, an exact IP allowlist, a unique permanent password, and only the permissions needed for viewing and input. |

RustDesk's direct listener can bind to multiple interfaces, and the direct IP transport should be treated as unencrypted. Tailscale provides WireGuard encryption, including when it uses a DERP relay. The host filter is what closes the direct listener to ordinary LAN traffic. Public RustDesk registration is a separate path and has its own acceptance check. [RustDesk listener source](https://github.com/rustdesk/rustdesk/blob/master/src/rendezvous_mediator.rs#L1403) · [RustDesk Direct IP discussion](https://github.com/rustdesk/rustdesk/discussions/532) · [Tailscale connection types](https://tailscale.com/docs/reference/connection-types)

[`prepare.py`](prepare.py) uses Python 3.9+ and prints a policy fragment, a macOS filter fragment, or RustDesk settings. It makes no network requests and applies no configuration. The [setup and rollback guide](docs/setup.md) covers deployment. The [validation checklist](docs/validation.md) covers Wi-Fi, cellular, both monitors, access restrictions, and recovery.

**Deployment status** — Configuration prepared for later deployment. Device and network validation is pending.
