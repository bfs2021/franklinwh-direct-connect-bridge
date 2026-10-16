# Scheduler parity: Modbus Bridge vs Direct Connect

The two bridges' schedulers, compared behaviour by behaviour, so they can be aligned.

| | Behaviours | Tested | Untested | Unclear |
|---|---|---|---|---|
| **Modbus Bridge** ([scheduler pages](https://david2069.github.io/franklinwh-modbus-bridge/user/scheduler/concepts/), test plan at its `main` f2e9134, PR #217) | 238 | 130 | 93 | 15 |
| **Direct Connect** ([Scheduler](../guide/scheduler/index.md), [test plan](scheduler-test-plan.md), 0.5.5) | 266 | 106 | 119 | 41 |

Of the Modbus Bridge's 238 behaviours, this bridge has **74 the same**, **121 that differ**
and is **missing 55**. It has **83 of its own** (Direct Connect only). 13 more rows compare
whole sections of the dependencies and examples pages, which carry no markers.

**How it was built.** Each row is one behaviour id. Ids are shared: where this bridge's page
documents the counterpart of a Modbus Bridge behaviour, it uses the same id, even when the
behaviour differs. *Has / tested* for the Modbus Bridge comes from its test plan; for this
bridge from the markers in the [Scheduler](../guide/scheduler/index.md) pages. The *gap* is a
short note written while reading both bridges' code. The Modbus Bridge's claims are taken
from its docs and were **not** re-verified against its code here; this bridge's side was read
from its code, and the less obvious defects were reproduced with a mock (no hardware).

| Column | Meaning |
|---|---|
| **#** | Behaviour id. "—" for a section-level comparison (no marker). |
| **Page · heading** | This bridge's page and the heading both bridges share. |
| **Modbus Bridge** / **Direct Connect** | `yes / tested`, `yes / untested`, `yes / unclear` or `no`. |
| **Gap** | **same**, **differs**, **missing here** (Modbus Bridge only) or **Direct Connect only**, then the difference. |
| **Issue** | The issue in this repository. Issues opened from this review are listed under [Issues filed from this review](#issues-filed-from-this-review). |

## Behaviours

| # | Page · heading | Modbus Bridge | Direct Connect | Gap | Issue |
|---|---|---|---|---|---|
| IDX-01 | [index](../guide/scheduler/index.md) · The entry list | yes / untested | yes / untested | **differs**: DC shows all by default |  |
| IDX-02 | [index](../guide/scheduler/index.md) · The entry list | yes / untested | yes / untested | **differs**: DC opens an unsaved 'Copy of' form, disabled |  |
| IDX-03 | [index](../guide/scheduler/index.md) · The entry list | yes / tested | yes / untested | **differs**: DC confirms but does not re-send a running force; change applies next window |  |
| IDX-04 | [index](../guide/scheduler/index.md) · Templates, export and import | yes / untested | yes / untested | **differs**: DC loads disabled, no enable prompt |  |
| IDX-05 | [index](../guide/scheduler/index.md) · Templates, export and import | yes / tested | yes / tested | same: DC also exports/imports its own franklinwh-local-schedules |  |
| IDX-06 | [index](../guide/scheduler/index.md) · Visual timeline | yes / tested | yes / tested | **differs**: DC: one list, interval/cron/always not drawn, not per gateway | [#161](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/161) |
| IDX-07 | [index](../guide/scheduler/index.md) · Visual timeline | yes / tested | yes / untested | **differs**: DC draws a one-off only on its date |  |
| IDX-08 | [index](../guide/scheduler/index.md) · The entry list | no | yes / tested | Direct Connect only: Turn on/off partial PUT merged (fixed 0.5.2) | [#157](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/157) |
| IDX-09 | [index](../guide/scheduler/index.md) · The entry list | no | yes / unclear | Direct Connect only: PUT without enabled re-enables | [#168](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/168) |
| IDX-10 | [index](../guide/scheduler/index.md) · Templates, export and import | no | yes / tested | Direct Connect only: eleven presets incl. four force presets (MB has four different templates) |  |
| IDX-11 | [index](../guide/scheduler/index.md) · Visual timeline | no | yes / untested | Direct Connect only: timeline ignores gateway and uses container clock | [#161](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/161) |
| IDX-12 | [index](../guide/scheduler/index.md) · Using schedules from Home Assistant (Direct Connect only) | no | yes / unclear | Direct Connect only: Pause/Resume API ineffective (does not hold a run, tick ignores paused) | [#200](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/200) |
| CON-01 | [concepts](../guide/scheduler/concepts.md) · The tick | yes / untested | yes / tested | same: DC cadence configurable 5-60 s |  |
| CON-02 | [concepts](../guide/scheduler/concepts.md) · The tick | yes / tested | yes / untested | **differs**: DC reads all by name; priority only in a same-tick contest |  |
| CON-03 | [concepts](../guide/scheduler/concepts.md) · The tick | yes / tested | yes / tested | same: none |  |
| CON-04 | [concepts](../guide/scheduler/concepts.md) · The tick | yes / tested | yes / tested | same: DC: per-resource claims (battery, grid, circuit) |  |
| CON-05 | [concepts](../guide/scheduler/concepts.md) · The tick | yes / untested | yes / untested | **differs**: DC waits for the next tick (<=15 s) |  |
| CON-06 | [concepts](../guide/scheduler/concepts.md) · The tick | yes / unclear | yes / untested | **differs**: DC has no module switch |  |
| CON-07 | [concepts](../guide/scheduler/concepts.md) · Legacy and v2 entries | yes / untested | no | **missing here**: DC has one format |  |
| CON-08 | [concepts](../guide/scheduler/concepts.md) · The tick | no | yes / tested | Direct Connect only: stale/disabled/never-polled gateway skipped (max(90 s, 3 polls)) |  |
| CON-09 | [concepts](../guide/scheduler/concepts.md) · Window, activation and run | no | yes / tested | Direct Connect only: stored occurrences: fire once per occurrence, retry while failed |  |
| CON-10 | [concepts](../guide/scheduler/concepts.md) · What the engine remembers | no | yes / untested | Direct Connect only: last fired occurrence, runs and dispatches survive restart |  |
| TRG-01 | [triggers](../guide/scheduler/triggers.md) · Fire-based triggers: the active window | yes / tested | yes / tested | same: none |  |
| TRG-02 | [triggers](../guide/scheduler/triggers.md) · Fire-based triggers: the active window | yes / untested | yes / untested | **differs**: DC: the one Fire at minute; force has no own timer, released at next tick after |  |
| TRG-03 | [triggers](../guide/scheduler/triggers.md) · Fire-based triggers: the active window | yes / tested | yes / untested | same: none |  |
| TRG-04 | [triggers](../guide/scheduler/triggers.md) · Recurring windows | yes / tested | yes / untested | same: untested in DC |  |
| TRG-05 | [triggers](../guide/scheduler/triggers.md) · Recurring windows | yes / tested | yes / tested | same: none |  |
| TRG-06 | [triggers](../guide/scheduler/triggers.md) · Recurring windows | yes / untested | yes / tested | **differs**: DC: each window is its own occurrence (fires once per window) |  |
| TRG-07 | [triggers](../guide/scheduler/triggers.md) · Recurring windows | yes / tested | yes / untested | same: DC: end <= start wraps |  |
| TRG-08 | [triggers](../guide/scheduler/triggers.md) · Recurring windows | yes / untested | yes / untested | **differs**: DC attributes the after-midnight part to the day it opened |  |
| TRG-09 | [triggers](../guide/scheduler/triggers.md) · Recurring windows | yes / tested | yes / unclear | **differs**: DC: start == end is a 24-hour window | [#198](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/198) |
| TRG-10 | [triggers](../guide/scheduler/triggers.md) · Recurring windows | yes / untested | yes / untested | **differs**: DC: 24:00 = end of day; unparsable window dropped, empty list falls back to fire_at |  |
| TRG-11 | [triggers](../guide/scheduler/triggers.md) · One-off date window | yes / tested | yes / tested | **differs**: DC: stored days still restrict; form shows windows that are ignored |  |
| TRG-12 | [triggers](../guide/scheduler/triggers.md) · One-off date window | yes / tested | yes / tested | same: DC card has no 'passed' label |  |
| TRG-13 | [triggers](../guide/scheduler/triggers.md) · One-off date window | yes / untested | yes / untested | **differs**: DC runs past midnight into the next date |  |
| TRG-14 | [triggers](../guide/scheduler/triggers.md) · Daily at time | yes / tested | yes / tested | same: none |  |
| TRG-15 | [triggers](../guide/scheduler/triggers.md) · Daily at time | yes / untested | yes / untested | same: form max 1440 |  |
| TRG-16 | [triggers](../guide/scheduler/triggers.md) · Weekly at time | yes / tested | yes / tested | **differs**: DC: no days = every day |  |
| TRG-17 | [triggers](../guide/scheduler/triggers.md) · Every N minutes | yes / tested | yes / tested | same: none |  |
| TRG-18 | [triggers](../guide/scheduler/triggers.md) · Every N minutes | yes / untested | yes / untested | same: untested in DC |  |
| TRG-19 | [triggers](../guide/scheduler/triggers.md) · Every N minutes | yes / untested | yes / unclear | **differs**: DC next_fire disagrees with the window | [#208](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/208) |
| TRG-20 | [triggers](../guide/scheduler/triggers.md) · Every N minutes | yes / tested | yes / untested | same: none |  |
| TRG-21 | [triggers](../guide/scheduler/triggers.md) · Monthly / calendar | yes / tested | yes / tested | same: none |  |
| TRG-22 | [triggers](../guide/scheduler/triggers.md) · Monthly / calendar | yes / tested | yes / untested | **differs**: DC does not validate; day 0/None = no restriction |  |
| TRG-23 | [triggers](../guide/scheduler/triggers.md) · Monthly / calendar | yes / untested | yes / untested | **differs**: DC: no day of month = fires every day | [#198](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/198) |
| TRG-24 | [triggers](../guide/scheduler/triggers.md) · Custom cron | yes / tested | yes / untested | **differs**: DC accepts it; never fires |  |
| TRG-25 | [triggers](../guide/scheduler/triggers.md) · Custom cron | yes / untested | yes / untested | same: untested in DC |  |
| TRG-26 | [triggers](../guide/scheduler/triggers.md) · Custom cron | yes / tested | yes / tested | same: none |  |
| TRG-27 | [triggers](../guide/scheduler/triggers.md) · Always evaluate | yes / tested | yes / tested | **differs**: DC: window = conditions; fires on rising edge |  |
| TRG-28 | [triggers](../guide/scheduler/triggers.md) · Always evaluate | yes / untested | yes / unclear | **differs**: DC: once EVER (stored occurrence, survives restart); falling edges still release | [#190](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/190) |
| TRG-29 | [triggers](../guide/scheduler/triggers.md) · Always evaluate | yes / unclear | yes / unclear | **differs**: DC: stored occurrence row, never pruned | [#190](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/190) |
| TRG-30 | [triggers](../guide/scheduler/triggers.md) · Always evaluate | yes / untested | yes / tested | **differs**: DC does release on the falling edge |  |
| TRG-31 | [triggers](../guide/scheduler/triggers.md) · Quick presets | yes / untested | yes / untested | same: DC preset list differs |  |
| TRG-32 | [triggers](../guide/scheduler/triggers.md) · Next fire | yes / tested | yes / tested | **differs**: DC searches 366 days; container clock | [#161](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/161) |
| TRG-33 | [triggers](../guide/scheduler/triggers.md) · Next fire | yes / untested | yes / tested | **differs**: DC: inside window AND fired this occurrence |  |
| TRG-34 | [triggers](../guide/scheduler/triggers.md) · Editing a trigger in the form | yes / untested | yes / unclear | **differs**: DC: hidden duration_min (default 90) also limits a scheduled force | [#160](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/160) |
| TRG-35 | [triggers](../guide/scheduler/triggers.md) · Editing a trigger in the form | yes / untested | no | **missing here**: DC has no API oneoff type |  |
| TRG-36 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / tested | no | **missing here**: DC: stale gateway skipped; no outage record | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TRG-37 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / tested | no | **missing here**: no catch-up | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TRG-38 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / tested | no | **missing here**: no catch-up | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TRG-39 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / tested | no | **missing here**: no catch-up | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TRG-40 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / tested | yes / tested | **differs**: DC: claimed runs whose window ended >120 s ago marked missed |  |
| TRG-41 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / untested | yes / untested | **differs**: DC: an unclaimed window leaves no missed row |  |
| TRG-42 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / untested | no | **missing here**: no missed policy | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TRG-43 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / tested | no | **missing here**: no late fire | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TRG-44 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / untested | no | **missing here**: no late fire | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TRG-45 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / untested | no | **missing here**: no late fire | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TRG-46 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / untested | no | **missing here**: no late fire | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TRG-47 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / untested | no | **missing here**: no catch-up | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TRG-48 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | yes / untested | no | **missing here**: no missed policy | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TRG-49 | [triggers](../guide/scheduler/triggers.md) · Summary | no | yes / untested | Direct Connect only: calendar restrictions apply to every trigger type |  |
| TRG-50 | [triggers](../guide/scheduler/triggers.md) · Recurring windows | no | yes / tested | Direct Connect only: start/end date range restriction with a reason |  |
| TRG-51 | [triggers](../guide/scheduler/triggers.md) · One-off date window | no | yes / unclear | Direct Connect only: One-off ignores its Time windows; no date = every day | [#198](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/198) |
| TRG-52 | [triggers](../guide/scheduler/triggers.md) · Next fire | no | yes / unclear | Direct Connect only: next_fire/active_now on container clock | [#161](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/161) |
| TRG-53 | [triggers](../guide/scheduler/triggers.md) · Editing a trigger in the form | no | yes / untested | Direct Connect only: trigger type change seeds defaults |  |
| TRG-54 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | no | yes / untested | Direct Connect only: no late fire ever | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TRG-55 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | no | yes / tested | Direct Connect only: stale snapshot skips evaluation |  |
| TRG-56 | [triggers](../guide/scheduler/triggers.md) · After an outage or a restart (catch-up) | no | yes / tested | Direct Connect only: older open runs coalesced |  |
| CND-01 | [conditions](../guide/scheduler/conditions.md) · Rules for every condition | yes / tested | yes / tested | same: none |  |
| CND-02 | [conditions](../guide/scheduler/conditions.md) · Rules for every condition | yes / tested | yes / untested | **differs**: import does not warn about unknown sensors | [#202](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/202) |
| CND-03 | [conditions](../guide/scheduler/conditions.md) · Rules for every condition | yes / tested | yes / untested | **differs**: same idea, but every gateway tick also fetches each HA instance's whole /api/states |  |
| CND-04 | [conditions](../guide/scheduler/conditions.md) · Rules for every condition | yes / untested | yes / untested | same: none; on/off sensors are stored as int 1/0 |  |
| CND-05 | [conditions](../guide/scheduler/conditions.md) · Operators | yes / tested | yes / tested | same: none |  |
| CND-06 | [conditions](../guide/scheduler/conditions.md) · Operators | yes / tested | yes / untested | **differs**: DC compares text case-insensitively; untested |  |
| CND-07 | [conditions](../guide/scheduler/conditions.md) · Operators | yes / tested | yes / untested | same: untested here |  |
| CND-08 | [conditions](../guide/scheduler/conditions.md) · Operators | yes / tested | yes / untested | **differs**: brackets not stripped; untested here |  |
| CND-09 | [conditions](../guide/scheduler/conditions.md) · Operators | yes / tested | yes / untested | same: untested here |  |
| CND-10 | [conditions](../guide/scheduler/conditions.md) · Operators | yes / tested | yes / untested | same: untested here |  |
| CND-11 | [conditions](../guide/scheduler/conditions.md) · Operators | yes / tested | yes / untested | same: untested here |  |
| CND-12 | [conditions](../guide/scheduler/conditions.md) · Operators | yes / tested | yes / untested | same: untested here |  |
| CND-13 | [conditions](../guide/scheduler/conditions.md) · Value and Lookup | yes / untested | yes / untested | same: none |  |
| CND-14 | [conditions](../guide/scheduler/conditions.md) · Value and Lookup | yes / tested | yes / untested | same: untested here |  |
| CND-15 | [conditions](../guide/scheduler/conditions.md) · Value and Lookup | yes / untested | yes / untested | **differs**: Explain prints the Lookup label; Test against live prints an empty RHS |  |
| CND-16 | [conditions](../guide/scheduler/conditions.md) · Groups and items: ALL / ANY | yes / tested | yes / tested | same: empty top-level block is true even with match any |  |
| CND-17 | [conditions](../guide/scheduler/conditions.md) · Groups and items: ALL / ANY | yes / tested | yes / tested | same: none |  |
| CND-18 | [conditions](../guide/scheduler/conditions.md) · Groups and items: ALL / ANY | yes / tested | yes / untested | same: untested here |  |
| CND-19 | [conditions](../guide/scheduler/conditions.md) · Groups and items: ALL / ANY | yes / untested | yes / untested | **differs**: empty block saved as [] (same effect) |  |
| CND-20 | [conditions](../guide/scheduler/conditions.md) · Groups and items: ALL / ANY | yes / untested | yes / untested | **differs**: an empty ALL exit group blocks the schedule from starting (exit condition already holds) |  |
| CND-21 | [conditions](../guide/scheduler/conditions.md) · Scope: which gateway's values | yes / untested | yes / untested | same: applies to gateway_scope all; untested |  |
| CND-22 | [conditions](../guide/scheduler/conditions.md) · Scope: which gateway's values | yes / untested | yes / tested | **differs**: DC measures each gateway against its own meter (better) |  |
| CND-23 | [conditions](../guide/scheduler/conditions.md) · Hold for (dwell) | yes / tested | yes / untested | same: untested here |  |
| CND-24 | [conditions](../guide/scheduler/conditions.md) · Hold for (dwell) | yes / tested | yes / untested | same: untested here |  |
| CND-25 | [conditions](../guide/scheduler/conditions.md) · Hold for (dwell) | yes / untested | yes / untested | same: none |  |
| CND-26 | [conditions](../guide/scheduler/conditions.md) · Hold for (dwell) | yes / tested | yes / untested | **differs**: no maximum; untested here |  |
| CND-27 | [conditions](../guide/scheduler/conditions.md) · Hold for (dwell) | yes / untested | yes / untested | **differs**: a retry waits the whole hold again | [#203](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/203) |
| CND-28 | [conditions](../guide/scheduler/conditions.md) · When conditions are evaluated | yes / tested | yes / untested | same: none |  |
| CND-29 | [conditions](../guide/scheduler/conditions.md) · When conditions are evaluated | yes / tested | yes / untested | **differs**: once per calendar day per gateway, up to two leaves; untested |  |
| CND-30 | [conditions](../guide/scheduler/conditions.md) · Test Verification | yes / tested | yes / tested | **differs**: editor Test uses the top-bar gateway, not the schedule's |  |
| CND-31 | [conditions](../guide/scheduler/conditions.md) · Test Verification | yes / untested | yes / unclear | **differs**: Test against live reads the default gateway and container clock, top-level rows only, no exit/hold/conflict check | [#161](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/161) |
| CND-32 | [conditions](../guide/scheduler/conditions.md) · Test Verification | yes / untested | yes / untested | **differs**: no login on this bridge's HTTP API |  |
| CND-33 | [conditions](../guide/scheduler/conditions.md) · Home Assistant entities | yes / tested | yes / tested | same: since 0.5.4 unavailable/unknown are no reading, as in the Modbus Bridge; before 0.5.4 they read 0 | [#167](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/167) (fixed in 0.5.4) |
| CND-34 | [conditions](../guide/scheduler/conditions.md) · Home Assistant entities | yes / tested | yes / tested | **differs**: REST /api/states (whole list) every tick of every gateway; no WebSocket |  |
| CND-35 | [conditions](../guide/scheduler/conditions.md) · Home Assistant entities | yes / tested | yes / untested | **differs**: no such warning | [#202](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/202) |
| CND-36 | [conditions](../guide/scheduler/conditions.md) · Conditions (intro) | no | yes / untested | Direct Connect only: DC evaluates exit conditions for every action kind while the window is open |  |
| CND-37 | [conditions](../guide/scheduler/conditions.md) · Home Assistant entities | no | yes / tested | Direct Connect only: DC auto-scales $/kWh to c/kWh (tested) |  |
| SEN-01 | [conditions](../guide/scheduler/conditions.md) · Notes on some sensors | yes / tested | no | **missing here**: no time.* sensors; use calendar restrictions | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| SEN-02 | [conditions](../guide/scheduler/conditions.md) · Notes on some sensors | yes / tested | no | **missing here**: no time.* sensors | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| SEN-03 | [conditions](../guide/scheduler/conditions.md) · Notes on some sensors | yes / tested | yes / tested | same: none |  |
| SEN-04 | [conditions](../guide/scheduler/conditions.md) · Grid | yes / tested | yes / tested | **differs**: DC derives it from grid power != 0, so it reads 0 at exactly 0 W while on grid | [#206](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/206) |
| SEN-05 | [conditions](../guide/scheduler/conditions.md) · Battery | yes / tested | no | **missing here**: no reserve sensors |  |
| SEN-06 | [conditions](../guide/scheduler/conditions.md) · Notes on some sensors | yes / tested | yes / tested | same: capacity is a user constant (no local capacity register); rate falls back to a constant |  |
| SEN-07 | [conditions](../guide/scheduler/conditions.md) · Constants | yes / tested | yes / tested | same: DC adds default operating mode; capacity/max power not in the picker |  |
| SEN-08 | [conditions](../guide/scheduler/conditions.md) · Tariff | yes / tested | yes / tested | **differs**: from the gateway's meter; None when undefined (fails closed) |  |
| SEN-09 | [conditions](../guide/scheduler/conditions.md) · Tariff | yes / tested | yes / untested | same: untested here |  |
| SEN-10 | [conditions](../guide/scheduler/conditions.md) · Tariff | yes / tested | yes / tested | **differs**: last good NEM price kept however old | [#207](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/207) |
| SEN-11 | [conditions](../guide/scheduler/conditions.md) · Utility Plan | yes / tested | yes / tested | same: none |  |
| SEN-12 | [conditions](../guide/scheduler/conditions.md) · Utility Plan | yes / tested | no | **missing here**: no such sensor |  |
| SEN-13 | [conditions](../guide/scheduler/conditions.md) · Weather | yes / tested | yes / untested | same: untested here; weather.code not in the picker |  |
| SEN-14 | [conditions](../guide/scheduler/conditions.md) · Gateway identity | yes / untested | no | **missing here**: no gateway.* sensors; system.* describe the install |  |
| SEN-15 | [conditions](../guide/scheduler/conditions.md) · Other | yes / tested | no | **missing here**: no dispatch.* sensors |  |
| SEN-16 | [conditions](../guide/scheduler/conditions.md) · Other | yes / unclear | no | **missing here**: no dispatch.* sensors |  |
| SEN-17 | [conditions](../guide/scheduler/conditions.md) · Energy | yes / tested | no | **missing here**: only billing-period import/export cost sensors |  |
| SEN-18 | [conditions](../guide/scheduler/conditions.md) · Every sensor in the picker | no | yes / tested | Direct Connect only: different groups (Gateway, Derived Battery, …, one per HA instance) |  |
| SEN-19 | [conditions](../guide/scheduler/conditions.md) · Tariff | no | yes / untested | Direct Connect only: DC keeps the last good NEM price with no age limit | [#207](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/207) |
| ACT-01 | [actions](../guide/scheduler/actions.md) · Summary | yes / untested | yes / tested | same: none |  |
| ACT-02 | [actions](../guide/scheduler/actions.md) · Summary | yes / untested | yes / untested | **differs**: DC validates no action at save; failures appear only at run | [#202](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/202) |
| ACT-03 | [actions](../guide/scheduler/actions.md) · Power and sizing | yes / tested | yes / untested | **differs**: DC sizes pct against the 702 rating or a 5000 W fallback; no trusted rating |  |
| ACT-04 | [actions](../guide/scheduler/actions.md) · Power and sizing | yes / tested | yes / unclear | **differs**: DC empty power = 0 W; form seeds 100 % | [#209](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/209) |
| ACT-05 | [actions](../guide/scheduler/actions.md) · Power and sizing | yes / untested | yes / untested | **differs**: DC offers % and kW in the form, W via API |  |
| ACT-06 | [actions](../guide/scheduler/actions.md) · Power and sizing | yes / untested | no | **missing here**: DC has no params validation at all (see ACT-02) |  |
| ACT-07 | [actions](../guide/scheduler/actions.md) · Power and sizing | yes / tested | no | **missing here**: no legacy format here |  |
| ACT-08 | [actions](../guide/scheduler/actions.md) · Power and sizing | yes / untested | no | **missing here**: n/a |  |
| ACT-09 | [actions](../guide/scheduler/actions.md) · Power and sizing | yes / untested | no | **missing here**: n/a |  |
| ACT-10 | [actions](../guide/scheduler/actions.md) · Power and sizing | yes / unclear | yes / unclear | **differs**: DC does not cap W/kW (library behaviour unverified) |  |
| ACT-11 | [actions](../guide/scheduler/actions.md) · Power and sizing | yes / tested | no | **missing here**: no trust model | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| ACT-12 | [actions](../guide/scheduler/actions.md) · Power and sizing | yes / tested | no | **missing here**: DC refuses only when the Modbus client is not ready (ACT-30) | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| ACT-13 | [actions](../guide/scheduler/actions.md) · Power and sizing | yes / tested | yes / unclear | **differs**: DC classifies a capability refusal as OK: logged fired, not retried | [#191](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/191) |
| ACT-14 | [actions](../guide/scheduler/actions.md) · What is written | yes / tested | yes / untested | **differs**: DC sends one BatteryCommand via the library and trusts its return; no read-back |  |
| ACT-15 | [actions](../guide/scheduler/actions.md) · What is written | yes / untested | yes / untested | **differs**: DC: bridge watchdog releases; hardware timer called cosmetic in a code comment (unverified) |  |
| ACT-16 | [actions](../guide/scheduler/actions.md) · What is written | yes / unclear | no | **missing here**: no staging in the scheduler path |  |
| ACT-17 | [actions](../guide/scheduler/actions.md) · Parameters you can set only through the API | yes / tested | yes / untested | **differs**: DC time limit is always duration_min x 60; hidden 90 min in Recurring windows | [#160](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/160) |
| ACT-18 | [actions](../guide/scheduler/actions.md) · Parameters you can set only through the API | yes / untested | yes / untested | **differs**: DC target SoC is in the form; checked every 5 s from the poller |  |
| ACT-19 | [actions](../guide/scheduler/actions.md) · Parameters you can set only through the API | yes / untested | yes / untested | **differs**: DC form keeps the whole action object |  |
| ACT-20 | [actions](../guide/scheduler/actions.md) · Battery actions: Force Standby | yes / tested | yes / untested | same: DC still needs a ready Modbus client (this bridge) |  |
| ACT-21 | [actions](../guide/scheduler/actions.md) · Battery actions: Release | yes / untested | no | **missing here**: no Release action | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| ACT-22 | [actions](../guide/scheduler/actions.md) · Non-battery actions: Reserve and Operating Mode | yes / tested | yes / tested | same: DC picker tou/self/backup from gateway work modes |  |
| ACT-23 | [actions](../guide/scheduler/actions.md) · Non-battery actions: Reserve and Operating Mode | yes / untested | yes / untested | **differs**: DC checks nothing; missing mode fails at run |  |
| ACT-24 | [actions](../guide/scheduler/actions.md) · Non-battery actions: Reserve and Operating Mode | yes / untested | yes / unclear | same: DC also logs a rejected mode or off-grid write as fired | [#191](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/191) |
| ACT-25 | [actions](../guide/scheduler/actions.md) · Non-battery actions: Reserve and Operating Mode | yes / tested | no | **missing here**: no write-lock tracking |  |
| ACT-26 | [actions](../guide/scheduler/actions.md) · Non-battery actions: Reserve and Operating Mode | yes / untested | yes / untested | same: DC: If busy is force-only; same-tick priority still applies |  |
| ACT-27 | [actions](../guide/scheduler/actions.md) · No battery action (HA only) | yes / tested | yes / tested | same: none |  |
| ACT-28 | [actions](../guide/scheduler/actions.md) · No battery action (HA only) | yes / untested | yes / untested | **differs**: DC Run now runs the fire-phase HA actions |  |
| ACT-29 | [actions](../guide/scheduler/actions.md) · Summary | no | yes / tested | Direct Connect only: Unknown action kind at run is skipped and logged fired |  |
| ACT-30 | [actions](../guide/scheduler/actions.md) · Battery actions: Force Charge and Force Discharge | no | yes / untested | Direct Connect only: Force refused unless a SunSpec read through the Modbus client (this bridge) succeeds |  |
| ACT-31 | [actions](../guide/scheduler/actions.md) · Battery actions: Force Charge and Force Discharge | no | yes / tested | Direct Connect only: No host: force skipped |  |
| ACT-32 | [actions](../guide/scheduler/actions.md) · Non-battery actions: Reserve and Operating Mode | no | yes / tested | Direct Connect only: reserve_soc always skipped, logged fired | [#129](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/129) |
| ACT-33 | [actions](../guide/scheduler/actions.md) · Smart circuits, off-grid and notify (Direct Connect only) | no | yes / tested | Direct Connect only: Smart circuit write with read-back; NOT confirmed retried |  |
| ACT-34 | [actions](../guide/scheduler/actions.md) · Smart circuits, off-grid and notify (Direct Connect only) | no | yes / tested | Direct Connect only: On/Off read strictly since 0.5.5; before it, Off ran as on | [#188](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/188) (fixed in 0.5.5) |
| ACT-35 | [actions](../guide/scheduler/actions.md) · Smart circuits, off-grid and notify (Direct Connect only) | no | yes / untested | Direct Connect only: Off-grid action with SoC, no confirm |  |
| ACT-37 | [actions](../guide/scheduler/actions.md) · Summary | no | yes / tested | Direct Connect only: smart_circuit_schedule listed unavailable with reason |  |
| ACT-38 | [actions](../guide/scheduler/actions.md) · Battery actions: Force Charge and Force Discharge | no | yes / untested | Direct Connect only: Force disabled in the form with the reason when the Modbus client (this bridge) is unavailable |  |
| ACT-39 | [actions](../guide/scheduler/actions.md) · What is written | no | yes / unclear | Direct Connect only: One in-memory force for the whole bridge; a second gateway's force drops the first's watchdog | [#194](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/194) |
| ACT-40 | [actions](../guide/scheduler/actions.md) · What is written | no | yes / untested | Direct Connect only: Up to 5 attempts with sleeps inside one tick; blocks all gateways | [#197](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/197) |
| ACT-41 | [actions](../guide/scheduler/actions.md) · What is written | no | yes / unclear | Direct Connect only: UNKNOWN verdict unreachable for scheduler actions | [#201](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/201) |
| ACT-42 | [actions](../guide/scheduler/actions.md) · What is written | no | yes / unclear | Direct Connect only: Retry deadline falls to 1 s for Always and zero-duration windows | [#209](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/209) |
| HAA-01 | [actions](../guide/scheduler/actions.md) · Home Assistant actions | yes / untested | yes / tested | **differs**: DC saves anything; skips with a reason at run | [#202](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/202) |
| HAA-02 | [actions](../guide/scheduler/actions.md) · Home Assistant actions | yes / untested | yes / untested | **differs**: DC form saves incomplete rows |  |
| HAA-03 | [actions](../guide/scheduler/actions.md) · When they run | yes / tested | yes / untested | same: DC: after the battery action whatever its result (HAA-07) |  |
| HAA-04 | [actions](../guide/scheduler/actions.md) · When they run | yes / tested | yes / untested | same: none |  |
| HAA-05 | [actions](../guide/scheduler/actions.md) · When they run | yes / tested | yes / untested | same: none |  |
| HAA-06 | [actions](../guide/scheduler/actions.md) · When they run | yes / tested | yes / unclear | **differs**: DC: at every closing edge of the window, even if never fired; not on Stop or an in-window end | [#189](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/189) |
| HAA-07 | [actions](../guide/scheduler/actions.md) · When they run | yes / untested | yes / unclear | **differs**: DC runs them on every attempt | [#203](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/203) |
| HAA-08 | [actions](../guide/scheduler/actions.md) · Guards | yes / tested | yes / untested | **differs**: DC skips silently, no log; API also accepts a tree |  |
| HAA-09 | [actions](../guide/scheduler/actions.md) · Placeholders in notifications | yes / tested | yes / tested | same: DC prints numbers as stored (no .0 trimming) |  |
| HAA-10 | [actions](../guide/scheduler/actions.md) · Placeholders in notifications | yes / untested | yes / untested | **differs**: DC: dotted ids work, ha: ids do not | [#169](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/169) |
| HAA-11 | [actions](../guide/scheduler/actions.md) · Failure alerts | yes / tested | no | **missing here**: no failure notifications | [#172](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/172) |
| HAA-12 | [actions](../guide/scheduler/actions.md) · What is logged | yes / tested | yes / untested | **differs**: DC folds results into the fired/exit/manual row; failures rarely fail the run |  |
| HAA-13 | [actions](../guide/scheduler/actions.md) · Failure alerts | no | yes / untested | Direct Connect only: run_action_outcome called without notifier | [#172](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/172) |
| HAA-14 | [actions](../guide/scheduler/actions.md) · Placeholders in notifications | no | yes / tested | Direct Connect only: Placeholders also in service entity_id and data |  |
| HAA-15 | [actions](../guide/scheduler/actions.md) · Home Assistant actions | no | yes / tested | Direct Connect only: Raw service with bad JSON is skipped with the reason |  |
| HAA-16 | [actions](../guide/scheduler/actions.md) · Home Assistant actions | no | yes / tested | Direct Connect only: Guided entity action calls domain.service with entity and data |  |
| HAA-17 | [actions](../guide/scheduler/actions.md) · Placeholders in notifications | no | yes / tested | Direct Connect only: %run.*%, %schedule.*%, %gateway.id% variables |  |
| HAA-18 | [actions](../guide/scheduler/actions.md) · Home Assistant actions | no | yes / untested | Direct Connect only: Notify as a battery action kind |  |
| TGT-01 | [targets](../guide/scheduler/targets.md) · Pick a target | yes / untested | yes / tested | **differs**: DC: bound schedule only on its gateway's tick; not evaluated while stale/disabled |  |
| TGT-02 | [targets](../guide/scheduler/targets.md) · Pick a target | yes / untested | yes / untested | **differs**: DC: API-only gateway_scope all; no Site target in the form | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TGT-03 | [targets](../guide/scheduler/targets.md) · Pick a target | yes / untested | no | **missing here**: no utility-service target | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| TGT-04 | [targets](../guide/scheduler/targets.md) · How a fan-out works | yes / tested | yes / tested | same: DC: occurrence and resource claim per gateway |  |
| TGT-05 | [targets](../guide/scheduler/targets.md) · How a fan-out works | yes / tested | yes / untested | same: DC: per gateway:entry; but see TGT-20 and ACT-39 |  |
| TGT-06 | [targets](../guide/scheduler/targets.md) · How a fan-out works | yes / tested | yes / untested | **differs**: History rows do not name the gateway | [#205](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/205) |
| TGT-07 | [targets](../guide/scheduler/targets.md) · How a fan-out works | yes / untested | yes / unclear | same: DC: a stale/disabled gateway gets no window-end release either |  |
| TGT-08 | [targets](../guide/scheduler/targets.md) · How a fan-out works | yes / untested | yes / tested | same: DC: stale/disabled gateway skipped with a debug log only |  |
| TGT-09 | [targets](../guide/scheduler/targets.md) · How a fan-out works | yes / untested | yes / unclear | **differs**: DC Run now: one gateway, and the top-bar gateway overrides the bound one | [#193](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/193) |
| TGT-10 | [targets](../guide/scheduler/targets.md) · Entries with no target id | yes / untested | yes / untested | **differs**: DC unbound = first-registered gateway, unstored | [#182](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/182) |
| TGT-11 | [targets](../guide/scheduler/targets.md) · Entries with no target id | yes / unclear | yes / untested | **differs**: DC: unbound claims the tick gateway, same group as bound |  |
| TGT-12 | [targets](../guide/scheduler/targets.md) · In the form | yes / unclear | no | **missing here**: no service select |  |
| TGT-13 | [targets](../guide/scheduler/targets.md) · In the form | yes / untested | no | **missing here**: no mock warning in the form |  |
| TGT-14 | [targets](../guide/scheduler/targets.md) · In the form | yes / tested | yes / tested | same: none |  |
| TGT-15 | [targets](../guide/scheduler/targets.md) · On the timeline | yes / untested | yes / untested | **differs**: DC timeline ignores gateway; one list | [#161](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/161) |
| TGT-16 | [targets](../guide/scheduler/targets.md) · How a fan-out works | yes / unclear | no | **missing here**: n/a; see TGT-07 |  |
| TGT-17 | [targets](../guide/scheduler/targets.md) · Entries with no target id | no | yes / unclear | Direct Connect only: Disabled first gateway: unbound schedules run nowhere | [#182](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/182) |
| TGT-18 | [targets](../guide/scheduler/targets.md) · In the form | no | yes / tested | Direct Connect only: Mock gateways skip the 702 ratings read |  |
| TGT-19 | [targets](../guide/scheduler/targets.md) · In the form | no | yes / untested | Direct Connect only: Test against live always uses the default gateway |  |
| TGT-20 | [targets](../guide/scheduler/targets.md) · How a fan-out works | no | yes / unclear | Direct Connect only: Stop, Pause, shutdown and boot reconcile use the default gateway's host | [#192](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/192) |
| TGT-21 | [targets](../guide/scheduler/targets.md) · Pick a target | no | yes / untested | Direct Connect only: Gateway select only with >1 gateway; Default gateway = empty id |  |
| TGT-22 | [targets](../guide/scheduler/targets.md) · Pick a target | no | yes / untested | Direct Connect only: Schedule bound to an unknown gateway id never runs, silently |  |
| TGT-23 | [targets](../guide/scheduler/targets.md) · Pick a target | no | yes / tested | Direct Connect only: gateway_scope survives a form save (#157 fix) | [#157](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/157) |
| EXT-01 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · How a run ends | yes / tested | yes / tested | **differs**: DC releases at every force entry's window close, owned or not; logged exit 'window closed' | [#189](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/189) |
| EXT-02 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · How a run ends | yes / tested | yes / tested | same: none; DC marks the occurrence fired |  |
| EXT-03 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · How a run ends | yes / tested | yes / tested | **differs**: DC uses per-occurrence keys instead of clearing a mark |  |
| EXT-04 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · How a run ends | yes / tested | yes / untested | **differs**: DC: disable releases on next tick; delete does not release | [#195](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/195) |
| EXT-05 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · How a run ends | yes / unclear | yes / unclear | **differs**: DC never hands over; it always releases, even another's force | [#189](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/189) |
| EXT-06 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · How a run ends | yes / unclear | no | **missing here**: no ownership hand-over in DC |  |
| EXT-07 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Exit conditions | yes / tested | yes / tested | **differs**: DC does not start when exit already holds |  |
| EXT-08 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Exit conditions | yes / tested | yes / tested | same: none (DC plain release) |  |
| EXT-09 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Exit conditions | yes / untested | yes / untested | **differs**: DC evaluates exit for every action kind while the window is open |  |
| EXT-10 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Exit conditions | yes / untested | yes / tested | **differs**: DC detail names no rows |  |
| EXT-11 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Release policy | yes / tested | no | **missing here**: no release policies; always plain release | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| EXT-12 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Release policy | yes / tested | yes / untested | **differs**: DC restore_on_exit (API only) writes the captured mode back, set_mode schedules only; end-to-end untested | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| EXT-13 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Release policy | yes / tested | no | **missing here**: not in DC | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| EXT-14 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Release policy | yes / tested | no | **missing here**: no policies; DC Stop never restores | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| EXT-15 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Release policy | yes / untested | no | **missing here**: no field |  |
| EXT-16 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Release policy | yes / untested | no | **missing here**: no such migration |  |
| EXT-17 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · What a release does on the gateway | yes / tested | yes / untested | **differs**: DC release has no read-back; refused when Modbus client off | [#174](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/174) |
| EXT-18 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Hold instead of release (API only) | yes / tested | no | **missing here**: no hold | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| EXT-19 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Hold instead of release (API only) | yes / unclear | no | **missing here**: no hold |  |
| EXT-20 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Bridge shutdown | yes / untested | yes / unclear | **differs**: DC releases the in-memory force to the first gateway's host, not the force's host | [#192](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/192) |
| EXT-21 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · How a run ends | no | yes / unclear | Direct Connect only: DC: deleting a running schedule does not release its force | [#195](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/195) |
| EXT-22 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Exit conditions | no | yes / tested | Direct Connect only: nested exit groups (MB also supports; tested here) |  |
| EXT-24 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · How a run ends | no | yes / unclear | Direct Connect only: flapping exit conditions repeat Release and exit HA actions | [#189](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/189) |
| EXT-25 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · How a run ends | no | yes / unclear | Direct Connect only: force watchdog uses hidden duration_min in Recurring windows | [#160](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/160) |
| EXT-26 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · How a run ends | no | yes / untested | Direct Connect only: bridge watchdog enforces duration and target SoC every 5 s |  |
| EXT-27 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Release policy | no | yes / tested | Direct Connect only: restore_on_exit captures mode before first attempt |  |
| EXT-28 | [exit-and-conflicts](../guide/scheduler/exit-and-conflicts.md) · Release policy | no | yes / tested | Direct Connect only: PUT merge keeps restore_on_exit | [#157](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/157) |
| PRI-01 | [priorities](../guide/scheduler/priorities.md) · Priorities and conflicts | yes / untested | yes / untested | **differs**: DC: any integer, free-text conflict (unknown = override), default override |  |
| PRI-02 | [priorities](../guide/scheduler/priorities.md) · Entries on the same target | yes / tested | yes / tested | **differs**: DC: contest only among entries ready on the same tick, per resource |  |
| PRI-03 | [priorities](../guide/scheduler/priorities.md) · Entries on the same target | yes / untested | yes / untested | **differs**: DC: later-ready entries judged only by If busy; override (default) pre-empts regardless of priority; mode entries never checked | [#196](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/196) |
| PRI-04 | [priorities](../guide/scheduler/priorities.md) · Entries on the same target | yes / untested | yes / untested | same: none (untested in both) |  |
| PRI-05 | [priorities](../guide/scheduler/priorities.md) · Entries on the same target | yes / untested | yes / tested | same: DC: mode only claims on its fire tick |  |
| PRI-06 | [priorities](../guide/scheduler/priorities.md) · Entries on the same target | yes / tested | yes / tested | **differs**: DC logs deferred, settles the occurrence skipped, no re-fire that occurrence |  |
| PRI-07 | [priorities](../guide/scheduler/priorities.md) · Manual control | yes / tested | yes / tested | **differs**: DC: active dispatches rows of another schedule or _widget; force winners only |  |
| PRI-08 | [priorities](../guide/scheduler/priorities.md) · Manual control | yes / tested | yes / tested | **differs**: DC defer marks the day done; wait logs every tick and retries |  |
| PRI-09 | [priorities](../guide/scheduler/priorities.md) · Manual control | yes / tested | yes / tested | same: none |  |
| PRI-10 | [priorities](../guide/scheduler/priorities.md) · Manual control | yes / untested | yes / untested | **differs**: DC: only wait does; defer gave up for the day |  |
| PRI-11 | [priorities](../guide/scheduler/priorities.md) · What the bridge cannot see | yes / untested | yes / untested | same: none (both dispatch over it) |  |
| PRI-12 | [priorities](../guide/scheduler/priorities.md) · What the bridge cannot see | yes / unclear | no | **missing here**: no ownership in DC |  |
| PRI-13 | [priorities](../guide/scheduler/priorities.md) · Entries on different targets | yes / unclear | yes / tested | **differs**: DC has gateway binding and scope all; claims per gateway on its tick |  |
| PRI-14 | [priorities](../guide/scheduler/priorities.md) · Who sent what (requester) | yes / tested | yes / tested | **differs**: DC records schedule id or _widget in the dispatches table only; no control-log requester |  |
| PRI-15 | [priorities](../guide/scheduler/priorities.md) · What the bridge cannot see | yes / unclear | no | **missing here**: no supervision in DC | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| PRI-16 | [priorities](../guide/scheduler/priorities.md) · Manual control | no | yes / tested | Direct Connect only: wait retries every tick (MB: wait = defer) |  |
| PRI-17 | [priorities](../guide/scheduler/priorities.md) · Entries on the same target | no | yes / tested | Direct Connect only: per-resource claims: grid, per-circuit, wildcard merge, unknown kind |  |
| PRI-18 | [priorities](../guide/scheduler/priorities.md) · Entries on the same target | no | yes / tested | Direct Connect only: notify/none claims nothing (MB: own lane, equivalent) |  |
| PRI-19 | [priorities](../guide/scheduler/priorities.md) · Manual control | no | yes / unclear | Direct Connect only: defer marks the date, so interval/cron/window#n entries defer and log every tick | [#204](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/204) |
| OUT-01 | [outcomes](../guide/scheduler/outcomes.md) · Activity Log results | yes / tested | yes / untested | **differs**: DC logs a word only; import writes no row |  |
| OUT-02 | [outcomes](../guide/scheduler/outcomes.md) · Activity Log results | yes / tested | yes / tested | same: DC also filters severity |  |
| OUT-03 | [outcomes](../guide/scheduler/outcomes.md) · Activity Log results | yes / untested | yes / untested | **differs**: DC History loads 200 rows, chips per status present; fired is used |  |
| OUT-04 | [outcomes](../guide/scheduler/outcomes.md) · Retries | yes / tested | yes / tested | **differs**: DC 30 s doubling to 600 s, plus in-tick resilience retries; no notification | [#172](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/172) |
| OUT-05 | [outcomes](../guide/scheduler/outcomes.md) · Retries | yes / tested | yes / tested | **differs**: DC logs plain fired; no notification | [#172](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/172) |
| OUT-06 | [outcomes](../guide/scheduler/outcomes.md) · Retries | yes / untested | yes / untested | same: DC settles it skipped |  |
| OUT-07 | [outcomes](../guide/scheduler/outcomes.md) · Supervision of a running command | yes / tested | no | **missing here**: no supervision | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| OUT-08 | [outcomes](../guide/scheduler/outcomes.md) · Supervision of a running command | yes / tested | no | **missing here**: no supervision | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| OUT-09 | [outcomes](../guide/scheduler/outcomes.md) · Supervision of a running command | yes / tested | no | **missing here**: no supervision | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| OUT-10 | [outcomes](../guide/scheduler/outcomes.md) · Supervision of a running command | yes / tested | no | **missing here**: no supervision | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| OUT-11 | [outcomes](../guide/scheduler/outcomes.md) · Supervision of a running command | yes / tested | no | **missing here**: no supervision | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| OUT-12 | [outcomes](../guide/scheduler/outcomes.md) · Supervision of a running command | yes / untested | no | **missing here**: no supervision | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| OUT-13 | [outcomes](../guide/scheduler/outcomes.md) · The dispatch record | yes / tested | yes / tested | **differs**: DC dispatches table: successful forces only (schedule, Run now, widget) | [#139](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/139) |
| OUT-14 | [outcomes](../guide/scheduler/outcomes.md) · The dispatch record | yes / untested | no | **missing here**: no verification states | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| OUT-15 | [outcomes](../guide/scheduler/outcomes.md) · The dispatch record | yes / untested | yes / untested | same: none |  |
| OUT-16 | [outcomes](../guide/scheduler/outcomes.md) · The dispatch record | yes / tested | no | **missing here**: no REST read of dispatches | [#139](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/139) |
| OUT-17 | [outcomes](../guide/scheduler/outcomes.md) · Overshoot guard | yes / tested | no | **missing here**: no overshoot guard | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| OUT-18 | [outcomes](../guide/scheduler/outcomes.md) · Notifications | yes / tested | yes / unclear | **differs**: no scheduler failure notifications; only boot reconcile notify | [#172](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/172) |
| OUT-19 | [outcomes](../guide/scheduler/outcomes.md) · Run now and Stop | yes / untested | yes / untested | **differs**: DC active_now also needs fired this occurrence; container clock | [#161](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/161) |
| OUT-20 | [outcomes](../guide/scheduler/outcomes.md) · Run now | yes / tested | yes / untested | **differs**: DC Run now ignores conditions entirely | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| OUT-21 | [outcomes](../guide/scheduler/outcomes.md) · Run now | yes / untested | yes / untested | same: DC uses duration_min (hidden 90 for windows) | [#160](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/160) |
| OUT-22 | [outcomes](../guide/scheduler/outcomes.md) · Run now | yes / untested | yes / untested | same: none |  |
| OUT-23 | [outcomes](../guide/scheduler/outcomes.md) · Run now | yes / untested | yes / untested | same: DC also runs disabled entries |  |
| OUT-24 | [outcomes](../guide/scheduler/outcomes.md) · Stop | yes / tested | yes / unclear | **differs**: DC Stop: plain Release via default gateway host, no exit HA actions, no block needed | [#192](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/192) |
| OUT-25 | [outcomes](../guide/scheduler/outcomes.md) · Stop | yes / untested | yes / untested | **differs**: DC Stop with nothing changes nothing; entry may still fire |  |
| OUT-26 | [outcomes](../guide/scheduler/outcomes.md) · The dispatch record | no | yes / untested | Direct Connect only: scheduled/Run now force writes a dispatches row |  |
| OUT-27 | [outcomes](../guide/scheduler/outcomes.md) · Run now | no | yes / untested | Direct Connect only: Run now force recorded, so Stop and If busy see it (MB: Stop does not see Run now) |  |
| OUT-28 | [outcomes](../guide/scheduler/outcomes.md) · Run now | no | yes / unclear | Direct Connect only: UI Run now uses the top-bar gateway over the bound one | [#193](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/193) |
| OUT-29 | [outcomes](../guide/scheduler/outcomes.md) · Retries | no | yes / tested | Direct Connect only: missed sweep after 120 s grace (MB: catch-up instead) |  |
| OUT-30 | [outcomes](../guide/scheduler/outcomes.md) · Activity Log results | no | yes / tested | Direct Connect only: coalesced backlog runs |  |
| OUT-31 | [outcomes](../guide/scheduler/outcomes.md) · Retries | no | yes / tested | Direct Connect only: unknown outcome settles, not retried |  |
| OUT-32 | [outcomes](../guide/scheduler/outcomes.md) · Retries | no | yes / unclear | Direct Connect only: unknown is unreachable from the action path | [#201](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/201) |
| OUT-33 | [outcomes](../guide/scheduler/outcomes.md) · Retries | no | yes / unclear | Direct Connect only: in-tick resilience retries block the scheduler thread | [#183](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/183) |
| OUT-34 | [outcomes](../guide/scheduler/outcomes.md) · Retries | no | yes / unclear | Direct Connect only: refused force / rejected mode logged fired (text classification) | [#191](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/191) |
| OUT-35 | [outcomes](../guide/scheduler/outcomes.md) · Retries | no | yes / unclear | Direct Connect only: per-attempt audit sink signature mismatch | [#201](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/201) |
| OUT-36 | [outcomes](../guide/scheduler/outcomes.md) · Run now and Stop | no | yes / unclear | Direct Connect only: Pause ineffective | [#200](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/200) |
| OUT-37 | [outcomes](../guide/scheduler/outcomes.md) · Run now and Stop | no | yes / tested | Direct Connect only: Resume only inside the window |  |
| OUT-38 | [outcomes](../guide/scheduler/outcomes.md) · Run now and Stop | no | yes / tested | Direct Connect only: paused runs become stopped at restart |  |
| OUT-39 | [outcomes](../guide/scheduler/outcomes.md) · Where to look | no | yes / tested | Direct Connect only: run queue /runs and /stats |  |
| OUT-40 | [outcomes](../guide/scheduler/outcomes.md) · Activity Log results | no | yes / tested | Direct Connect only: log severity classes with per-class caps |  |
| OUT-41 | [outcomes](../guide/scheduler/outcomes.md) · Activity Log results | no | yes / tested | Direct Connect only: 'nothing to do' still logged |  |
| OUT-42 | [outcomes](../guide/scheduler/outcomes.md) · Retries | no | yes / tested | Direct Connect only: error row names attempt and retry delay |  |
| OUT-43 | [outcomes](../guide/scheduler/outcomes.md) · Run now | no | yes / untested | Direct Connect only: Run now placeholders limited to gateway + HA values |  |
| CLK-01 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · The clock | yes / untested | yes / tested | **differs**: DC: each gateway's aGate clock (site time) |  |
| CLK-02 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · The clock | yes / untested | yes / unclear | **differs**: DC: previews on container clock, tick on site clock | [#161](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/161) |
| CLK-03 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · The clock | yes / tested | yes / tested | **differs**: DC: site timezone setting for mocks; no install check |  |
| CLK-04 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · Daylight saving | yes / unclear | yes / unclear | **differs**: DC: fixed offset re-read every 10 min; late by up to 10 min |  |
| CLK-05 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · The clock | no | yes / tested | Direct Connect only: unreadable gateway falls back to container clock, not UTC |  |
| CLK-06 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · The clock | no | yes / tested | Direct Connect only: implausible aGate clock refused |  |
| RST-01 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · Bridge restart | yes / tested | yes / untested | **differs**: DC releases only the in-memory force, to the first gateway's host | [#192](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/192) |
| RST-02 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · Bridge restart | yes / untested | yes / tested | **differs**: DC: reconcile policy, default notify (battery untouched) |  |
| RST-03 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · Bridge restart | yes / tested | yes / tested | **differs**: DC: a fired occurrence is stored, no re-fire |  |
| RST-04 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · Bridge restart | yes / untested | yes / unclear | **differs**: DC: release_stale never called; no catch-up | [#199](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/199) |
| RST-05 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · Bridge restart | no | yes / tested | Direct Connect only: paused runs resolved to stopped at start-up |  |
| RST-06 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · Bridge restart | no | yes / tested | Direct Connect only: release/resume policies re-arm or re-force |  |
| RST-07 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · Bridge restart | no | yes / untested | Direct Connect only: with notify a force outlives a restart; timer lost |  |
| RST-08 | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) · Bridge restart | no | yes / unclear | Direct Connect only: reconcile and shutdown handle only the first gateway | [#192](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/192) |
| DEP-01 | [dependencies](../guide/scheduler/dependencies.md) · Dependency matrix → Actions | no | yes / untested | same: none (untested here) | [#128](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/128) |
| — | [dependencies](../guide/scheduler/dependencies.md) · A Home Assistant action did not run | no | section | Direct Connect only: kept from the old troubleshooting page | [#169](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/169) [#171](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/171) |
| — | [dependencies](../guide/scheduler/dependencies.md) · A condition is always true when it should not be | section | section | **differs**: DC: tariff windows read None when unconfigured; grid.connected reads 0 at 0 W; before 0.5.4 an unavailable HA entity read 0 (#167) | [#206](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/206) |
| — | [dependencies](../guide/scheduler/dependencies.md) · An action is refused or does nothing | section | section | **differs**: a force refused by the Modbus client path, and a mode/off-grid write with a non-zero result, are logged fired | [#191](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/191) |
| — | [dependencies](../guide/scheduler/dependencies.md) · An entry never fires | section | section | **differs**: DC Always runs once ever (occurrence stays done across restarts) | [#190](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/190) |
| — | [dependencies](../guide/scheduler/dependencies.md) · Dependency matrix | section | section | **differs**: DC: force needs the Modbus client (this bridge); reserve never runs (#129); no trusted-rating gate | [#129](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/129) |
| — | [examples](../guide/scheduler/examples.md) · 1. Evening top-up | section | section | **differs**: weekly fire-at+duration (#160); power in % or kW (W API only); target SoC field | [#160](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/160) |
| — | [examples](../guide/scheduler/examples.md) · 2. Evening peak discharge until the minimum SoC | section | section | **differs**: daily 17:00 + 240 min because of #160 | [#160](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/160) |
| — | [examples](../guide/scheduler/examples.md) · 3. Charge from the grid when the NEM spot price is low | section | section | same: stale NEM price kept forever | [#207](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/207) |
| — | [examples](../guide/scheduler/examples.md) · 4. Storm forecast: fill the battery | section | section | **differs**: weather.code not in the picker; condition text unverified |  |
| — | [examples](../guide/scheduler/examples.md) · 5. Peak-demand window | section | section | **differs**: window flag None when undefined; overlapping force schedules release each other | [#189](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/189) |
| — | [examples](../guide/scheduler/examples.md) · 6. Weekend export, unless Home Assistant says you are away | section | section | same: since 0.5.4 an unavailable entity has no value, as in the Modbus Bridge | [#167](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/167) (fixed in 0.5.4) |
| — | [examples](../guide/scheduler/examples.md) · 7. Full by 07:00, starting as late as possible | section | no | **missing here**: no time.* sensors; one cron schedule per rung instead | [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) |
| — | [examples](../guide/scheduler/examples.md) · More examples (Direct Connect only) | no | section | Direct Connect only: template-based recipes moved from the old troubleshooting page |  |

## Existing issues this page touches

| Issue | Where |
|---|---|
| [#157](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/157) Turning a schedule on/off wiped its settings | Fixed in 0.5.2: a PUT merges what it sends into the stored schedule ([index](../guide/scheduler/index.md)). |
| [#160](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/160) A force in a Recurring window stops at the hidden duration | [triggers](../guide/scheduler/triggers.md), [actions](../guide/scheduler/actions.md), [exit](../guide/scheduler/exit-and-conflicts.md) |
| [#161](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/161) Timeline, next fire and Test use the container clock | [restarts-and-clock](../guide/scheduler/restarts-and-clock.md) |
| [#162](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/162) Scheduler parity with the Modbus Bridge | most *missing here* rows |
| [#167](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/167) An unavailable HA entity read 0 | Fixed in 0.5.4: it now has no value ([conditions](../guide/scheduler/conditions.md)). |
| [#168](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/168) PUT without `enabled` re-enables | [index](../guide/scheduler/index.md) |
| [#169](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/169) `%ha:…%` placeholders are not substituted | [actions](../guide/scheduler/actions.md) |
| [#129](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/129) reserve_soc is always skipped | [actions](../guide/scheduler/actions.md) |
| [#172](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/172) No failure notification | [outcomes](../guide/scheduler/outcomes.md) |
| [#182](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/182) The default gateway is the first registered and moves | [targets](../guide/scheduler/targets.md) |
| [#165](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/165), [#171](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/171), [#173](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/173), [#174](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/174), [#175](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/175), [#183](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/183) | release button, notification switch, dispatch notifications, Release read-back, worker restart guard, scheduler heartbeat |

## Issues filed from this review

Each was found while writing the Scheduler pages, from a code read; the ones marked
*reproduced* were confirmed by driving `scheduler.tick` with a temporary store and a
monkeypatched `battery_control.execute` (no hardware, no emulator, so not evidence of what an
aGate does). The Test against live point (it reads the default gateway's values) was added
to [#161](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/161).

| Issue | Title | Evidence | Rows |
|---|---|---|---|
| [#188](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/188) | Scheduler on/off picker stores "false" as text, which runs as on: smart circuit turns ON, Go off-grid / reconnect goes OFF-GRID (fixed in 0.5.5) | reproduced in the engine; the form path is a code read | ACT-34 |
| [#189](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/189) | A force schedule's window end sends Release even if it never fired, or after another schedule or the Battery Control widget took the battery; exit HA actions run too; flapping exit conditions repeat both | reproduced | HAA-06, EXT-01, EXT-05, EXT-24 |
| [#190](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/190) | An Always schedule fires only once, ever (its single stored run stays finished), yet keeps sending Release on every falling edge | reproduced | TRG-28, TRG-29 |
| [#191](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/191) | A force refused by the Modbus client (this bridge), and a mode or off-grid write the aGate rejects, are logged "fired" and never retried | reproduced | ACT-13, ACT-24, OUT-34 |
| [#192](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/192) | Stop, Pause, the shutdown release and the boot reconcile use the first gateway's host, not the host the force was recorded on | code read | TGT-20, EXT-20, OUT-24, RST-01, RST-08 |
| [#193](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/193) | Run now from the UI acts on the top-bar gateway, not the schedule's own gateway | code read | TGT-09, OUT-28 |
| [#194](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/194) | battery_control supervises one force per process: a second gateway's force drops the first one's time limit and target SoC | code read | ACT-39 |
| [#195](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/195) | Deleting a running schedule does not release its force | reproduced | EXT-04, EXT-21 |
| [#196](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/196) | Priority only counts on the same tick: a force that becomes ready later overrides a running one whatever their priorities (default If busy = override) | reproduced | PRI-03 |
| [#200](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/200) | Pause does not hold a run: the tick re-attempts paused runs, and a run that already succeeded is not found | reproduced | IDX-12, OUT-36 |
| [#197](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/197) | Force retries sleep inside the scheduler tick and stall every gateway (cf. #183) | code read | ACT-40 |
| [#201](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/201) | The scheduler can never record an UNKNOWN outcome, and its resilience audit hook never writes (signature mismatch) | reproduced | ACT-41, OUT-32, OUT-35 |
| [#198](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/198) | Weekly with no days, Monthly with no day of month, and One-off with no date fire every day; a Recurring window with start = end is open all day | reproduced | TRG-09, TRG-23, TRG-51 |
| [#202](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/202) | Validate actions, HA actions, cron, day of month and months when a schedule is saved; import should flag unknown sensors and operators | code read | CND-02, CND-35, ACT-02, HAA-01 |
| [#203](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/203) | On-entry HA actions repeat on every retry, and a retry waits the whole hold again | code read | CND-27, HAA-07 |
| [#204](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/204) | If busy = defer re-defers and logs every tick for interval, cron and second-window schedules | code read | PRI-19 |
| [#205](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/205) | History rows should name the gateway (gateway scope "all" rows cannot be told apart) | code read | TGT-06 |
| [#206](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/206) | grid.connected reads 0 whenever grid power is exactly 0 W | code read | SEN-04 |
| [#207](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/207) | A stale AEMO NEM price is kept forever when the fetch fails | code read | SEN-10, SEN-19 |
| [#208](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/208) | Every N minutes of 24 h or more: Next shows anchor + N, the engine fires at the anchor | reproduced | TRG-19 |
| [#199](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/199) | battery_control.release_stale() is never called; start-up relies on the reconcile policy alone | code read | RST-04 |
| [#209](https://github.com/david2069/franklinwh-direct-connect-bridge/issues/209) | An empty power sent through the API is a 0 W force; Always and zero-duration schedules get a 1-second retry deadline | code read | ACT-04, ACT-42 |

