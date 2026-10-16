# Plan: Home Assistant controls over MQTT

Status: **draft for the owner's decisions** (§4). Written 2026-10-16 after 0.4.4.

## 1. Where it stands (0.4.4)

21 entities per gateway:
- **18 sensors**, all with values since 0.4.3 (#96).
- **Controls:**
  - an *Operating Mode* select (works);
  - three *Smart Circuit* switches. They accept on/off, but their **state is always unknown**: the poll never reads circuit state (1409).

There are no number entities (sliders), no buttons, and no limits.

The comparison of HA diagnostics from a live install (Direct 0.4.1 vs FWHAI 0.6.80 and Modbus Bridge 0.2.6
on the same aGate, 2026-10-16) shows what the other two bridges offer:

| Control | Modbus Bridge | FWHAI | Direct today | How the bridge could do it |
|---|---|---|---|---|
| Smart circuit on/off with state | — | switch, state works | switch, state **unknown** | read 1409 each poll, or after each command |
| Reserve SoC (per mode) | number 0–100 % | number 0–100 % | none | **local write is discarded by the aGate** (1405, see API_COMPARISON.md), so only via the cloud provider (`POST /api/cloud/reserve`) when credentials exist |
| Grid export/import limit | — | number 0–100 kW plus "unlimited" switches | none | `POST /api/grid/limits` exists. It is an **unverified** local write, so it needs `confirm` |
| Battery command / dispatch | select plus power, duration and target SoC | dispatch action/power/duration/target | none | `POST /api/dispatch` and `/api/battery/command` exist |
| Off-grid | — | select | none | `POST /api/offgrid` (consequential, needs `confirm`) |
| Run status text | — | — | raw number (`1`) | publish `run_status_desc`, which the poll already has |

## 2. Principles

- **Only writes verified on hardware become HA controls.** An HA control that silently does nothing
  is worse than no control (the existing rule in `publish/entities.py`).
- **A control's state must come from a read, not from the last command.** No control is published
  without a state source.
- An HA control has no confirm dialog. So **a consequential action (off-grid, dispatch, grid limits)
  is only exposed if the owner decides HA automations may do it unconfirmed.**
- New entities are additions, not identity changes. They can ship without the #92 migration, but
  **each release covers one functional area** (TEST_POLICY §1).

## 3. Releases, one area each, every one through G0–G3

| Release | Contents | Gates beyond G0/G1 |
|---|---|---|
| **C1** | Smart-circuit switch **state**: read 1409 in the poll's own session and publish `circuit_N_on`. Run status as text. | G2 read-only: show the switch state follows the app; measure the poll time added |
| **C2** | Reserve SoC numbers (one per mode), published **only when the cloud provider is configured**. State from the provider's read. | G2 write: plan, read back **and** the app showing the new value, restore the original |
| **C3** | Grid export/import limits: numbers in kW plus "unlimited" switches, if the owner allows unconfirmed writes from HA (§4) | G2 write: read-back, cloud witness, restore; outside 17:30–20:00 |
| **C4** | Battery command / dispatch (select plus power, duration, target), if the owner wants it in this bridge at all (§4) | G2 write: **measured** battery W against the command, revert timer, restore mode |
| — | Off-grid as an HA control | only if the owner decides (§4) |

All of them: Modbus off on the real aGate, read-only by default, real hardware only on the owner's
go-ahead in the session.

## 4. Decisions for the owner

1. **C3 and C4:** may Home Assistant automations change grid limits and dispatch the battery **without
   a confirm**? If not, those stay in the bridge UI only.
2. **C4 at all:** the Modbus Bridge already offers battery commands. Offer them here too, or leave them
   there to avoid two controllers on one aGate?
3. **Off-grid** as an HA control: yes or no?
4. **Order:** C1 → C2 → C3 → C4 as above?
