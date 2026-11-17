# Validation checklist

Run from a safe test desktop while someone can access the Mac locally. Record the date, versions, test outcome, and any recovery steps in `local/`.

| Check | Pass condition | Result |
| --- | --- | --- |
| Tailscale policy | The merged policy passes its accept and applicable deny assertions. | Pending |
| Home Wi-Fi | Pixel reaches the Mac's Tailscale IPv4 on TCP 21118 and signs in. | Pending |
| Mobile data | With phone Wi-Fi off, open a fresh Direct IP session via Tailscale. | Pending |
| Both displays | Switch from display 1 to display 2 and back. Verify image, pointer, clicks and keyboard on each using a scratch document. | Pending |
| Codex | View an active Codex session and reconnect without interrupting it. | Pending |
| Lock and reconnect | Lock the Mac, disconnect, and start a fresh session. Verify the lock screen and expected unlock behavior. | Pending |
| Displays off | Test display sleep and hardware power-off separately, then check whether both displays remain available. | Pending |
| Other tailnet device | An enrolled peer outside the grant cannot open TCP 21118 on the Mac's Tailscale IPv4 or IPv6. | Pending |
| LAN bypass | From another home-LAN device with Tailscale disconnected, TCP 21118 is unreachable at the Mac's LAN IPv4 and any reachable non-tailnet IPv6 address. | Pending |
| Internet exposure | Router rules do not publish TCP 21118, including over IPv6. From an owned off-LAN connection with Tailscale off, confirm there is no direct access to a public address of the Mac where applicable. | Pending |
| Public RustDesk ID | After restarting RustDesk on the Mac with isolation in place, a fresh stock client using the public RustDesk service cannot connect to the Mac's ID. The phone still connects by tailnet IP. | Pending |
| Reduced permissions | File transfer and clipboard synchronization are refused. Other disabled features are unavailable. | Pending |
| Service restarts | Restart RustDesk and reconnect. Then restart Tailscale and verify the tunnel interface, Direct IP, and LAN block again. | Pending |
| Reboot recovery | With local help available, verify the expected FileVault and login behavior, then reconnect and rerun the LAN block check. | Pending |

For network-level negative tests, use a short TCP connect attempt against only the Mac address under test. On a macOS test client, for example, use `nc -G 3 -vz ADDRESS 21118` with the relevant address. A RustDesk login rejection still means the TCP listener was reachable. Use a fresh connection after any policy or firewall change.

Distinguish a RustDesk ID test that fails to locate or connect to the Mac from one that reaches a password prompt or an application-level rejection. The latter means the public ID path still reaches the host. Inspect the installed client's connection status and RustDesk egress where available to corroborate the test. A successful tailnet Direct IP session alone only proves the private path works.

The setup is ready for unattended use once cellular access, both displays, and reconnect work, the access restrictions pass, and recovery requirements are understood. If the firewall, public ID, or other access restriction fails, turn off Direct IP and stop inbound RustDesk service until the restriction is fixed.
