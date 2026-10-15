# Test and release policy: FranklinWH bridges

Applies to **franklinwh-direct-connect-bridge** and **franklinwh-modbus-bridge**: every change that
reaches a user as a Home Assistant add-on, a Docker image or a PyPI package.

Written 2026-10-16, after 0.3.3 and 0.4.0 of the Direct Connect bridge shipped to the add-on store
unable to add a gateway on a fresh install (#81). What went wrong:

- Three feature changes went into two releases within a day.
- No release was installed fresh on Home Assistant OS before it shipped.
- The roster tests stubbed the very function that failed (`db.get_store`), so the suite passed.
- Nothing recorded what the UI showed, what the browser logged or what the add-on logged, so
  there was no trace to compare against when users reported the failure.

The install and update lifecycle (fresh install, update, reinstall, uninstall, Docker, coexistence)
and its effect on HA devices, entities and retained MQTT topics is defined in
franklinwh-modbus-bridge `docs/install-lifecycle.md`. This policy says **what must be tested and
recorded**. That document says **which lifecycle paths exist and what each must do**. The G1 matrix below
runs that document's paths.

## 1. Release size

- **One release, one functional area.** Areas: store/migrations, poller, MQTT/HA identity, setup
  wizard/UI, HTTP API, Modbus, scheduler/dispatch, packaging.
- **A hotfix contains the fix and nothing else.** No feature rides along with a fix.
- **A release PR contains only the version bump and the CHANGELOG section.** The changes it releases
  were merged and gated before it.
- **Anything that changes how HA identifies things** (device identifiers, `unique_id`, entity naming,
  MQTT topics, add-on slug) is **released alone**. Its notes say exactly what users will see change.
- **No release on the same day as the previous one** unless it is a hotfix for that release.

## 2. Gates

Every change passes the gates its risk requires. A release passes all of them.

| Gate | What | Required for |
|---|---|---|
| **G0 Suite** | Full test suite green. Each fix has a regression test **seen failing without the fix**. A test must not stub the component it is testing; stub only its edges (network, device, clock). | every PR |
| **G1 HAOS acceptance** | Scripted run on the HAOS test VM, with a trace (§3). | every release; any PR touching setup, store, MQTT/HA identity, add-on config or packaging |
| **G2 Real hardware** | Reference aGate, under §4. | device I/O, dispatch, writes, Modbus, anything "critical" in CLAUDE.md |
| **G3 Sign-off** | Owner approves the release PR with the G1 summary (and G2 where needed) in its body. | every release |

A **failed or skipped gate is stated in the PR**. It is never left out.

## 3. G1: HAOS acceptance run

### Environment

- HAOS `generic-aarch64` under QEMU (`~/dev/haos-qemu`, `start.sh`), current stable HAOS.
- **Record the HAOS, Core and Supervisor versions in every run.**
- Mosquitto add-on installed, and the HA MQTT integration accepted.
- HA is served on guest **:80** in HAOS 18.x; guest :8123 only redirects. Forward :80.
- Bridges coexisting on one VM use distinct host ports; nothing listens on `127.0.0.1:8123`.

### Prove the build is the code under test

Installing from `repo#branch` builds whatever the Dockerfile builds. In franklinwh-modbus-bridge a pinned
`BRIDGE_REF` builds the last release tag instead (its #140). **Before judging a run, check that
`/api/live` (or `/api/version`) reports the version and source of the branch.** If it doesn't, the
run tested something else and does not count.

### Matrix (each a fresh run with its own trace)

1. **Fresh install, default options**, through the setup wizard's mock/demo path in a real browser.
2. **Update in place** from the previous release with a configured gateway: devices, entities and
   history survive with no orphans and no duplicates (see install-lifecycle.md).
3. **Reinstall keeping data** and **uninstall + purge**: the outcomes install-lifecycle.md specifies.
4. **Coexistence**: both bridges installed in one HA, with no clash of devices, entities or topics.

### The trace (every run, kept per run)

`results/runs/<UTC stamp>_<slug>_<version>/`:

- `summary.md` / `summary.json`: versions, pass/fail per check, notes
- `screenshots/`: **every wizard screen**, the add-on page, its Configuration tab with defaults, the
  ingress panel, the dashboard after setup, and the HA device page
- `addon.log`: the add-on log for the run
- `browser-console.log`: console errors/warnings and uncaught page errors
- `http-failures.log`: every request from the UI that answered ≥ 400 or failed
- `api/*.json`: the raw API answers the checks were judged on

### Pass criteria

- The wizard completes with **no error banner**.
- A gateway is added, polls, and appears in HA as one device whose entities are available.
- The setup checks are all true.
- **No ERROR or Traceback** in the add-on log, **no console errors**, **no failed UI calls**.

A failure that already exists in the previous release may be **accepted only if it is listed in the PR
with its open issue number**. Running the same matrix on the previous release gives the baseline. A
failure that is **new** compared with the baseline blocks the release.

### Evidence that may be published

The PR body carries `summary.md` and selected screenshots **from mock/demo runs only**. Real-hardware
runs stay local; quote masked output inline. No serials, LAN IPs or site data, per CLAUDE.md.

## 4. G2: Real-aGate access

- **Read-only by default.** Writes, mode changes and dispatch need the owner's go-ahead **in that
  session**. An approval relayed by another session does not count.
- **The aGate's Modbus :502 serves one client.** Never open :502 while another client (the Modbus
  bridge, another bridge's Modbus fallback) is polling it. A Direct Connect test **switches the
  bridge's Modbus path off before adding the real gateway**.
- When :502 is needed: coordinate, stop the other client, **verify the stop by counting sockets**,
  test, restart it, and record the downtime.
- Record which other clients were active (Direct Connect :9000 and Modbus :502) during the test.

## 5. Shared identity rules (both bridges in one Home Assistant)

Each bridge owns its own namespace. No identifier may be produced by both.

| | Direct Connect bridge (current) | Modbus bridge (v0.2.6, as reported by that repo's session, 2026-10-16) |
|---|---|---|
| Add-on slug | `franklinwh_local_bridge` (never rename) | `franklinwh_modbus_bridge` |
| Ports | 8101 | ingress 8099; direct port off by default |
| MQTT state prefix | `franklinwh-local/<node>/…` | `fwh_mb/<short_id>/…` (legacy installs: `franklinwh/…`); reserves `fwhai`, `fwh_ai`, `fwh_lb`, `franklinwh-local` |
| HA device `identifiers` | `franklinwh_<node>` (node = **full** serial, lower case) | `<prefix>_modbus_<SERIAL>`; before 0.2.4: `franklinwh_<SERIAL>` (upper case) |
| `unique_id` | `franklinwh_<node>_<key>` | `<prefix>_<short_id>_<slug>` (short_id = last 8 of the serial); legacy `franklinwh_<serial8>_<slug>` |
| Device name | `FranklinWH Direct <last 8 of serial>` | `FranklinWH Modbus <last 8 of serial>`; mocks `… (mock)` |

Known near-collision: the Direct Connect device identifier `franklinwh_<serial>` and the Modbus
bridge's pre-0.2.4 `franklinwh_<SERIAL>` differ **only by case**. If either side ever normalises case,
the two bridges' devices merge. The `unique_id`s do not collide today: ours uses the full serial and
theirs the last 8 characters.

HA 2026.10 does not use the published `object_id`: entity IDs are derived from the device name
(`sensor.franklinwh_direct_<serial8>_…`). **Renaming a device therefore changes the entity IDs of
new installs.**

- **Open question for both repos:** `franklinwh_<serial>` is a generic prefix. If the Modbus bridge also
  derives identifiers from `franklinwh_` + serial, the two would merge into one HA device. Each bridge
  should carry a bridge-specific prefix. Changing one is an identity change (§1): released alone, with a
  migration that leaves no orphans.
- Changing an identifier, a `unique_id` or the device naming is a **breaking change for HA history**.
  It needs a migration or a documented rename, and G1 matrix item 2.

## 6. Sign-off checklist (release PR)

- [ ] One functional area; the PR has only the version bump and CHANGELOG
- [ ] G0: suite count, plus the regression tests named
- [ ] G1: `summary.md` of every matrix run pasted, with baseline differences listed
- [ ] Build proven to be the branch (`/api/live` version and source)
- [ ] Known failures each linked to an open issue
- [ ] G2 done, or "not needed because …"
- [ ] No site data in the PR, the CHANGELOG or the commits
- [ ] Owner approval
