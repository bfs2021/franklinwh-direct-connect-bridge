# Scheduler: troubleshooting and examples

[Back to the guide index](README.md) · [Scheduler](scheduler.md)

This page covers what each condition and action needs, how to find out why a schedule did
nothing, and some worked recipes.

---

## What each condition needs

A condition whose sensor has no value is **false**, for every operator. So a sensor that
depends on something you have not set up makes its condition fail. The picker groups the
sensors; each group needs this:

| Picker group | Needs |
|---|---|
| **Gateway** | Fresh data from that gateway's poller. |
| **Derived Battery** | **Settings → Automation → Automation Constants**: battery capacity, max charge SoC and min discharge SoC. The "at max rate" times also need a rating: from the Modbus client (this bridge), or the battery max power constant. The solar tracker rows need the solar forecast. |
| **Weather & Solar** | A location and PV array under **Settings → Integrations**. |
| **Tariff & Utility** | A meter and tariff for the gateway's site. The wholesale spot price needs an AEMO NEM region or a Home Assistant price entity. |
| **Demand / Tariff**, **Energy**, **Fixed Charges** | A tariff with those charges or windows configured. |
| **Automation Constants** | Values set under **Settings → Automation**. |
| One group per **Home Assistant** instance | The instance set up, and the entity **exposed** on the Home Assistant tab. |

## What each action needs

| Battery action | Needs |
|---|---|
| **Set operating mode** | The local Direct Connect path. |
| **Smart circuit on/off** | The local Direct Connect path. |
| **Go off-grid / reconnect** | The local Direct Connect path. |
| **Set reserve SoC** | Validated FranklinWH cloud credentials. There is no local write path. |
| **Notify (Home Assistant)** | A notification device. |
| **Force charge / discharge / standby** | The Modbus client (this bridge) switched on, and the aGate Modbus TCP Server (:502) reachable. Otherwise the action is shown as unavailable, with the reason. |

| Home Assistant action | Needs |
|---|---|
| **+ notify** | A notification device. The button is disabled until you add one. |
| **+ entity** | A Home Assistant instance. The guided picker lists only exposed entities; **Advanced (raw service)…** takes any domain, service and entity. |

---

## Troubleshooting

Start with two tools on the Scheduler tab:

- **⋮ → Test against live** on the card. It says *Would fire* or *Would not fire*, with
  the reason (for example "outside its window" or "entry conditions not met"), and each
  condition row with its live value.
- The **History** view. Filter by *gated*, *error* or *missed* to see what the scheduler
  decided, and why.

### A schedule never fires

Check these in order:

1. **Is it enabled?** The card shows **On**, and **Next:** shows a time rather than
   *disabled*.
2. **Is the window open now?** Test against live says "outside its window", or names the
   calendar restriction that blocks today: "not one of its days of the week", "before
   start date", and so on.
3. **Did it already fire this occurrence?** It fires at most once per window. Test
   against live says "already fired this occurrence".
4. **Is it the right gateway?** A schedule with **Default gateway** runs only on the
   default gateway. See [Multi-gateway behaviour](scheduler.md#multi-gateway-behaviour).
5. **Is the gateway's data fresh?** If the gateway has not been polled for three poll
   intervals (at least 90 seconds), its schedules are not evaluated. Check the **Network**
   and **Health** tabs.
6. **Did it lose to another schedule?** The History view shows *deferred*, naming the
   winner and its priority.
7. **Is the window long enough?** The scheduler ticks every 15 seconds by default. A
   one-minute window is always long enough.

### A condition is always false

- **The sensor has no value.** Test against live shows "—", or the editor's **Test**
  marks the row *no value*. Set up what the sensor needs (see
  [What each condition needs](#what-each-condition-needs)).
- **A Lookup's sensor has no value.** The right-hand sensor must have a value too.
- **The unit is not what you expected.** Check the sensor's label in the picker. Tariff
  rates are in $/kWh; the spot price is in c/kWh.
- **`!=` on a missing value is false.** Use a positive test, such as `status.vpp == 0`.
- **The text does not match.** `==` on text ignores case, but the words must match.
  Use `like` with `*` for a partial match.

### An action is refused or does nothing

- **Force is unavailable.** The Battery action list says *unavailable*, and the form shows
  the reason. Usually the Modbus client (this bridge) is off.
- **Set reserve SoC fails.** It needs validated cloud credentials.
- **The mode did not change back.** A mode change is not undone at the end of the
  window. Add a second schedule to switch back.
- **A force stopped early.** Check its **Target SoC** and **Duration (min)**. See the
  warning in [Your first schedule](scheduler.md#your-first-schedule).
- **The History view shows *error*.** The bridge retries while the window is open. If the
  window closes first, the run is logged as *missed*.
- **The History view shows *unknown*.** The bridge could not tell whether the write
  landed, and did not retry. Check the gateway, and the **Logs** tab.

### A Home Assistant action did not run

- Check its **when**: **On entry**, **On exit** or **Entry & exit**.
- Check its guard. An action whose guard is false at that moment is skipped.
- A value in the message that cannot be read shows as `?`. The message is still sent.

---

## Examples

Each example starts from **Add schedule** or **Templates** on the Scheduler tab. Press
**Test** on each condition block before you save.

### 1. Low-battery alert

Tell me when the battery drops below 20 %. No battery action.

1. **Templates → Low battery alert (notify only) → Use**.
2. Under **Home Assistant actions**, pick your notification device.
3. Tick **Enabled** and press **Create Entry**.

It covers the whole day (00:00 for 1439 minutes) and fires at most once a day, the first
time the SoC is below 20 %. The message uses `%battery.soc_pct%` for the live value.

### 2. Notify at the start and end of the peak window

1. **Templates → Peak window — notify start & end → Use**.
2. Pick your notification device. The action's **when** is **Entry & exit**, so you get
   one message at 16:00 and one at 21:00.

### 3. Overnight off-peak charge

Charge overnight on the cheap rate, only if the battery is below 50 %, up to 90 %. Needs
the Modbus client (this bridge).

1. **Templates → Off-peak charge (overnight) → Use**.
2. Check the window: **Fire at** `01:00`, **Duration (min)** `300`.
3. Check the action: **Force charge**, `100` **% of inverter power**, **Target SoC** `90`.
4. Tick **Enabled** and press **Create Entry**.

The force stops at 90 % or at 06:00, whichever comes first.

### 4. Time-of-Use at peak, then back to Self-Consumption

A mode change stays until something changes it, so this takes two schedules.

1. **Templates → Time-of-Use at peak (only if charged) → Use**. It switches to Time-of-Use
   at 16:00, only if the SoC is above 50 %. Save it.
2. **Add schedule**. **Trigger type:** **Daily at time**, **Fire at** `21:00`,
   **Duration (min)** `0`. **Battery action:** **Set operating mode**, Self-Consumption.
   Save it.

### 5. Only when Home Assistant says so

Run a schedule only while a Home Assistant switch or binary sensor is on.

1. On the **Home Assistant** tab, expose the entity.
2. In the schedule's **Entry conditions**, press **+ row** and pick the entity from its
   Home Assistant group.
3. Choose `==` and `1`. Home Assistant `on`, `true`, `open` and `home` read as `1`;
   `off`, `false`, `closed`, `away`, `unavailable` and `unknown` read as `0`.
