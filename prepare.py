#!/usr/bin/env python3
"""Print configuration for one RustDesk controller and one Mac."""

import argparse
import ipaddress
import json
import re

PORT = 21118
TAILSCALE_IPV4 = ipaddress.IPv4Network("100.64.0.0/10")
TAILSCALE_IPV6 = ipaddress.IPv6Network("fd7a:115c:a1e0::/48")
RESERVED_IPV4 = tuple(
    ipaddress.IPv4Network(network)
    for network in (
        "100.100.0.0/24",
        "100.100.100.0/24",
        "100.115.92.0/23",
        "100.101.102.103/32",
    )
)


def tailnet_ipv4(value):
    try:
        address = ipaddress.IPv4Address(value)
    except ValueError:
        raise argparse.ArgumentTypeError("expected a single IPv4 address") from None
    if address not in TAILSCALE_IPV4 or any(address in net for net in RESERVED_IPV4):
        raise argparse.ArgumentTypeError("expected an assignable Tailscale IPv4 address")
    return str(address)


def tailnet_ipv6(value):
    try:
        address = ipaddress.IPv6Address(value)
    except ValueError:
        raise argparse.ArgumentTypeError("expected a single IPv6 address") from None
    if (
        address not in TAILSCALE_IPV6
        or address.scope_id is not None
        or address == ipaddress.IPv6Address("fd7a:115c:a1e0::53")
    ):
        raise argparse.ArgumentTypeError("expected an assignable Tailscale IPv6 address")
    return str(address)


def policy(args):
    hosts = {"rustdesk-pixel": args.pixel_ip, "rustdesk-mac": args.mac_ip}
    destination = f"rustdesk-mac:{PORT}"
    tests = [{"src": "rustdesk-pixel", "proto": "tcp", "accept": [destination]}]
    denied = [destination]
    if args.mac_ipv6:
        ipv6_destination = f"[{args.mac_ipv6}]:{PORT}"
        tests[0]["deny"] = [ipv6_destination]
        denied.append(ipv6_destination)

    for index, address in enumerate(args.deny_peer, start=1):
        alias = f"rustdesk-denied-{index}"
        hosts[alias] = address
        tests.append({"src": alias, "proto": "tcp", "deny": denied})

    return {
        "hosts": hosts,
        "grants": [
            {"src": ["rustdesk-pixel"], "dst": ["rustdesk-mac"], "ip": [f"tcp:{PORT}"]}
        ],
        "tests": tests,
    }


def firewall(args):
    return "\n".join(
        (
            "# Place in a macOS PF filter anchor. See docs/setup.md.",
            f"block in quick on ! {args.tunnel_interface} proto tcp from any to any port {PORT}",
            f"block in quick inet6 proto tcp from any to any port {PORT}",
            f"block in quick inet proto tcp from ! {args.pixel_ip} to any port {PORT}",
            f"block in quick inet proto tcp from any to ! {args.mac_ip} port {PORT}",
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pixel_ip", type=tailnet_ipv4)
    parser.add_argument("mac_ip", type=tailnet_ipv4)
    parser.add_argument("--format", choices=("policy", "pf", "rustdesk"), default="policy")
    parser.add_argument("--deny-peer", type=tailnet_ipv4, action="append", default=[])
    parser.add_argument("--mac-ipv6", type=tailnet_ipv6)
    parser.add_argument("--tunnel-interface", metavar="utunN")
    args = parser.parse_args()

    if len(set([args.pixel_ip, args.mac_ip, *args.deny_peer])) != 2 + len(args.deny_peer):
        parser.error("device IPv4 addresses must be distinct")
    if args.format != "policy" and (args.deny_peer or args.mac_ipv6):
        parser.error("--deny-peer and --mac-ipv6 require --format policy")
    if args.format == "pf":
        if not re.fullmatch(r"utun[0-9]+", args.tunnel_interface or ""):
            parser.error("--format pf requires --tunnel-interface utunN")
        print(firewall(args))
    elif args.tunnel_interface:
        parser.error("--tunnel-interface requires --format pf")
    elif args.format == "rustdesk":
        print(f"Mac Direct IP port: {PORT}")
        print(f"Mac IP allowlist: {args.pixel_ip}/32")
        print(f"Pixel connection address: {args.mac_ip}:{PORT}")
    else:
        print(json.dumps(policy(args), indent=2))


if __name__ == "__main__":
    main()
