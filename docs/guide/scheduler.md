# Scheduler

[Back to the guide index](index.md)

The Scheduler is the bridge's automation engine. A schedule is one rule, and every rule
has the same shape:

```
trigger  →  calendar restrictions  →  entry conditions  →  hold  →  priority  →  action(s)  →  exit
```

You can use as little of that as you like. "Switch to Self-Consumption at midnight" uses
only the first step and the action. The rest exists so that a rule which moves your
battery can be made to do so only when it should.

You find it on the **Scheduler** tab. It has three views: **Schedules** (the list),
**Timeline** and **History**.

New to the Scheduler? Read [Concepts](#concepts), then follow
[Your first schedule](#your-first-schedule). When something does not run, see
[Scheduler: troubleshooting and examples](scheduler-troubleshooting.md).

## Concepts

| Term | Meaning |
|---|---|
| **Schedule** | One card on the Schedules view. Also called a rule or an entry. It has a name, a trigger, an optional battery action, optional conditions and optional Home Assistant actions. |
| **Trigger** | What opens the **window**: recurring time windows, a fire time plus a duration, every N minutes, a cron expression, or "always". See [Trigger](#1-trigger-when-the-window-opens). |
| **Window** | The time a schedule is active. For **Recurring windows** it is the start and end you type. For the other triggers it is *fire time → fire time + Duration (min)*. |
| **Occurrence** | One opening of the window. A schedule fires at most once per occurrence. |
| **Entry conditions** | The gate ("Entry conditions (must hold to fire)"). Checked before the action is sent. |
| **Hold** | How long the entry conditions must stay true before the schedule fires. |
| **Battery action** | What is sent to the gateway: a mode, a smart circuit, off-grid, a reserve, a force command, or nothing ("No battery action (HA only)"). |
| **Home Assistant actions** | Optional notifications and service calls that run on entry, on exit, or both. |
| **Exit conditions** | "End early when…". Checked while the window is open; the first time they are true the window closes. |
| **Priority** and **If busy** | How a schedule competes with other schedules for the same gateway. See [Hold, and conflict resolution](#3-hold-and-conflict-resolution). |

## How a schedule is evaluated

The scheduler runs as its own worker. Every tick (15 seconds by default) it does this,
for each gateway and each enabled schedule that applies to it:

1. **Is the gateway's data fresh?** The scheduler reads the values the poller last
   stored for that gateway. If they are older than three poll intervals (at least
   90 seconds), the gateway is skipped for this tick. A schedule never acts on stale
   data.
2. **Is the window open?** The trigger and the calendar restrictions must both allow
   today and now. If exit conditions are already true, the window counts as closed.
3. **Has it already fired this occurrence?** If so, it waits for the next window.
4. **Do the entry conditions pass?** If not, it logs *gated* (once a day) and tries again
   next tick, for as long as the window is open.
5. **Has the hold passed?** If not, it logs *waiting* and keeps counting.
6. **Does it win the gateway?** If several schedules want the same thing, the highest
   priority wins. Then **If busy** decides what happens when another schedule's force
   command is already running.
7. **Send the battery action, then the on-entry Home Assistant actions.** A success
   logs *fired*. A failure logs *error* and is retried while the window is open. See
   [When a run fails, is missed, or the bridge restarts](#when-a-run-fails-is-missed-or-the-bridge-restarts).

When the window closes (time runs out, or the exit conditions become true), the bridge
runs the exit steps described in [Exit](#5-exit-ending-the-window).

A few rules follow from this:

- **Conditions are a gate, not a leash.** Entry conditions are checked before the action
  is sent. Once a force command is running, only the exit conditions, the end of the
  window or the force's target SoC stop it.
- **A mode change is not undone at the end of the window.** Only a force command is
  released. To switch back, add a second schedule, or set **restore on exit** (see
  [Exit](#5-exit-ending-the-window)).
- **Schedules with no battery action never compete.** A notify-only schedule always runs.

## Your first schedule

This walkthrough discharges the battery on weekday evenings, but only if it has charge to
spare, and stops at your minimum discharge SoC.

!!! note "Force commands need the Modbus client (this bridge)"
    **Force charge / discharge / standby** goes through the Modbus client (this bridge) to
    the aGate Modbus TCP Server (:502). If the Modbus client (this bridge) is off, the action
    is shown as unavailable with the reason. To try the Scheduler without it, use the
    **Set operating mode** action instead.

![Add schedule: trigger, battery action, priority, If busy, gateway, entry conditions, hold and exit conditions](../images/scheduler/12-hold-and-conflicts.png)

To create it:

1. On the **Scheduler** tab, press **Add schedule**.
2. **Name:** `Evening discharge`.
3. **Trigger type:** **Weekly at time**. Under **Days**, tick **Mon** to **Fri** (none
   ticked means every day). Set **Fire at** to `17:00` and **Duration (min)** to `180`.
4. **Battery action:** **Force charge / discharge / standby**. Set **Direction** to
   **Force discharge**, **Power unit** to **% of inverter power**, and **Power** to `50`.
   Leave **Target SoC** empty.
5. Leave **Priority** at `0`, **If busy** at `override` and the gateway at
   **Default gateway**.
6. **Entry conditions:** press **+ row**. Pick **Battery SoC (%)**, operator `>`,
   value `40`.
7. **End early when…:** press **+ row**. Pick **Battery SoC (%)**, operator `<=`, press
   **Lookup**, and pick **Const: min discharge SoC (%)**. Set that constant first under
   **Settings → Automation → Automation Constants**.
8. Press **Test** under each block. Each row is marked *passes*, *fails* or *no value*
   against the live data.
9. Leave **Enabled** ticked and press **Create Entry**.

What happens next:

- At 17:00 on a weekday the bridge checks the SoC. Above 40 %, it starts the force
  discharge. Otherwise it logs *gated* and checks again every tick until 20:00, so it can
  still start later in the window.
- When the SoC falls to your minimum discharge SoC, the exit condition closes the window
  and the force is released. The schedule does not fire again until tomorrow's window.
- At 20:00 the window closes and the bridge releases the force if it is still running.

!!! warning "For a force action, use a trigger with Fire at and Duration"
    In 0.5.2 and earlier a force command also stops after the schedule's **Duration (min)** (#160). A
    **Recurring windows** schedule still has that value, although the form hides it, and
    a new schedule starts with 90. So a force in a three-hour recurring window stops after
    90 minutes. Use **Daily at time** or **Weekly at time** for force actions.

To check it before the window opens, open the card's **⋮** menu and choose
**Test against live**. It says *Would fire* or *Would not fire*, with the reason and each
row's live value.

## The schedule list

![The Schedules view: a schedule card with Explain, Edit, Turn on and the ⋮ menu](../images/scheduler/18-using-schedules-from-ha.png)

Each schedule is a card. It shows:

- the name, the fire time and duration, the recurrence in words and the number of
  conditions;
- **Next:** when it fires next, or *disabled*;
- **● active** while its window is open, and **On** or **Off**;
- the battery action (or *No gateway action*) and the number of HA actions;
- the last result, with its date.

Above the cards, **N active now** counts the running schedules. The **All / Enabled /
Disabled** buttons filter the list; a note says how many are hidden.

| Control | What it does |
|---|---|
| **Explain** | A plain-language summary of what the schedule will do, at three levels: **min**, **medium** and **full**. |
| **Edit** | Opens the form. If the schedule is running, saving asks first, then applies the change to the window in progress. |
| **Turn on** / **Turn off** | Enables or disables the schedule. See the warning below. |
| **Stop** | Shown while the schedule is active. Releases the force command this schedule started. The schedule stays enabled. |
| **⋮ → Test against live** | Evaluates the conditions against live values, without acting. |
| **⋮ → Run now** | Runs the actions immediately, ignoring the window. Asks first. See [Run now, Stop, Pause and Resume](#run-now-stop-pause-and-resume). |
| **⋮ → Duplicate** | Opens a copy in the form, named "Copy of …", with **Enabled** unticked. It is saved as a new schedule. |
| **⋮ → Delete** | Removes the schedule, after asking. |

!!! note "Before 0.5.2, Turn on / Turn off reset a schedule's settings"
    Up to 0.5.1 the **Turn on** / **Turn off** button saved only part of the schedule: the
    trigger type, time windows, days and months, date range, exit conditions, hold,
    priority, **If busy**, **restore on exit** and **gateway scope "all"** went back to
    their defaults. Saving from the form also lost the last two. 0.5.2 fixed both: a save
    now changes only what it sends (#157). **If you used the button before 0.5.2, check
    the schedule's settings.**

## Timeline

![Planned windows on the Timeline view](../images/scheduler/17-working-with-schedules.png)
<!-- screenshot needed: the Timeline view, with the SoC line, mode band, fire markers and Planned windows -->

The **Timeline** view shows today, from 00:00 to 24:00:

- a band along the top coloured by the operating mode the gateway actually ran;
- the battery SoC as a line;
- dashed markers where a schedule fired, exited, was gated or failed;
- a line at the current time.

Below it, **Planned windows** lists each enabled schedule's windows for today as a bar.
Schedules with no fixed daily window (every N minutes, cron, always) are not drawn, nor
are schedules the calendar excludes today.

## History

<!-- screenshot needed: the History view, with the status filter chips and a few events -->

The **History** view is the activity log: every decision the scheduler made, newest
first. Times are in bridge-host time.

The chips at the top filter the list. **all** shows everything, **battery** shows battery
events (force commands, and external control by a VPP), and there is one chip per status present. Click a chip again to clear it.

| Status | Meaning |
|---|---|
| created, updated, enabled, disabled, deleted | A change to the schedule. |
| fired | The actions ran and succeeded. |
| gated | The window was open but the entry conditions failed. Names the failing rows (up to two) and their live values. Logged once a day. |
| waiting | The conditions are met and the hold is counting down. Also *If busy = wait*. |
| deferred | Another schedule won the gateway, or *If busy = defer* skipped it. Names the winner. |
| exit | The window closed: "exit condition met" or "window closed". |
| error | An action failed. Says which attempt, and when it will retry. |
| unknown | The bridge cannot tell whether the write landed. Not retried. |
| missed | The window closed with no successful run. |
| coalesced | A run left open by downtime was folded into the current run. |
| manual | **Run now**. |
| stopped, paused, resumed | **Stop**, or the pause and resume API calls. |
| dispatch-start, dispatch-end, vpp-start, vpp-stop | A force command started or ended, or external (VPP) control started or stopped. Shown under the **battery** chip. |

---

## 1. Trigger — when the window opens

![Add schedule, with the trigger types listed](../images/scheduler/01-trigger-types.png)

Eight trigger types, confirmed from the running bridge (`GET /api/schedules` →
`trigger_types`):

| Trigger | What it means |
|---|---|
| `daily` | One `fire_at` time plus a duration, every day the calendar allows. |
| `window` | A list of start→end pairs. A window whose end is at or before its start wraps past midnight. |
| `weekly` | A time, restricted to chosen days of the week. |
| `monthly` | A time, restricted to a day of the month — clamped at month end, so "31" fires on the 30th or 28th rather than being skipped. |
| `once` | Fires on one date, then goes dormant. |
| `interval` | Every N minutes, from an optional anchor time. |
| `cron` | A cron expression. Needs the `croniter` package; the UI reports whether it is available (`cron_available` was `true` on the bridge read live). |
| `always` | **No time window at all.** The entry conditions *are* the window — it acts whenever they hold and ends when they stop. |

Everything except `interval`, `cron` and `always` resolves to one or more daily time
windows. A duration of zero means a single instant rather than a window.

Windows that cross midnight are handled properly, and the occurrence is attributed to the
day the window *opened* — so a 22:00 window lasting 300 minutes is still "yesterday's
run" at 01:00, and recurrence is judged against the opening day.

### Calendar restrictions

![A Recurring windows trigger: days of the week and time windows](../images/scheduler/02-calendar-restrictions.png)

Every recurrence field is a **restriction**, and leaving it empty means *no* restriction:

- days of the week
- months
- day of the month
- a start date and an end date

A rule that is blocked by one of these reports why — "not one of its days of the week",
"after end date 2026-12-31" — rather than quietly doing nothing.

### How fast can a schedule react

![The Scheduler tab's note that schedules run on the poll tick](../images/scheduler/03-how-fast-tick-note.png)

The scheduler ticks on its own cadence (`scheduler_tick_s`, default 15 seconds, held
between 5 and 60 seconds so a one-minute window cannot be stepped over). But it reads
the values the poller last stored, so **a rule cannot react faster than the bridge reads
the gateway**. The Scheduler tab says "Schedules run on the poll tick" for this reason.
A gateway whose stored values are older than three poll intervals (at least 90 seconds)
is not evaluated at all.

### Which clock

![Settings → Setup → Where is this site? The site timezone schedules run on](../images/scheduler/04-which-clock-site-timezone.png)

Schedule *rules* are evaluated in the **site's** wall-clock time — the aGate's timezone,
not the container's. If the gateway cannot be read, the bridge falls back to
container-local time. The audit trail and logs, by contrast, are in bridge-host time.
`docs/TIMEZONES.md` has the full picture.

---

## 2. Conditions — the gate

![An entry condition: Battery SoC > 20](../images/scheduler/05-conditions.png)

A condition tree answers one question: *should this rule act right now?* Two trees are
available per rule: **entry conditions** (the "Only if" box) and **exit conditions**
("End early when…").

### Operators

![The operator list](../images/scheduler/06-operators.png)

Thirteen, confirmed live (`ops` from `GET /api/schedules`):

| Operator | Notes |
|---|---|
| `<` `<=` `==` `!=` `>=` `>` | `==` compares numerically when both sides are numbers, exactly for booleans, and case-insensitively otherwise — so `mode.name == self-consumption` matches. |
| `between` | Inclusive, and order-independent. |
| `in` / `not_in` | Numeric membership. Members can be scalars or inclusive ranges written `20-40` or `20..40`. |
| `matchlist` / `not_matchlist` | Verbatim name lists, case-folded, with no range parsing — so `Self-Consumption` stays one name. |
| `like` / `not_like` | Case-insensitive wildcards: `*` or `%` for many, `?` or `_` for one. A pattern with no wildcard falls back to a substring test. |

The six list- and pattern-style operators take a raw member list on the right, so the
**Value / Lookup** toggle is hidden for them.

### Value or Lookup

![A Lookup comparison against Const: min discharge SoC](../images/scheduler/07-value-or-lookup.png)

The right-hand side can be a literal **Value** or a **Lookup** — another sensor's live
value. `battery.soc_pct > const.min_discharge_soc` is a lookup comparison, and keeps the
threshold in one place instead of copied across rules.

### ALL / ANY, and nesting

![Match ALL with a nested Match ANY group](../images/scheduler/08-all-any-nesting.png)

Rows combine with **Match ALL** or **Match ANY**, and they nest into groups, so
"(A and B) or C" is expressible. An empty ALL group is true; an empty ANY group is false.

### The rule that matters most

![Test: a row with no value (no forecast configured) fails the gate](../images/scheduler/09-missing-value-is-false.png)

**A missing or unreadable value is FALSE for every operator — including `!=`.** A
scheduler must never act on data it does not have. The same applies to the right-hand
side of a Lookup: if the sensor it names cannot be read, the leaf fails closed. This is
why a rule can appear to "do nothing" when a sensor briefly goes unavailable, and it is
deliberate.

### What you can gate on

![The grouped sensor picker](../images/scheduler/10-what-you-can-gate-on.png)

The sensor picker is grouped. On the bridge read live on 2026-10-15 it offered **196
sensors** across eleven groups:

| Group | Count | Examples |
|---|---|---|
| Gateway | 15 | `battery.soc_pct`, `battery.power_w`, `grid.power_w`, `grid.connected`, `solar.power_w`, `load.power_w`, `generator.power_w`, `mode.name`, `status.run_status`, `status.run_status_desc`, `status.vpp`, `status.off_grid`, `status.debug`, `status.programme_id`, `bridge.latency_ms` |
| Derived Battery | 10 | `battery.stored_kwh`, `battery.remaining_kwh`, ETAs to the charge/discharge targets at current and at max rate, solar-tracker percentages |
| Weather & Solar | 7 | `weather.temp_c`, `solar_forecast.today_kwh`, `solar_forecast.remaining_kwh`, `solar.today_kwh` (actual) |
| Tariff & Utility | 23 | the active tariff's rates, permissions and window flags |
| Demand / Tariff | 5 | peak and interval grid-import demand, demand charge to date |
| Energy | 5 | period import/export and cost |
| Fixed Charges | 5 | standing-charge accrual |
| System Setup | 8 | the derived install profile |
| Automation Constants | 4 | `const.min_discharge_soc`, `const.max_charge_soc`, `const.demand_charge_min_soc`, `const.default_operating_mode` |
| one group **per Home Assistant instance**, named after it | 114 across two instances | every HA entity you have **exposed** — see below |

Your counts will differ. The Home Assistant groups are named after your own instances
(the live bridge had two, contributing 113 and 1 exposed entities), so what you see there
is exactly what you exposed on the Home Assistant tab. The tariff groups depend on having
a tariff configured at all.

Two notes on specific sensors, taken from the code's own warnings:

- **`status.run_status`** is available both as a number and as text
  (`status.run_status_desc`). Use the number for an exact machine test, the text for a
  readable one and for message substitution. Documented values: 0 Standby, 1 Charging,
  2 Discharging, 5–7 off-grid, 8 Debug, 9 VPP.
- **`status.programme_id`**: `9` means VPP, but ordinary programmes use large arbitrary
  ids. So test `== 9`; never `!= 9` to mean "no programme".
- Booleans are exposed as `1`/`0` so they compare like everything else (`status.vpp == 1`).
- `grid.connected` is **derived** from grid power being non-zero, not a device field.

### Gating on Home Assistant

![An exposed Home Assistant entity in the sensor picker](../images/scheduler/11-gating-on-home-assistant.png)

Any HA entity you expose on the **Home Assistant** tab becomes a scheduler sensor named
`ha:<instance>:<entity_id>`. Only exposed entities are read each tick — polling every
entity in a large HA install would hammer it. HA states are coerced for you: numeric
strings become numbers, and `on/true/open/home` → `1` while
`off/false/closed/away/unavailable/unknown` → `0`, so a binary sensor works in a `== 1`
condition.

---

## 3. Hold, and conflict resolution

![Priority, If busy (override / defer / wait) and Hold](../images/scheduler/12-hold-and-conflicts.png)

**Hold (`entry_hold_s`)** — the conditions must stay true *continuously* for this many
seconds before the rule fires. A rule that is waiting out its hold logs
"conditions met — holding Ns before firing"; if the conditions lapse, the timer resets. A
bridge restart restarts the hold, which is the safe direction.

**Priority** — when several rules become due on the same tick and want the same thing,
the highest priority wins and the others are deferred **with a reason that names the
winner**, e.g. *"deferred — 'Peak shaving' (priority 5) holds battery this occurrence;
this rule is priority 0"*.

Contention is per **resource**, not per gateway. This matters: `force`, `set_mode` and
`reserve_soc` contend with each other because they are one behaviour, whereas a rule that
only sends a notification claims nothing and never contends. A wildcard smart-circuit
claim is merged with the specific-circuit claims on the same gateway before a winner is
picked, so two rules that genuinely fight cannot each "win" their own group. On a tie in
priority, the **older** schedule wins, so renaming a schedule never changes the winner.

**If busy** — what a schedule with a **force** action does when another schedule's force
command is already running on the battery:

| If busy | What happens |
|---|---|
| `override` (default) | Takes control and sends its own force command. |
| `defer` | Skips this occurrence. Logged as *deferred*. |
| `wait` | Logs *waiting* and tries again next tick, while its window is open. |

**If busy** looks at the force commands the bridge has recorded as running: those
started by other schedules, and one started from the **Battery Control** widget on the
Control tab.

---

## 4. Actions — what the rule does

![The battery action list](../images/scheduler/13-actions.png)

Six action kinds are offered (`actions` from `GET /api/schedules`), each with a note in
the code about how it is known to work:

| Action | Needs | Note from the code |
|---|---|---|
| **Set operating mode** | local | "1727 opt:3 — verified." |
| **Smart circuit on/off** | local | "1409 full-block RMW with read-back — verified 2026-08-08." |
| **Go off-grid / reconnect** | local | "consequential; confirm before enabling a schedule that uses it." |
| **Set reserve SoC** | **cloud** provider | "No local write path exists; needs cloud credentials." |
| **Notify (Home Assistant)** | a configured notification device | — |
| **Force charge / discharge / standby** | **Modbus** reachable | Runs for the schedule window, auto-releases at window end, and enforces the target SoC if set. |

One kind is listed as **unavailable, with the reason** rather than hidden:
`smart_circuit_schedule` — *"the gateway accepts and discards schedule writes"*. The
principle throughout is that offering a control which silently does nothing is worse than
not offering it, so an unavailable action is shown greyed with its reason.

### The force action in detail

![The force action: direction, power, power unit and target SoC](../images/scheduler/14-force-action.png)

It runs for the schedule's **window**, not for a duration you set separately. The
bridge's watchdog releases at the window's end and enforces the **target SoC** — charge
stops at SoC ≥ target, discharge at SoC ≤ target — reading live SoC from that gateway's
last poll. The window's closing edge also fires a release as a safety net, so a force
never outlives its window.

Device-commanding actions (`force`, `set_mode`, `smart_circuit`, `offgrid`) are executed
as **writes** with a deadline: retried only while the fault looks transient, and **never**
retried once the outcome is unknown. An ambiguous first force-charge is not followed by a
second one.

### Home Assistant actions

![Home Assistant actions on a rule](../images/scheduler/15-home-assistant-actions.png)

In addition to the gateway action, a rule can carry any number of **HA actions**, in
three flavours:

- **NOTIFY** — a message to a configured notification device.
- **ENTITY** — a guided service call: pick an exposed entity, and the editor offers the
  domain-appropriate control (turn on, turn off, toggle, set an option, press a button,
  run a scene or script).
- **SERVICE** — the raw form: domain, service, entity and a JSON payload.

Each HA action has a **when**: on entry, on exit, or both. Each can carry its own
**guard** — a condition that must hold at the moment it fires. And messages support
variable substitution: `%battery.soc_pct%` is replaced with the live value, using the same
sensor vocabulary as the conditions. A value that cannot be read renders as `?` rather
than blocking the message, on the grounds that a notification missing one field beats one
that never arrives.

---

## 5. Exit — ending the window

![End early when Battery SoC <= 20](../images/scheduler/16-exit-conditions.png)

A window closes two ways: time runs out, or the **exit conditions** become true
mid-window. "End early when `battery.soc_pct <= 20`" stops a force discharge before it
drains the pack.

At the closing edge the bridge:

1. fires the exit-tagged HA actions (guards respected);
2. if **restore on exit** is set, puts back what the rule overrode;
3. releases a force dispatch, whether or not the action itself already ended;
4. logs an `exit` event saying which it was — "exit condition met" or "window closed".

**Restore on exit** is opt-in on purpose: "leave it where the rule left it" is a
legitimate intent, and turning restoration on by default would silently change what
existing rules do. Today it covers the operating mode. The form has no control for it:
set `"restore_on_exit": true` through the API (see
[Using schedules from Home Assistant](#7-using-schedules-from-home-assistant)). Saving
the schedule from the form afterwards turns it off again.

A rule whose exit condition already holds will not *start*; it reports "exit condition
already holds".

---

## 6. Working with schedules

![The built-in Templates](../images/scheduler/17-working-with-schedules.png)

- **Templates** — built-in presets, loaded into the editor for review rather than fired
  blind. The local-only ones (mode switches, a circuit off overnight, a low-battery
  notification, a peak-window notify, "Time-of-Use at peak only if charged") need nothing
  special. Four more require Modbus: **Peak shaving**, **Battery Bonus export**,
  **Solar sponge** and **Off-peak charge** — each a force window with an SoC condition
  and a target-SoC floor.
- **Test against live** — evaluates the condition tree against the current snapshot and
  returns a trace with *one row per leaf*: the sensor, the operator, the resolved
  right-hand side, the live value and the result. There is no short-circuiting during a
  test, so you see every leaf, not just the first failure.
- **Run now**, **Stop**, **Duplicate** — see [The schedule list](#the-schedule-list) and
  [Run now, Stop, Pause and Resume](#run-now-stop-pause-and-resume). Pause and Resume
  are API calls only; the tab has no button for them.
- **Planned windows** — see [Timeline](#timeline).
- **The log explains itself.** Besides fired and exit events, the engine records a
  `gated` event — *once a day*, not every tick — naming the first failing leaf and its
  live value, so "why did my rule do nothing?" has an answer in the UI.
- **Import / export.** Schedules export as a `franklinwh-local-schedules` bundle. The
  bridge also **imports the Modbus Bridge's `franklinwh-automations` bundles** and maps
  them field by field, and can convert its own rules back to that format. Import
  validation reports the whole bundle at once rather than failing on the first bad row,
  separating errors (a missing name, a `fire_at` that is not `HH:MM`, an unknown action)
  from warnings (a gateway or notify device that does not exist here, which you fix after
  import).

---

## Run now, Stop, Pause and Resume

| Control | Where | What it does |
|---|---|---|
| **Run now** | **⋮** menu, or `POST /api/schedules/{id}/run` | Runs the battery action and the on-entry HA actions immediately. It ignores the window **and the entry conditions**; each HA action's own guard still applies. A force command runs for the schedule's **Duration (min)**; with no duration it runs until you release it or it reaches its target SoC. Exit conditions do not apply. Logged as *manual*. |
| **Stop** | Card button while active, or `POST /api/schedules/{id}/stop` | Releases the force command this schedule started. The schedule stays enabled. If it owns no force command, nothing changes and the log says so. Logged as *stopped*. |
| **Pause** | API only: `POST /api/schedules/{id}/pause` | Releases control but keeps the current run, so you can resume it. Logged as *paused*. |
| **Resume** | API only: `POST /api/schedules/{id}/resume` | Re-enters a paused run. Refused once its window has closed. Logged as *resumed*. |

To stop a schedule from firing at all, disable it: press **Edit**, untick **Enabled**, and
press **Save Changes**.

!!! warning "Run now acts for real"
    Run now does exactly what the schedule does: a mode change, a smart circuit, or a
    battery force. Use **⋮ → Test against live** first.

## When a run fails, is missed, or the bridge restarts

**A failed action is retried while the window is open.** The bridge waits 30 seconds,
then doubles the wait after each failure, up to 10 minutes. Each attempt logs *error*
with the attempt number and the next wait.

**An unknown outcome is not retried.** If the bridge cannot tell whether a write landed
(for example, the connection dropped mid-write), it logs *unknown* and does not send it
again. Sending a second force command after an ambiguous first one could dispatch twice.
Check the battery yourself.

**A window that closes without success is recorded as missed.** Two minutes after the
window closes, a run that never succeeded is logged as *missed*, with the number of
attempts. There is no catch-up: a missed run does not fire late.

**After a restart:**

- A schedule that already fired in the current window does not fire again.
- A schedule that has not yet fired is evaluated afresh. Its hold timer starts again.
- A force command a restart interrupted is handled by the interrupted-dispatch policy
  (default: notify you, without touching the battery). See
  [After a bridge restart mid-dispatch](control.md#after-a-bridge-restart-mid-dispatch).
- A paused run is not resumed.

**Stale data stops evaluation.** If a gateway's stored values are older than three poll
intervals (at least 90 seconds), its schedules are not evaluated until fresh data
arrives.

## Not available in this bridge

The FranklinWH Modbus Bridge's scheduler has some features this bridge does not. Do not
expect these here:

- **A Release action.** There is no schedule action that only releases. A force command
  is released at the end of its window, by an exit condition, by **Stop** or by its
  target SoC.
- **Release policies and hold-instead-of-release.** At window end a force command is
  always released. The only option is **restore on exit** (API only).
- **Site and utility-service targets.** A schedule targets one gateway, or every gateway
  with gateway scope `all` (API only).
- **Dispatch verification and re-send.** The bridge does not check that the battery
  actually moved after a force command, and does not re-send a lost setpoint.
- **An overshoot guard.** The bridge does not release a force command because the battery
  ran faster than requested.
- **Catch-up after an outage.** A missed window is logged, not fired late.
- **Pause and Resume buttons.** Both exist as API calls only.
- **Per-schedule export from the card.** **Export** downloads every schedule. To export
  some, use `GET /api/schedules/export?ids=<id>,<id>`.

---

## 7. Using schedules from Home Assistant

![A saved schedule in the list; each of these actions is also a REST call](../images/scheduler/18-using-schedules-from-ha.png)

Everything the Scheduler tab does is also a REST call. Home Assistant can make those calls
with `rest_command`, so automations and scripts can read, create, update, delete, run and pause
schedules. Home Assistant entities for run, pause and state over MQTT are planned (#128).

**The address.** From Home Assistant, the add-on is reachable on its internal hostname. The
add-on's **Info** page shows it (for example `4a12892f-franklinwh-local-bridge`). Use
`http://<that hostname>:8101`. A Docker install uses its own host and port.

> The bridge's HTTP API has no login. Anything that can reach it can do all of the below.
> Keep it on a trusted network.

```yaml
# configuration.yaml
rest_command:
  fwh_schedule_create:          # body: a full schedule (see "The fields" below)
    url: "http://<hostname>:8101/api/schedules"
    method: POST
    content_type: "application/json"
    payload: "{{ schedule | tojson }}"
  fwh_schedule_update:          # merges into the definition (#157); always send name and enabled
    url: "http://<hostname>:8101/api/schedules/{{ id }}"
    method: PUT
    content_type: "application/json"
    payload: "{{ schedule | tojson }}"
  fwh_schedule_delete:
    url: "http://<hostname>:8101/api/schedules/{{ id }}"
    method: DELETE
  fwh_schedule_run:             # runs its actions NOW, ignoring the window
    url: "http://<hostname>:8101/api/schedules/{{ id }}/run"
    method: POST
  fwh_schedule_pause:           # releases control but keeps the current run
    url: "http://<hostname>:8101/api/schedules/{{ id }}/pause"
    method: POST
  fwh_schedule_resume:          # re-enters a paused run while its window is open
    url: "http://<hostname>:8101/api/schedules/{{ id }}/resume"
    method: POST
  fwh_schedule_stop:            # releases this schedule's battery dispatch; stays enabled
    url: "http://<hostname>:8101/api/schedules/{{ id }}/stop"
    method: POST
```

**Reading.** A `rest` sensor on `GET /api/schedules` lists every schedule with `enabled`,
`next_fire` and `active_now`. `GET /api/schedules/runs` and `GET /api/schedules/log` give
what ran and why.

**Pause vs disable: they are different.**

| You want | Call |
|---|---|
| Stop the **current run** but keep it, to resume within its window | `pause`, then `resume` |
| Release a **battery dispatch** this schedule started, and leave the rule enabled | `stop` |
| Stop the rule from **firing at all** until further notice | `update` with `"enabled": false` |

**Run means real actions.** `run` does what the schedule does: a mode change, a smart
circuit, or a battery force. Test a new rule with `POST /api/schedules/{id}/test` first:
it evaluates the conditions and says what *would* happen, without acting.

**The fields** are those of the Scheduler tab's editor. A minimal rule that switches to
Self-Consumption at midnight:

```json
{"name": "Self-Consumption all day", "enabled": true,
 "fire_at": "00:00", "duration_min": 0,
 "action": {"kind": "set_mode", "mode": "self"}}
```

For anything more involved, build it in the Scheduler tab and **export** it
(`GET /api/schedules/export`): that is the exact JSON the API accepts.

## Multi-gateway behaviour

![Binding a rule to a gateway](../images/scheduler/19-multi-gateway-binding.png)

Covered in [Multi-gateway and sites](multi-gateway.md), but the short version:

- A rule **bound to a gateway** fires only on that gateway's tick.
- An **unbound** rule fires on the **default gateway's** tick only — so it does not run
  once per gateway on a multi-gateway site.
- A rule with **gateway scope "all"** is evaluated by every gateway on its own tick,
  producing one run and one resource claim per gateway. The form has no control for
  this: set `"gateway_scope": "all"` through the API. From 0.5.2, saving the schedule from
  the form keeps it (before 0.5.2 the form turned it off).
