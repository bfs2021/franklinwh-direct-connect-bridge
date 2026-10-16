# Targets

Direct Connect Bridge. Mirrors the Modbus Bridge page
[Targets](https://david2069.github.io/franklinwh-modbus-bridge/user/scheduler/targets/)
section for section.

The target says which gateway a schedule acts on. Here a schedule is bound to one gateway,
left on the default gateway, or (API only) set to run on every gateway. See also
[Multi-gateway and sites](../multi-gateway.md).

![Binding a rule to a gateway](../../images/scheduler/19-multi-gateway-binding.png)

## Pick a target

1. In **Add schedule** or **Edit**, find the gateway list next to **Priority** and **If busy**
   in the **Battery action** box. It is shown only when the bridge has more than one gateway.
2. Pick a gateway, or leave **Default gateway**.

<!-- @b TGT-21 ;; src: templates/tabs/scheduler.html:542-549, static/js/scheduler_tab.js:244-249 ;; untested ;; write: no ;; b: The gateway select appears only with more than one gateway; Default gateway stores gateway_id "" ;; test: browser: with one gateway the select is hidden; with two it lists both plus Default gateway -->

| Target | API | Acts on |
|---|---|---|
| a gateway | `gateway_id`: the gateway id | that gateway only, on its own tick |
| **Default gateway** | `gateway_id`: `""` | the default gateway (below) |
| every gateway (API only) | `gateway_scope`: `"all"` | each gateway on its own tick |

A schedule bound to a gateway is evaluated only on that gateway's tick, so its action goes to
that aGate. <!-- @b TGT-01 ;; src: scheduler.py:1978-1988 ;; tested: tests/test_scheduler.py::test_bound_schedule_fires_only_on_its_gateway ;; write: yes ;; b: A bound schedule is skipped on every other gateway's tick ;; test: — -->
A gateway's schedules are evaluated only while that gateway is enabled and its last poll is
fresh (three poll intervals, at least 90 s). A bound gateway that is offline or stale is
skipped with a debug log line only; nothing is sent and History shows nothing.
<!-- @b TGT-08 ;; src: scheduler_worker.py:94-104, scheduler_worker.py:156-160 ;; tested: tests/test_scheduler_worker.py::test_stale_gateways_are_not_passed_to_tick_at_all ;; write: yes ;; b: A disabled, never-polled or stale gateway is not evaluated at all, silently ;; test: — -->
A schedule bound to a gateway id that does not exist (deleted, renamed) never runs, and
nothing says so. <!-- @b TGT-22 ;; src: scheduler.py:1984-1986 ;; untested ;; write: yes ;; b: A gateway_id matching no registered gateway is skipped on every tick with no log ;; test: unit: schedule bound to "ghost"; tick two real gateways; assert no fire and decide on a warning -->

**Not in this bridge: Site and Service targets.** There is no utility-service target and no
"Site (all gateways)" choice in the form (#162). The closest is gateway scope *all*.

**Gateway scope "all" (API only).** With `"gateway_scope": "all"` the schedule is
evaluated by every gateway on its own tick. The form has no control for it. Since 0.5.2
(#157) saving from the form keeps it; before 0.5.2 the form turned it off. Any value other
than exactly `all` means one gateway. <!-- @b TGT-02 ;; src: scheduler.py:1979-1988, app.py:640-644, scheduler_worker.py:156-163 ;; untested ;; write: yes ;; b: gateway_scope all makes every eligible gateway (mocks included) evaluate the schedule on its own tick ;; test: unit: scope all schedule, tick gw1 and gw2; assert one fire per gateway -->
<!-- @b TGT-23 ;; src: app.py:3111-3127 ;; tested: tests/test_schedule_update_merge.py::test_a_form_save_keeps_api_only_fields ;; write: yes ;; b: A form save (which never sends gateway_scope) keeps gateway_scope all ;; test: — -->

## How a fan-out works

For gateway scope *all*, each gateway is handled on its own:

| Per gateway | Detail |
|---|---|
| Conditions | that gateway's own snapshot (see [Conditions → Scope](conditions.md#scope-which-gateways-values)) |
| Run | one run (occurrence) per gateway, with its own status and retries |
| Priority | one resource claim per gateway (`<gateway>/battery`), so gateways do not compete |
| Window end | each gateway's tick sends its own release when the window closes |
| History | one row per gateway, but the row does **not** name the gateway |

<!-- @b TGT-04 ;; src: scheduler.py:2084-2094, scheduler.py:2317-2329, db.py:1935-1962 ;; tested: tests/test_occurrences.py::test_the_same_rule_on_two_gateways_is_two_runs ;; write: yes ;; b: Each gateway gets its own occurrence row and its own resource claim for an all-scope rule ;; test: — -->
<!-- @b TGT-05 ;; src: scheduler.py:1989, scheduler.py:2014-2033 ;; untested ;; write: yes ;; b: The window-end release runs per gateway:entry key, to that gateway's host ;; test: unit: all-scope force on two gateways; close the window; assert a Release to each host -->
<!-- @b TGT-06 ;; src: db.py:1004-1023, scheduler.py:2458 ;; untested ;; write: no ;; b: History rows carry schedule id and name but no gateway ;; test: unit: all-scope fire on two gateways gives two identical fired rows; decide to add the gateway -->

!!! warning "Two gateways cannot run a force at the same time safely"
    The Modbus client (this bridge) supervises **one** force for the whole bridge. When a
    second gateway starts a force, the first gateway's time limit and target SoC stop being
    enforced; only its window-end release remains. See
    [Actions → What is written](actions.md#what-is-written). From a code read; unverified on
    hardware.

!!! warning "Stop, Pause and shutdown release the default gateway"
    **Stop** and the Pause API release through `FWH_MODBUS_HOST` or the **default gateway's**
    host, not the host of the gateway the force runs on. On a site with several gateways,
    **Stop** on a schedule bound to the second gateway releases the first one. A graceful
    shutdown and the start-up check for an interrupted dispatch also look only at the first
    gateway. From a code read. Issue #192. <!-- @b TGT-20 ;; src: app.py:3148-3174, app.py:3177-3204, app.py:3473-3480, app.py:1196-1204, app.py:973-977, app.py:1004-1023 ;; unclear ;; write: yes ;; b: Stop, Pause, shutdown release and boot reconcile use the default gateway host, not the dispatch's host ;; test: unit (API): dispatch row on host B, Stop calls execute("Release", host=B) (fails today) -->

A gateway that leaves (disabled, or its poll goes stale) while its force runs is no longer
evaluated, so its window-end release is not sent. The force keeps running until the
watchdog's time limit or target SoC ends it (if that gateway still holds the watchdog), or
until you release it. <!-- @b TGT-07 ;; src: scheduler_worker.py:156-160, scheduler.py:2014-2033, battery_control.py:92-110 ;; unclear ;; write: yes ;; b: A gateway skipped as stale gets no exit edge; only the in-memory watchdog can still end its force ;; test: unit: force running, then gateway stale past window end; assert a release is still sent (fails today) -->

**Run now** runs once, on one gateway, even for scope *all* (see below).

## Entries with no target id

A schedule left on **Default gateway** (`gateway_id` empty) runs on the default gateway's
tick only, so it does not run once per gateway. The default gateway is the
**first-registered** gateway in the bridge's memory. Nothing is stored or shown; deleting or
re-ordering gateways moves it (#182). <!-- @b TGT-10 ;; src: scheduler.py:1858-1866, scheduler.py:1987-1988, state.py:84-94 ;; untested ;; write: yes ;; b: An unbound schedule runs only when the tick's gateway is state.gateways()[0] ;; test: unit: two registered gateways, unbound schedule; assert it fires only on the first -->
In the same tick an unbound schedule claims that gateway's id, so it competes on priority with
schedules bound to that gateway. <!-- @b TGT-11 ;; src: scheduler.py:2088-2089 ;; untested ;; write: yes ;; b: An unbound schedule claims <tick gateway>/battery, the same resource as one bound to that gateway ;; test: unit: unbound and bound force entries on gw1 in one tick; assert one deferred -->

!!! warning "A disabled first gateway stops every unbound schedule"
    The default is the first-registered gateway whether or not it is enabled. A disabled
    gateway is not evaluated, and every other gateway refuses unbound schedules, so they run
    nowhere and History shows nothing. Bind them to a gateway (#182). <!-- @b TGT-17 ;; src: scheduler.py:1858-1866, scheduler_worker.py:96-97 ;; unclear ;; write: yes ;; b: The default-gateway test ignores enabled, so a disabled first gateway leaves unbound schedules unevaluated ;; test: unit: first gateway disabled, second enabled; unbound schedule never fires (fails today) -->

## In the form

- The gateway list shows the gateway's label (else its serial or id).
- **Not in this bridge: a mock warning.** The form does not warn when the picked gateway is a
  mock. For a mock, the scheduler skips the ratings read through the Modbus client (this
  bridge). <!-- @b TGT-18 ;; src: scheduler_worker.py:107-116, scheduler.py:1967-1969 ;; tested: tests/test_scheduler_worker.py::test_mock_gateways_skip_the_modbus_read ;; write: no ;; b: A mock gateway's tick passes an empty Modbus host, so no 702 ratings read ;; test: — -->
  Whether a force to a mock reaches anything depends on the mock's address answering SunSpec
  (**unverified**).
- **Test** under a condition block evaluates against the gateway selected in the top bar (or
  the default gateway in site view or with one gateway). **⋮ → Test against live** on a card
  always uses the default gateway's values, whatever gateway the schedule is bound to
  (see [Conditions → Test Verification](conditions.md#test-verification)). <!-- @b TGT-19 ;; src: static/js/scheduler_tab.js:606-613, static/js/scheduler_tab.js:921-931, app.py:3360-3369, app.py:3397-3402 ;; untested ;; write: no ;; b: Editor Test uses the top-bar gateway; Test against live reads get_state(), the default gateway ;; test: unit (API): /test on a schedule bound to gw2 uses gw2's state (fails today) -->
- **Import** points an entry whose gateway does not exist here at **Default gateway**, warns
  "gateway '…' not found — will use the default gateway", and creates it disabled. A Modbus
  Bridge entry with target `default` maps to **Default gateway**. <!-- @b TGT-14 ;; src: scheduler.py:852-854, scheduler.py:728-729, app.py:3294-3309 ;; tested: tests/test_scheduler.py::test_import_maps_modbus_automations_bundle ;; write: no ;; b: Import maps a default/unknown gateway to "" and creates the entry disabled ;; test: — -->

!!! warning "Run now uses the gateway selected in the top bar"
    With more than one gateway and one picked in the top bar, **⋮ → Run now** sends that
    gateway's id, and the bridge uses it **instead of** the schedule's own gateway. The
    action goes to the top-bar gateway. In site view, or with one gateway, it uses the
    schedule's gateway, else the default. From a code read. Issue #193.
    <!-- @b TGT-09 ;; src: static/js/scheduler_tab.js:616-631, static/js/app.js:880-885, app.py:3433-3436 ;; unclear ;; write: yes ;; b: The UI's Run now passes the top-bar gateway, which overrides the schedule's gateway_id ;; test: unit (API): POST /run?gateway=gw1 on a schedule bound to gw2 should act on gw2 or refuse -->

## On the timeline

The **Timeline** view draws every enabled schedule's planned windows, for all gateways, in
one list. It does not split by gateway, and the fire markers come from every gateway's
History. The tab asks for the timeline without a gateway, so the mode band and SoC line are the default gateway's. <!-- @b TGT-15 ;; src: app.py:3327-3358, scheduler.py:864-885, static/js/scheduler_tab.js:71-74 ;; untested ;; write: no ;; b: Timeline segments ignore the gateway; markers come from the whole log; the tab sends no gateway ;; test: unit (API): timeline?gateway=gw2 still lists a schedule bound to gw1 -->

Related pages: [Multi-gateway and sites](../multi-gateway.md),
[Priorities and conflicts](priorities.md), [Actions](actions.md).
