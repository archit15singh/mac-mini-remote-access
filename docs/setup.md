# Setup and rollback

Do the initial setup from the Mac with a local keyboard and display available. Complete the tailnet policy and host firewall steps before enabling the RustDesk listener. Keep actual addresses, policy backups, and validation notes in the ignored `local/` directory. Store passwords in a password manager.

## 1. Enroll the devices

1. Install Tailscale on the [Mac](https://tailscale.com/docs/install/mac) and [Android phone](https://tailscale.com/docs/install/android). Use one macOS client variant. Sign both devices into the same private tailnet and enable MFA at the identity provider.
2. In the Tailscale admin console, confirm both devices are connected. Copy each device's Tailscale IPv4 from its machine record. Also copy the Mac's tailnet IPv6 if assigned. Pick another enrolled device for a negative test if one is available.
3. Keep the Mac's user signed in. The supported macOS GUI clients need a logged-in user session. [Tailscale macOS client variants](https://tailscale.com/docs/concepts/macos-variants)

## 2. Configure the tailnet

Use a local shell and substitute actual device addresses for each value ending in `_HERE`. The commands write local files for review.

```sh
mkdir -p local
PIXEL_IP=PIXEL_TAILSCALE_IPV4_HERE
MAC_IP=MAC_TAILSCALE_IPV4_HERE
OTHER_IP=OTHER_DEVICE_TAILSCALE_IPV4_HERE
MAC_IPV6=MAC_TAILSCALE_IPV6_HERE

python3 prepare.py "$PIXEL_IP" "$MAC_IP" \
  --deny-peer "$OTHER_IP" --mac-ipv6 "$MAC_IPV6" > local/tailnet-fragment.json
```

Omit `--deny-peer "$OTHER_IP"` when no other device is enrolled and `--mac-ipv6 "$MAC_IPV6"` when the Mac lacks tailnet IPv6. Repeat `--deny-peer` for additional test devices.

1. Export a copy of the active policy from **Access controls** in the Tailscale admin console. Review all existing `grants` and `acls` that can reach the Mac over TCP 21118, including wildcard rules, same-user access, groups, tags, and both address families. Check routes to any alternate address of the Mac.
2. Merge the generated host aliases, single grant, and tests into the existing policy. Preserve unrelated entries and check for name collisions. Narrow any overlapping rules so they preserve intended access elsewhere and exclude this listener. Tailscale combines all matching permissions. Adding the narrow grant by itself leaves broader permissions effective.
3. Save through the policy editor and confirm its assertions pass. The peer-deny assertions cover the specified sources. Audit the full policy and use the live negative tests to establish effective restrictions.

[Tailscale grants explained](https://tailscale.com/docs/features/access-control/grants/grants-explained) · [Tailscale policy test syntax](https://tailscale.com/docs/reference/syntax/policy-file#tests)

## 3. Guard the host listener

1. Check the router for port forwards, automatic mappings, and IPv6 inbound rules. Keep TCP 21118 closed to the internet. Check for Tailscale Funnel or any other publication of this listener.
2. With Tailscale connected, look up the interface for the phone's tailnet route. Confirm that this interface belongs to Tailscale, especially if other VPNs are present. Use its actual name in the second command.

   ```sh
   route -n get "$PIXEL_IP"
   python3 prepare.py "$PIXEL_IP" "$MAC_IP" --format pf \
     --tunnel-interface TAILSCALE_UTUN_HERE > local/rustdesk.pf
   ```

3. Back up the existing macOS PF configuration and record its enabled state. Integrate the generated rules as their own filter anchor. For example, put the fragment at `/etc/pf.anchors/rustdesk-tailnet` with root ownership and add the following in the filter section of the active configuration, before any matching early `quick` passes.

   ```pf
   anchor "rustdesk-tailnet"
   load anchor "rustdesk-tailnet" from "/etc/pf.anchors/rustdesk-tailnet"
   ```

4. Check the complete candidate with `sudo pfctl -nf /path/to/candidate.conf` before loading it through the host's firewall workflow. Confirm PF is enabled and the anchor appears in the active rules. For a manually managed ruleset, inspect it with `sudo pfctl -sr` and `sudo pfctl -a rustdesk-tailnet -sr`. Start with the RustDesk listener off and no previously allowed RustDesk flows. Review skipped interfaces, rule order, and existing state because each can affect the result.
5. The fragment only blocks traffic. Any existing default-deny firewall still needs to permit the exact Pixel-to-Mac flow on the Tailscale interface. The rules cover inbound TCP 21118 on the Mac and are intended for an endpoint, with no forwarded traffic on that port. A `utun` number can change after VPN reconnect or reboot. Recheck the route, update the anchor locally if needed, and repeat the positive and LAN-negative tests before relying on remote access. If app or system changes remove the host firewall guard, turn off Direct IP until it is restored.

## 4. Configure RustDesk

1. Install the official clients from the [RustDesk releases](https://github.com/rustdesk/rustdesk/releases). On macOS, install the helper RustDesk offers for unattended operation, grant Accessibility and Screen Recording, and grant Input Monitoring if the installed build requires it. On Android, use RustDesk as the controller and leave inbound screen sharing disabled. [RustDesk macOS permissions](https://rustdesk.com/docs/en/client/mac/)
2. In the Mac's RustDesk **Security** settings, select password authorization with a permanent password only. Set a long, unique password. Enable **Use IP Whitelisting** and enter the phone's exact Tailscale IPv4 address with `/32`. Keep keyboard and mouse enabled. Disable clipboard, file transfer, remote configuration, tunneling, terminal, audio, camera, and LAN discovery where offered and unneeded. Review the supported options in the installed version.
3. For the stock clients, try setting **Network → ID Server** to `127.0.0.1` on both devices, with no RustDesk server running there and no relay override. Current upstream source returns only the configured custom rendezvous server when that setting is populated. This is a version-dependent way to prevent public registration. Verify it with the clients you install. When loopback configuration is unavailable or public registration persists, use a per-app egress policy on the Mac that blocks RustDesk and its helpers from public destinations while preserving the tailnet flow. Leave **Stop service** off since it also stops the Direct IP listener. [RustDesk rendezvous configuration](https://github.com/rustdesk/hbb_common/blob/master/src/config.rs#L1072) · [RustDesk service and listener source](https://github.com/rustdesk/rustdesk/blob/master/src/rendezvous_mediator.rs#L1403)
4. Enable **Direct IP Access** on TCP 21118 on the Mac. On the phone, enter the Mac's Tailscale IPv4 followed by `:21118`. Connect with the permanent password. To print the relevant local values, use `python3 prepare.py "$PIXEL_IP" "$MAC_IP" --format rustdesk`. [RustDesk advanced settings](https://rustdesk.com/docs/en/self-host/client-configuration/advanced-settings/) · [RustDesk IP whitelisting](https://www.rustdesk.com/blog/rustdesk-and-remote-access-scams/)

## 5. Keep a working desktop available

In **System Settings → Energy**, prevent automatic sleep while the display is off. Keep the password requirement after display sleep and test locking the screen while the user remains logged in. Test the monitors' actual power-off behavior, since a display that disappears from macOS also disappears from the capture choices. The physical displays can show the remote operator's activity after unlocking. Arrange local recovery for logout or reboot, including a FileVault unlock when required. [Apple desktop sleep settings](https://support.apple.com/guide/mac-help/mchle41a6ccd/mac) · [Apple FileVault recovery](https://support.apple.com/guide/mac-help/mh35881/mac)

## Rollback

1. On the Mac, end active sessions, disable Direct IP, and remove the permanent password or stop RustDesk inbound service. If the phone is lost, remove its device from the tailnet and rotate any saved RustDesk password.
2. Remove the grant and its tests and aliases from the tailnet policy. Restore only the intended previous access after reviewing subsequent policy changes.
3. Remove the dedicated PF anchor and validate and reload the edited configuration locally through the same firewall workflow. Preserve independent firewall rules.
4. Restore any sleep or app settings changed for this setup. If retiring RustDesk, uninstall its helper and client and revoke its macOS privacy permissions.
