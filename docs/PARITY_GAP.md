# Feature-parity gap: Direct Connect Bridge vs Modbus Bridge vs FWHAI (REST + Home Assistant)

**Written 2026-10-16.** This compares each bridge's **REST API** and its **Home Assistant MQTT entities**, not MQTT entities alone. The earlier `docs/HA_CONTROL_GAP.md` compared HA entities only. It put the whole bridge-admin surface (schedules, tariffs, HA, notify, MQTT admin, settings, backups) "out of scope", so it missed the scheduler and other feature areas. This document covers them.

## §0 Sources and method

| Bridge | Version / commit | REST source | HA/MQTT source |
|---|---|---|---|
| **Direct** (subject) | `main` 45ea8c8, v0.4.9 | **OpenAPI generated** from `create_app().openapi()`: 232 operations (including `GET /`), including 36 `GET /api/cmd/<name>` reads registered in a loop. Line numbers are from `@app.<method>` in `src/franklinwh_direct_connect_bridge/app.py` (`D app:N`). | `publish/entities.py` (`D ent:N`): `ENTITIES` (18 sensors, ent:14-33) and `CONTROLS` (1 select and 3 switches, ent:46-56). The HA export of v0.4.5 shows 21 entities per device. |
| **Modbus Bridge (MB)** | `origin/main` = HEAD 38d794d, v0.2.7 (`git describe` v0.2.7-1) | **OpenAPI generated** from `franklinwh_bridge.main:app`, using the repo venv's interpreter read-only with a scratch data dir. Nothing was installed. 175 operations (including UI pages). Lines cite `src/franklinwh_bridge/api/<file>.py` (`mb/<file>:N`). | `publish/entities.py` (`mb/ent:N`), plus user-promoted SunSpec points (`publish/promoted_points.py`). Cross-checked against the HA MQTT diagnostics export of **v0.2.7** (65 entities). |
| **FWHAI** | 0.6.80 (scratchpad clone) | FastAPI. No OpenAPI run (dependencies not installed). Routes were grepped: 360 `@router.*` decorators, with prefixes resolved from `main.py:862-888` `mount(...)` (`fw/<file>:N`, files in `src/routes/`). | `src/models/entities.py` (`fw/ent:N`), plus HEMS forecast-load devices (`src/services/mqtt_publisher.py:863-958`). HA exports of v0.6.76 (90 and 103 entities) were checked. **No 0.6.80 export was present** in Downloads, so the "FranklinWH Cloud" files named in the brief were not found. |

**Method.** Every operation from the three route lists was assigned to a feature area, then to an operation (read / create / update / delete / execute / pause / resume / stop / test / export / import / history / timeline / stats). Every HA entity was assigned the same way. "—" means no route or entity was found.

**Gap for Direct** values:
- **none**: Direct covers the capability in both REST and HA wherever a reference does.
- **missing in REST**: a reference has a REST route and Direct does not.
- **missing in HA**: Direct has REST, and a reference publishes an HA entity that Direct lacks.
- **missing entirely**: a reference has it, and Direct has neither REST nor HA.
- **Direct-only**: no reference has it.

Rows marked "(inferred)" were not read from code line by line.

**Write-gating legend for Direct.**
- **W**: needs the `allow_writes` setting.
- **W+c**: also needs `confirm=true`.
- **cloud**: needs cloud credentials.
- **MBus**: goes over the Modbus client (this bridge) to the aGate Modbus TCP Server (:502).

**Naming.** "aGate Modbus TCP Server (:502)" is the aGate's listener, switched by `1205 der_comms`. "Modbus client (this bridge)" is a bridge's own connection to that listener.

---

## §1 Capability matrix

### 1.1 Monitoring and summary

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Monitoring | Dashboard summary / live snapshot | `GET /api/summary` (app:1647), `GET /api/live` (1345), `GET /api/gateways/{id}/summary` (2220), `GET /api/site/status` (2229) | — (state JSON feeds sensors) | `GET /api/status` (health:48), `GET /api/site/status` (gateways_api:95), `GET /api/gateways/{id}/points` (:1131) | — | `GET /api/gateways/{id}/summary` (phase9:130), `/data` (gateways:726), `/status` (:707), `/status/all` (:1017), `/telemetry/live_power` (:939) | — | none | |
| Monitoring | SoC | `GET /api/power` (2258), `/api/cloud/stats` (2276) | `State of Charge` (ent:15) | `GET /api/points` (admin:328) | State of Charge (mb/ent:103) | summary/data | State of Charge (fw/ent:106) | none | local 1301 |
| Monitoring | Grid / solar / battery / load / generator W | `GET /api/power`, `/api/energy/flow` (5588) | 5 power sensors and Generator Power (ent:16-21) | `GET /api/energy/flow` (energy_api:67) | Grid Power, Solar Power, Battery Power, Home Load, PV Total Power (mb/ent:126,314,756,772,786). No generator. | `/telemetry/live_power` | Battery/Solar/Grid Power, Home Load, Generator Power (fw/ent:117,152,178,200,213) | none | |
| Monitoring | Flow breakdown (solar→battery, grid→battery, solar→grid, battery→grid) | `GET /api/energy/flow` (5588) | — | `GET /api/energy/flow` | — | — | Solar Charging Battery, Grid Charging Battery, Solar Export to Grid, Battery Export to Grid (fw/ent:502-504,520) | missing in HA | derivable from 1301 |
| Monitoring | Run status / battery state text | in poll and `/api/cmd/device_states` | `Run Status` (raw number), `Battery State` (ent:31-32) | — | Battery State, Inverter State (mb/ent:166,409) | — | Battery Run Status, Runtime Mode, Operating Mode sensor (fw/ent:548,339,325) | missing in HA (text) | HA_CONTROL_GAP §1: raw `run_status` is still published |
| Monitoring | Temperatures | `GET /api/battery` (4570) | Ambient Temperature (ent:30) | points | Ambient, Cabinet, Battery Temperature (mb/ent:728,741,153) | `/batteries` (phase9:70) | Ambient Temperature (fw/ent:459); per-aPower Temperature (fw/ent:634) | missing in HA (battery/cabinet temp) | local 1105 |
| Monitoring | Relays (grid 1/2, PV 1/2, generator, black start, aPbox) | `GET /api/solar` (3652), `/api/cloud/power-info` (3771), `/api/cmd/relay_status` | — | — | — | data | 7 relay binary_sensors (fw/ent:447-453) | missing in HA | local 1707/1710 |
| Monitoring | Per-device (aPower) telemetry | `GET /api/battery` (4570), `/api/cmd/battery_modules`, `/battery_cells` | — | points | Battery N Power / Voltage / Temperature (mb/ent:269-296) | `/batteries` (phase9:70), `/batteries/debug` (:104) | Per-aPower HA device: SoC, SoH, Voltage, Current, Temperature, Heater (fw/ent:591-644) | missing in HA | local 1105/1107 |
| Monitoring | Raw point / register browser | `POST /api/raw` (2369, W+c for writes), `GET /api/raw/catalog` (2401), `GET /api/schema` (4652), `GET /api/catalog` (4658), 36 × `GET /api/cmd/<name>`, `POST /api/call/{cmd}` (4703) | — | `GET /api/models` (admin:199), `/api/catalog/points` (:227), `POST /api/models/{id}/read` (:235), `POST /api/models/refresh` (:299), `GET /api/points`, `/points/{id}` (:328,360), `GET/PUT /api/pics` (:927,935) | promoted points → sensors (promoted_points:60-123) | `GET /api/entities` (phase9:33) | — | none (REST). Missing in HA: user-promoted raw points | MB lets a user promote any point to an HA sensor |
| Monitoring | Point history / time series | `GET /api/metrics` (5562), `/api/metrics/info` (5678) | — | `GET /api/point-history/series` (point_history:137), `/config` GET/PUT (:98,112), `/storage` (:190) | — | `GET /api/metrics/timeline` (metrics:527), `/historical` (:619) | — | none | |
| Monitoring | Alarms / device events | `GET /api/cmd/event_block` (read) | — | `GET /api/alarm-events` (admin:451), `GET /api/events` (:484) | — | — | — | missing in REST (no event history store) (inferred) | Direct reads the event block live but keeps no alarm-event history |
| Monitoring | Web dashboards / e-ink | `GET /` (5869) | — | `GET /`, `/user` (ui:120,140) | — | `/view/{slug}`, `/dashboard/inkypi*` (admin:200-213), `/api/dashboard/*` (:374-387) | — | missing entirely (e-ink) | low priority |

### 1.2 Power flow, energy and history/metrics export

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Energy | Daily energy counters | `GET /api/power` | 6 `total_increasing` (ent:24-29) | `GET /api/energy/totals` (energy_api:195) | lifetime Grid Import/Export, Battery Charged/Discharged, Solar Total/Proximal (mb/ent:419,433,844,862,876,890) | data | Daily Solar, Grid Import/Export, Battery Charge/Discharge (fw/ent:128,139,164,518,519) | none | |
| Energy | Lifetime counters | `/api/cmd/energy_history` (inferred content) | — | totals | yes (above) | — | — | missing in HA (lifetime) | HA energy dashboard prefers lifetime counters (inferred) |
| Energy | Battery hours / runtime estimate | `GET /api/cloud/runtime` (3765) | — | `GET /api/energy/battery-hours` (energy_api:151) | — | — | — | missing in HA | |
| History | Metrics export | `GET /api/admin/metrics/export` (5812) | — | `GET /api/metrics/export` (admin:1054) | — | — | — | none | |
| History | Metrics import | — | — | `POST /api/metrics/import` (admin:1095) | — | — | — | missing in REST | |
| History | Metrics archive / retention | `GET /api/admin/storage` (5733), `POST /api/admin/vacuum` (5746) | — | `POST /api/metrics/archive` (admin:443), `GET/PUT /api/settings/metrics` (:532,547), `GET /api/stats/storage` (:436) | — | `POST /api/system/db/prune` (system:836), `/prune-preview` (:853), `/wal-status` (:873) | — | none (retention settings inferred to be in `/api/settings`) | |
| History | Cloud-side history | `GET /api/cloud/stats` (local re-shape) | — | — | — | `GET /api/metrics/cloud`, `/cloud/history` (metrics:233,274) | — | Direct-local by design | |

### 1.3 Battery and BMS

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Battery | Capacity total / available | `GET /api/battery`, `/api/apower-specs` (5315) | — | — | Total Capacity, Available Capacity (mb/ent:205,219) | `/batteries` | Total / Available Capacity, Battery Count, Batteries Online (fw/ent:496-499) | missing in HA | |
| Battery | SoH / battery health | `GET /api/battery` | — | — | State of Health, Battery Health (mb/ent:115,175) | `/batteries` | per-aPower SoH (fw/ent:602) | missing in HA | |
| Battery | Battery current / voltage | `GET /api/battery` | — | — | Battery Current (mb/ent:140) | — | Battery Current (fw/ent:523) | missing in HA | |
| Battery | Max charge / discharge rate | `GET /api/grid` (3945, from SunSpec 702 via Modbus client (this bridge)) | — | `GET /api/battery/limits` (admin:954), `/gateways/{id}/battery/limits` (gateways_api:1214) | Max Charge Rate, Max Discharge Rate (mb/ent:232,246) | — | Max Charge Power, Max Discharge Power (fw/ent:524,525) | missing in HA | 1701 `fhpRatePower` reads 0 on this firmware (HA_CONTROL_GAP) |
| BMS | Recording sessions (start / stop / status / list / get / delete) | `POST /api/battery/record` (4589), `/record/stop` (4616), `GET /record/status` (4621), `GET /api/battery/sessions` (4626), `GET /sessions/{id}` (4633), `DELETE` (4642) | — | — | — | `POST /gateways/{id}/bms/trigger` (gateways:417), `GET /bms/history` (:469), `POST /bms/record_task` (:477), `POST/GET /bms/sessions` (:491,505), `GET/DELETE /gateways/bms/sessions/{id}` (:510,523) | Battery Heater binary_sensor (fw/ent:514,644) | none (REST); missing in HA (heater state) | |

### 1.4 Operating mode and reserves

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Mode | Read mode | `GET /api/cloud/mode` (3753), `/api/constants/modes` (2997), `/api/cmd/mode_config`, `/mode_list` | Operating Mode sensor (ent:22) | points | Operating Mode sensor, Control Mode (mb/ent:906,918) | `GET /gateways/{id}/mode/current` (control:265), `/mode/tou-raw` (:277) | Operating Mode sensor (fw/ent:325) | none | |
| Mode | Set mode | `POST /api/mode` (4203, W+c), `POST /api/cloud/set-mode` (4376) | Operating Mode select (ent:48) | `POST /api/command` (ui:171), `POST /gateways/{id}/command` (gateways_api:1182), slug `operating_mode` (command_handler:365) | Operating Mode select (mb/ent:1036) | `POST /gateways/{id}/mode/set` (control:295), `POST /gateways/{id}/control` (:171) cmd `operating_mode` | Operating Mode select (fw/ent:365) | none | local 1727, verified. The HA select skips confirm and is not audited (HA_CONTROL_GAP §3.2) |
| Reserve | Read reserve SoC per mode | `GET /api/cloud/reserves` (3739), `/api/cmd/mode_soc` | — | points | Active Reserve SOC (mb/ent:1047) | `GET /gateways/{id}/mode/reserves` (control:271) | Emergency Backup Reserved SOC (fw/ent:409) | missing in HA | local 1726 read matches the cloud (METRICS_GAP_ANALYSIS:167) |
| Reserve | Write reserve SoC (Self / TOU) | `POST /api/cloud/reserve` (4516, W, **cloud**) | — | command slugs `self_reserve_pct`, `tou_reserve_pct` (command_handler:367-369) | Self-Consumption Reserve SOC, TOU Reserve SOC numbers (mb/ent:1058,1073) | `PATCH /gateways/{id}/mode/reserve` (control:308), control `battery_backup_reserve`, `min_discharge_soc`, `max_charge_soc` | Battery Self-Consumption SOC, Battery TOU Reserved SOC numbers (fw/ent:418,432) | missing in HA | **Local 1405 is accepted and discarded** (LOCAL_ONLY "other direction"). MB writes ext 15508/15509 over the aGate Modbus TCP Server (:502); whether TOU applies is unverified. FWHAI uses the cloud. A Direct HA number is feasible only with a cloud provider. |
| Reserve | Reserve change history | `GET /api/control-log` (4297) (`set_reserve` audit, app:4532) | — | schedule log | — | `GET /gateways/{id}/control/backup-history` (control:320) | — | none | |
| Mode | Emergency-backup duration / resume mode | — (`/api/cloud/set-mode` reports these as `not_applied_locally`) | — | — | — | control `emergency_backup_duration_type` | Emergency Backup Duration, Duration Type, Resume Mode (fw/ent:484-486) | missing entirely | cloud-only |
| Mode | Storm hedge | — | — | — | — | control `storm_hedge_enabled`, `storm_hedge_config` | Storm Hedge, Storm Decision Strategy, Storm Backup Lead Time (fw/ent:385,472,473) | missing entirely | FWHAI's own engine plus a weather feed. Not local. |
| Mode | Control locks | — (only `allow_writes` and per-call `confirm`) | — | role gate `_REQUIRE_CONTROL` | — | — (inferred: lock state is set via the HA switches) | Control Lock, Lock Grid Disconnect, Lock Operating Mode, Lock Battery Dispatch (fw/ent:289-316) | missing in HA | software interlocks (inferred from names) |

### 1.5 Scheduler (the area the earlier analysis missed)

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Scheduler | List rules (+ action catalogue incl. unavailable actions) | `GET /api/schedules` (3027) | — | `GET /api/schedules` (schedules_api:284), `GET /api/schedule/actions` (:663) | — | `GET /api/scheduler/jobs` (scheduler:81); `GET /api/automation/rules` (automation:299), `/rulebooks` (:357) | — | missing in HA | No reference publishes per-schedule entities either |
| Scheduler | Get one rule | — (list only) | — | `GET /api/schedules/{id}` (schedules_api:596) | — | — | — | missing in REST (minor) | |
| Scheduler | Create | `POST /api/schedules` (3081) | — | `POST /api/schedules` (:293) | — | `POST /api/scheduler/jobs` (scheduler:127) | — | none | |
| Scheduler | Update | `PUT /api/schedules/{sid}` (3096) | — | `PATCH /api/schedules/{id}` (:606) | — | `PUT /api/scheduler/jobs/{id}` (:179) | — | none | |
| Scheduler | Delete | `DELETE /api/schedules/{sid}` (3115) | — | `DELETE /api/schedules/{id}` (:646) | — | `DELETE /api/scheduler/jobs/{id}` (:242) | — | none | |
| Scheduler | Enable / disable | via `PUT` body `enabled` (scheduler.py:462 reads it) (inferred: no dedicated route) | — | via `PATCH` `enabled` (inferred) | — | `POST /api/scheduler/jobs/{id}/toggle` (:295) "Pause or resume"; `PUT /api/automation/rules/{id}/toggle` (automation:345) | — | missing in HA | An HA `switch` per schedule would be the natural entity |
| Scheduler | Run now (execute) | `POST /api/schedules/{sid}/run` (3401, W) | — | `POST /api/schedules/{id}/execute?force=` (:514) | — | `POST /api/scheduler/jobs/{id}/execute` (:262), returns trace id | — | missing in HA | MB `force` bypasses entry conditions. Direct `run` ignores the window. |
| Scheduler | Stop current run | `POST /api/schedules/{sid}/stop` (3128, W) | — | `POST /api/schedules/{id}/stop` (:527) | — | — | — | missing in HA | |
| Scheduler | Pause / resume a run | `POST /api/schedules/{sid}/pause` (3157), `/resume` (3186) | — | — | — | job toggle (pauses the job, not a run) | — | Direct-only (REST); missing in HA | Direct separates Stop from Pause (BR-18) |
| Scheduler | Test saved rule (dry-run conditions) | `POST /api/schedules/{sid}/test` (3336) | — | — | — | — | — | Direct-only | |
| Scheduler | Evaluate unsaved condition tree | `POST /api/schedules/evaluate` (3373) | — | `POST /api/scheduler/evaluate` (scheduler_api:121) | — | `POST /api/scheduler/evaluate` (scheduler:335) | — | none | |
| Scheduler | Condition sensors / constants | `GET/PUT /api/constants` (2990,3013) | — | `GET /api/sensors` (scheduler_api:65), `GET/PUT /api/automation/constants` (:93,103) | — | `GET /api/automation/home-load-fields` (automation:1593) | — | none | |
| Scheduler | Conflict / priority | per-rule `priority` and `conflict` fields (scheduler.py:635, 2037-2039) | — | `priority` 0-1000, `conflict` defer/override/wait (schedules_api:~105) | — | `PUT /api/automation/rules/priority` (automation:330) | — | none (no reorder route; minor) | |
| Scheduler | Presets / templates | `GET /api/schedules/presets` (3225) | — | — | — | Smart Dispatch reserved presets `GET /api/automation/presets/reserved` (automation:387); TOU presets (see 1.6) | TOU Preset Dispatches select (fw/ent:493) | none (REST) | Direct presets cover only what local can do (no force preset) |
| Scheduler | Export | `GET /api/schedules/export?fmt=native\|automations` (3231) | — | `GET /api/schedules/export` (:422) | — | — | — | none | Direct emits MB's `franklinwh-automations` schema too |
| Scheduler | Import (dry-run, created disabled) | `POST /api/schedules/import` (3246) | — | `POST /api/schedules/import` (:444) | — | — | — | none | |
| Scheduler | **Timeline** | `GET /api/schedules/timeline` (3304): windows, real mode band, SoC line, fire markers | — | `GET /api/schedules/timeline?day=` (:541): per-entry segments, any weekday | — | — (`GET /api/metrics/timeline` (metrics:527) is a power history, not a schedule) | TOU Dispatch Now / Next / Next Start / Next End / Remaining (fw/ent:565-571) | missing in HA ("active / next schedule" sensors). Missing in REST: preview of another weekday (minor; Direct shows today only) | |
| Scheduler | **Run history / log** | `GET /api/schedules/log` (3288) | — | `GET /api/schedules/log?schedule_id=&status=` (:494) | — | `GET /api/scheduler/history` (scheduler:325), `GET /api/automation/history` (automation:366) | — | missing in HA (last run / last result sensor) | |
| Scheduler | **Run queue / outcomes** | `GET /api/schedules/runs` (3220): ran, pending, missed | — | in log statuses (fired/gated/missed/executed/exit_condition_met) | Last Command Result (mb/ent:1024) | — | Dispatch Status, Active Dispatch (fw/ent:552,510) | missing in HA | |
| Scheduler | **Stats** | `GET /api/schedules/stats` (3212): runs, first, last, last failure | — | — | — | — | — | Direct-only | |
| Scheduler | Edit audit (structural) | `GET /api/control-log` (pause/resume entries, app:3183,3209) | — | schedule log includes `deleted` etc. (schedules_api:655) | — | `GET /api/scheduler/audit` (scheduler:314) | — | none | |
| Scheduler | Action: set mode | yes (`set_mode`, scheduler.py:37) | — | `mode` | — | rule actions | — | none | |
| Scheduler | Action: smart circuit | yes | — | — | — | rule actions (inferred) | — | none | |
| Scheduler | Action: off-grid | yes (`offgrid`) | — | — | — | (inferred) | — | none | |
| Scheduler | Action: reserve SoC | declared but **always skipped**: "no local write path… needs a cloud provider" (scheduler.py:1806-1808), even when `POST /api/cloud/reserve` works | — | `reserve_self`, `reserve_tou` (schedules_api:38-48) | — | rule actions (cloud) | — | **missing (scheduler cannot change reserve)** | Wire it to the same cloud path as `/api/cloud/reserve` when a provider is configured |
| Scheduler | Action: force charge / discharge / standby | yes (`force`, MBus) | — | `force_*`, `release` | — | Smart Dispatch | — | none | |
| Scheduler | Action: HA service / notify | `notify` action and HA service calls (scheduler.py:1800) | — | `ha_actions` kind entity / notify (schedules_api:~70) | — | notifications engine | — | none | |
| Scheduler | Target scope (gateway / service / site) | per-gateway | — | `target_type` gateway/service/site | — | per gateway | — | missing in REST (site / service targeting) (inferred) | |

### 1.6 Gateway TOU programme (aGate-side schedule, not the bridge scheduler)

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| TOU programme | Read | `GET /api/cloud/tou` (3746), `/api/cmd/tou_schedule` | — | — | — | `GET /gateways/{id}/schedule` (phase9:326) | TOU Dispatch Now / Next / Tariff Now / Next (fw/ent:565-576) | missing in HA | local read works |
| TOU programme | Write / push to gateway | — | — | — | — | `POST /schedule/set` (phase9:481), `/usage-type` (:553,571), `/tariff` GET/POST (:582,638), `/apply-tariff` (:748) | — | **missing entirely** | Local write unverified. FWHAI goes via the cloud. |
| TOU programme | Presets save / load / delete | — | — | — | — | `GET/POST /gateways/schedule/presets` (:817,824), `/{name}/load` (:993), `DELETE` (:1011) | TOU Preset Dispatches select (fw/ent:493) | missing entirely | |
| TOU programme | Snapshots / version history / restore | — | — | — | — | `GET /schedule/snapshots` (:1027), `DELETE` (:1047), `/prune` (:1064), `/restore` (:1084), `/save-as-preset` (:1109) | — | missing entirely | |
| TOU programme | Optimise / savings / health | — | — | — | — | `/schedule/optimise` (:851), `/calculate-savings` (:1175), `GET/POST /schedule/health` (:1218,1266) | — | missing entirely | |
| TOU programme | Utilities / tariff catalogue (cloud) | — | — | — | — | `/schedule/utilities` (:674), `/tariff-list` (:703), `/tariff-detail` (:726), `/tariff-profile` (:1364) | — | missing entirely | cloud catalogue |

### 1.7 Dispatch / battery command

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Dispatch | Force charge / discharge / standby / release, power W or %, duration, target SoC | `POST /api/battery/command` (3488, W, MBus), `POST /api/dispatch` (4835, delegates to MB or the library) | — | `POST /api/command`, `/gateways/{id}/command` slugs `battery_command*` (command_handler:323-349) | Battery Command select, Command Power, Command Power %, Command Duration, Target SoC (mb/ent:1090-1152) | `POST /gateways/{id}/control` `dispatch_*` (control:~100-140) | Dispatch Action, Dispatch Method selects; Dispatch Power, Duration, Target SOC numbers (fw/ent:395,488-491) | **missing in HA** (C4) | No local cmdType exists. Dispatch goes over the aGate Modbus TCP Server (:502) WSet. |
| Dispatch | Live command state | `GET /api/battery/command` (3468) | — | power_limits / state | WSet Enabled, Power Setpoint, Power Setpoint %, WSet Mode, HW Revert Timer / Remaining, SW Watchdog Remaining, Command Elapsed Time (mb/ent:928-1012) | `GET /gateways/{id}/dispatch/status` (gateways:907) | Active Dispatch, Dispatch Start / End / Remaining, Dispatch Status (fw/ent:510-513,552) | missing in HA | |
| Dispatch | **Outcome record** (sent / verified / not_effective / reasserted / released / superseded, requester) | partial: events go to the schedule log as `_batt` (app:3521-3524) and `store.record_dispatch` (app:3542). No REST that lists outcomes with verification state (inferred). | — | `GET /api/gateways/{id}/dispatch-outcomes` (gateways_api:1230) | Last Command Result (mb/ent:1024) | `GET /api/smart_dispatch/log` (sd:856), `/decision_chain` (:707), `/earnings` (:870) | — | **missing in REST and HA** | |
| Dispatch | Price-driven auto dispatch engine (Amber, matrix, simulate, forecast loads) | — | — | `GET /api/tariff/dynamic` (nem_api:160) | — | `/api/smart_dispatch/*`: config, schedules, matrix, actuators, eval, force, simulate, forecast, energy devices, lock / unlock (sd:232-1861); `PUT /api/automation/engine/mode` (automation:427) | HEMS Load devices: Power, Energy, Enabled switch, Active (mqtt_publisher:863-958) | missing entirely | FWHAI's own engine. Out of local scope. |

### 1.8 Smart circuits

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Circuits | On / off | `POST /api/circuits/{n}/power` (3712, W), `POST /api/cloud/smart-circuit/state` (4426) | Smart Circuit 1-3 switches (ent:50-55) | — | — | `POST /gateways/{id}/control` `smart_circuit_*` (control:221) | Circuit 1-3 switches (fw/ent:477-479) | none | local 1409, verified 2026-08-08 |
| Circuits | Read state / config | `GET /api/circuits` (3697), `/circuits/raw` (3675), `/api/cloud/smart-circuits` (2282), `/info` (2292) | via switch state | — | — | data | — | none | |
| Circuits | Metering (power, daily energy) | `GET /api/circuits/meter` (3684) | — | — | — | data | Circuit 1-3 Power, Daily Energy (fw/ent:231-271,540,541) | missing in HA | local 1411 |
| Circuits | Schedules write | `PUT /api/circuits/{n}/schedule` (2342) returns `discarded: true` | — | — | — | — (none found) | — | none (not possible locally) | **The aGate discards it locally** (live-tested 2026-09-14). Cloud / app only. |

### 1.9 Generator

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Generator | Read state / config | `GET /api/generator` (2302), `/raw` (2315) | Generator Power (ent:20) | — | — | data | Generator Power, Generator Relay, Generator Enabled (fw/ent:213,449,515) | missing in HA (enabled / relay) | |
| Generator | Run / mode | `POST /api/generator/mode` (2324, 409 if no generator) | — | — | — | control `generator_run` (control:30) | — | none (REST) | not exercised on real generator hardware |
| Generator | Enable, charge windows, exercise, SoC thresholds | `PUT /api/generator/enable` (3594), `/window/{n}` (3612), `/exercise` (3626), `/soc` (3639) | — | — | — | — | — | Direct-only | local 1901, verified 2026-09-14 |

### 1.10 Grid (limits, status, off-grid)

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Grid | Grid status / connection | `GET /api/grid` (3945), `/api/cmd/offgrid` | — | points | Grid Connection (mb/ent:399) | data | Grid Status, Grid Connection Status (fw/ent:509,556) | missing in HA | |
| Grid | Electricals (V, A, Hz, PF, VA, var, per phase) | `GET /api/grid`, `/api/cmd/power_electronics` | — | points; `GET /gateways/{id}/detect-phases` (gateways_api:1038) | Grid Voltage / Current, Frequency, Apparent / Reactive Power, PF, L1-L3 sets (mb/ent:328-713) | — | Frequency, Voltage (fw/ent:189,543) | missing in HA | MB values are from SunSpec |
| Grid | Import / export limits read | `GET /api/grid` | — | — | — | data | Grid Import / Export Limit numbers (fw/ent:481,482) | missing in HA (read sensors) | |
| Grid | Import / export limits write | `POST /api/grid/limits` (4062, W+c, `dry_run`) | — | — | — | `POST /gateways/{id}/profile/power` (phase9:182); control `grid_*_limit`, `grid_*_unlimited` | Grid Import / Export Limit numbers, Import / Export Unlimited switches (fw/ent:470,471,481,482) | missing in HA (owner: not in HA, C3 dropped) | Local 1701 write is **unverified**. FWHAI uses the cloud. |
| Grid | Go off-grid / reconnect | `POST /api/offgrid` (4216, W+c), `POST /api/cloud/grid-status` (4405) | — | — | — | `POST /gateways/{id}/profile/islanding` (phase9:199); control `off_grid_mode` | Off-Grid Mode select (fw/ent:375) | missing in HA (owner: not in HA) | local 1723, measured live 2026-10-15 |
| Grid | Grid compliance profile | `GET /api/cmd/grid_profile`, `/grid_policy` | — | `GET /api/pics` | — | `GET /gateways/{id}/compliance/{type}` (gateways:993) | Grid Compliance Profile (fw/ent:562) | missing in HA | |

### 1.11 aGate Modbus TCP Server (1205), Modbus client (this bridge), reboot

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| **aGate Modbus TCP Server (1205)** | Read enabled (SunSpec / IEEE 2030.5) | `GET /api/der-comms` (2262), `/api/cmd/der_comms` | — | — (`/api/gateway/test` (admin:158) only probes reachability) | WSet Enabled (related, different) | — | — | Direct-only | |
| **aGate Modbus TCP Server (1205)** | Enable / disable | `POST /api/der-comms` (4782, W; 409 to disable without `confirm`) | — | — | — | — | — | Direct-only | **Local is the only path** (LOCAL_ONLY §1). Disabling it takes MB and every other :502 client offline. No `_audit` call in this handler (app:4782-4814) (from grep), so the change does not reach `/api/control-log`. |
| Modbus client (this bridge) | Enable, host override, test | `GET/PUT /api/modbus` (4309,4325), `POST /api/modbus/test` (4357) | — | gateway CRUD, `POST /gateways/{id}/start` / `stop` / `restart` / `healthcheck` / `test` / `diagnose` (gateways_api:943-1094) | — | — | — | none | |
| Reboot | Reboot aGate | `POST /api/reboot` (4815, W+c) | — | — | — | — (`POST /api/system/restart` (system:218) restarts the add-on only) | — | Direct-only | local 1721 |
| Reboot | Restart the bridge or its workers | `POST /api/gateways/{id}/restart` (2132), `POST /api/health/workers/{name}/restart` (4929) | — | `POST /gateways/{id}/restart` (gateways_api:990) | — | `POST /api/system/restart` (system:218), `POST /system/processes/{name}/restart` (:186) | Last Restart, Integration Startup Time (fw/ent:528,529) | missing in HA (diagnostics) | |

### 1.12 Device info, firmware, network, discovery

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Device | Model / serial / identity | `GET /api/device/model` (3579), `/api/cloud/device-info` (3777), `/api/cmd/device_info`, `/agate_serial`, `/install_profile` | HA device registry (`device_info`, ent:181-200) | `GET /api/gateway` (admin:152) | device registry | `GET /gateways/{id}/profile` (phase9:115), `/profile/refresh` (:159); `/api/models/devices*` and `/accessories*` (models:119-241) | Model, Serial Number (fw/ent:464,530) | none (registry carries it) | FWHAI's serial sensor would need masking in any public export |
| Firmware | Versions (aGate, all devices) | `GET /api/firmware` (2266), `/firmware/all` (2419) | `sw_version` suffix (ent:197) | (inferred: SunSpec model 1) | — | data | Firmware Version, Software Version (Cloud), Update Available (fw/ent:461,465,466) | missing in HA (firmware and update sensors) | OTA 1501/1503 is local-only (LOCAL_ONLY §2) and is not exposed by any bridge |
| Network | Network state | `GET /api/network` (3829), `/api/cloud/network` (3782), `/api/cmd/network_interfaces`, `/wifi_config`, `/wifi_scan`, `/connectivity` | — | `GET /api/health/connectivity` (health:38) | — | `GET /gateways/{id}/network` (gateways:782); PUT is "NOT YET SUPPORTED" (:866) | WiFi Signal, Mobile Signal, Network Connection (fw/ent:456-458) | missing in HA | Signal strength has no local source (cloud 317/341) |
| Network | Ping / cloud reachability | `GET /api/network/ping` (3919), `/api/cloud/pop` (3908) | — | — | — | `GET /api/metrics/edge`, `/edge-pops` (metrics:390,400) | — | none | |
| Discovery | LAN scan / probe | `GET /api/gateways/scan/default` (2169), `POST /api/gateways/scan` (2190), `POST /api/probe` (1542) | — | `GET /api/setup/subnets` (setup:128), `POST /setup/scan` (:320), `GET /scan/{id}` (:345), `POST /setup/probe` (:362) | — | `POST /api/gateways/discover` (gateways:1117), `/discover/linked` (:1127), `/cloud/available` (:1145), `POST /gateways/linked` (:1311) | — | none | |
| Discovery | Discovery bundle per gateway | — | — | — | — | `GET /gateways/{id}/discovery.json` (gateways:1069) | — | missing in REST (minor) | |
| Timezone | Site / host timezone | `GET /api/site/timezone` (4144), `/host/timezone` (4131), `GET/POST /api/setup/timezone` (2774,2783) | — | `GET /api/system/timezone` (gateways_api:156), `POST /confirm` (:164) | — | — | Site Timezone (fw/ent:467) | missing in HA (minor) | |

### 1.13 Health, link history, workers

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Health | Health probe | `GET /api/health` (1364), `GET /api/version` (5839) | availability topic; Round-trip Latency (ent:23) | `GET /api/health` (health:23), `/api/stats` (admin:578) | availability | `GET /api/health` (main:891), `/health/detail` (metrics:28) | MQTT Status, Startup Time, Cloud Stale-Window Drops, Data Provider, Control Source (fw/ent:582,579,353,460,559) | missing in HA (bridge diagnostics beyond latency) | |
| Health | Link history | `GET /api/health/link` (1368), `/link/hourly` (1611) | — | `GET /gateways/{id}/link-stats` (gateways_api:1295) | — | `GET /api/metrics/api` (metrics:202), `/system/rate-limits` GET / PATCH / reset (gateways:1531-1616) | — | none | |
| Health | Workers / processes | `GET /api/health/workers` (4900), restart (4929) | — | gateway start / stop / healthcheck | — | `GET /api/system/processes` (system:150), restart | — | none | |
| Health | Poll interval | (inferred: in `/api/settings`) | — | (inferred: `/api/config`) | — | `GET/PATCH /api/system/poll-interval` (gateways:1626,1644) | — | unverified | |

### 1.14 Notifications

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Notify | Targets / devices CRUD | `GET /api/ha/notify-targets` (2512), `/api/ha/notify-devices` CRUD (2562-2607) | — | `GET /api/ha/notify-targets` (ha_api:173) | — | `/api/ha/devices` GET / POST / DELETE (ha:1062-1093), `/ha/instances/{id}/targets` (:1100), `/automation/notifications/targets` (automation:453) | — | none | |
| Notify | Triggers / settings | `GET/PUT /api/notify/triggers` (2662,2669) | — | schedule `ha_actions` kind=notify | — | `GET/PUT /automation/notifications/settings` (:463,499) | — | none | |
| Notify | Templates | — (inferred: message text lives inside triggers) | — | per-action title / message | — | `GET/PUT /automation/notifications/templates` (:560,574) | — | missing in REST (inferred) | |
| Notify | Cooldowns / dedup | — (inferred) | — | — | — | `GET/PUT /automation/notifications/cooldown-rules` (:843,854); audit `/cooldowns`, `/multi-emit`, `/shadow-decisions`, `/stale-window` (:778-822) | — | missing in REST (inferred) | |
| Notify | Test / broadcast | `POST /api/ha/notify-devices/test` (2614), `/broadcast` (2634), `POST /api/notify/triggers/test` (2681), `POST /api/notify/test` (5129) | — | `POST /api/ha/test` (ha_api:147) | — | `POST /automation/notifications/test` (:600), `/test-webhook` (:903), `/test-result` (:881), `/verify-yaml` (:679) | — | none | |
| Notify | Actionable callback / override | — | — | — | — | `POST /automation/notifications/callback` (:1026), `/override` (:1046), `/test-callback-path` (:930) | — | missing entirely | |
| Notify | Log / audit | `GET /api/notify/log` (2676) | — | schedule log | — | `/automation/notifications/audit` (:747), `/debug-log` (:836) | — | none | |

### 1.15 HA integration (instances, entities, MQTT publish, namespace)

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| HA | HA instances CRUD and test | `/api/ha/instances` GET / POST / PATCH / DELETE (2442-2466), `POST /api/ha/test` (2473) | — | `/api/ha/instances` GET / POST / PATCH / DELETE (ha_api:85-130), test (:147) | — | `/api/ha/instances` GET / POST / DELETE (ha:989-1055), `/ha/config` GET / POST (:242,273), `/ha/test`, `/enable`, `/disable`, `/generate-pin` (:292-357), `/ha/status` (:164) | — | none | |
| HA | Browse / expose HA entities | `GET /api/ha/entities` (2482), `POST /entities/expose` (2504) | — | `GET /api/ha/entities` (:186), `/domains` (:245), `POST /entities/expose` (:252) | — | `GET /api/ha/entities` (:374), `/entity-survey` (:915), `/ha/history` (:445) | — | none | |
| HA | Dashboard YAML | `GET /api/ha/dashboard-yaml` (4231) | — | `GET /api/ha/dashboard-yaml` (:293) | — | `GET /api/ha/dashboard-yaml` (:887) | — | none | |
| HA | Analyse / repair / rename entities | — | — | — | — | `GET /api/ha/analyse` (:548), `POST /repair` (:668), `GET /entity-rename/plan` (:827), `POST /apply` (:840) | — | missing in REST | |
| HA | Conflicts with other integrations | `GET /api/mqtt/conflicts` (4875) | — | — | — | `GET /api/ha/conflicts` (:953), `POST /conflicts/disable` (:968) | — | none (detect only; no disable) | |
| MQTT | Broker config read / write | `GET /api/mqtt/config` (4862) (write inferred via `PUT /api/settings`) | — | `GET/PATCH /api/mqtt/config` (mqtt_api:67,83) | — | `GET/PATCH /api/mqtt/config` (mqtt:565,589), `/enable`, `/disable`, `/generate-pin` (:1255-1294) | — | none (inferred) | |
| MQTT | Broker auto-detect | `GET /api/mqtt/supervisor` (4953), `POST /enable` (4970) | — | `GET /api/mqtt/detect-broker` (:239) | — | `GET /api/mqtt/detect-broker` (:1214), `/service-status` (:1186) | — | none | |
| MQTT | Connection status / reconnect / test | (inferred: in `/api/summary`) | — | `GET /status` (:170), `POST /reconnect` (:198), `POST /test` (:251) | — | `GET /status` (:62), `POST /reconnect` (:631), `POST /test` (:1321) | — | missing in REST (reconnect, test) | |
| MQTT | Republish / unpublish discovery | `POST /api/mqtt/republish` (5103), `/unpublish` (5112) | — | `POST /api/mqtt/publish` (:218), `/unpublish` (:228) | — | `POST /api/mqtt/publish` (:649), `/unpublish` (:676), `/discovery/clear` (:207), `/discovery/auto` GET / POST (:155,164) | — | none | |
| MQTT | Orphans / ghosts cleanup | `GET /api/mqtt/orphans` (4998), `POST /purge` (5012), `GET /api/mqtt/discover` (5121) | — | — (tombstones on republish, mqtt_publisher:700) | — | `GET /retained/orphans` (:111), `POST /retained/clear` (:253), `GET /discovery/ghosts` (:172) | — | none | |
| MQTT | Entity groups (opt in / out) | `GET/PUT /api/mqtt/groups` (5051,5057): 5 fixed groups (ent:59-65) | — | `/api/groups` CRUD, members, points (groups_api:73-251): user-defined groups and promoted points | — | — | — | missing in REST (custom groups, promoted points) | |
| MQTT | Published entity list | `GET /api/mqtt/entities` (5069), `GET /api/ha/published` (3563) | — | `GET /api/groups/entities` (:81), `/disabled` (:107) | — | `GET /api/entities` (phase9:33) | — | none | |
| MQTT | Topic browser / inspector | — | — | `GET /api/mqtt/topics` (:281) | — | `GET /topics` (:439), `/inspector` (:470), `WS /api/ws/mqtt` (:1067) | — | missing in REST | |
| MQTT | **Namespace / prefix change and migration** | — (`mqtt_prefix` setting, config.py:53) | — | `GET/POST /api/mqtt/namespace` (:139,147) | — | `GET/PUT /api/mqtt/prefix` (:741,816), `/prefix/scan` (:841), `POST /migrate-prefix` (:910), `/device-id-scheme` (:285,301), `/device-name` (:324,339), `/slug-aliases` (:382,397) | — | missing in REST | |

### 1.16 Tariffs, costs, forecast, weather

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Tariff | Utilities / services CRUD | `/api/utilities` CRUD (1870-1895) | — | `/api/services` CRUD (gateways_api:518-586), `/switch-plan` (:334) | — | `/api/utility-services` CRUD (pricing:475-604), `/gateways` (:621), `/phase` (:648), `/api/gateway-sites` (:663) | — | none | |
| Tariff | Tariff plans CRUD, validate | `/api/tariffs` CRUD (1906-1936), `POST /validate` (1945) | — | `/api/tariff/plans` GET / POST / PATCH (tariff_api:256-299), `POST /tariff/validate-rates` (gateways_api:490) | — | `/utility-services/{id}/windows` (pricing:1152-1218), `/tariff-profile` (:1244) | — | none | |
| Tariff | Standing charges | (inferred: inside the tariff model) | — | (inferred) | — | `/utility-services/{id}/standing-charges` GET / POST / DELETE (:561-593) | — | unverified | |
| Tariff | Import / export | `GET /api/tariffs/{id}/export` (1966), `POST /api/tariffs/import` (1983) | — | `GET /services/{id}/export` (:383), `POST /services/import` (:411) | — | `GET /pricing/tariffs/export` (:1296), `POST /import` (:1314) | — | none | |
| Costs | Billing overview / history | `GET /api/billing/overview` (2032), `/history` (2068) | — | `GET /api/tariff/overview` (tariff_api:61), `/history` (:200), `/history.csv` (:323), `/services/{id}/history-count` (gateways_api:511) | — | `GET /pricing/dashboard` (:746), `/pricing/history` (:211), `/utility-services/{id}/audit` (:1235) | — | missing in REST (CSV export) | |
| Costs | Close period / import history | `POST /api/billing/close` (2086), `/import` (2098), `/import-modbus` (2109) | — | — | — | — | — | Direct-only | `import-modbus` pulls MB history |
| Costs | Cost / price sensors in HA | — | — | — | — | — | TOU Dispatch Tariff Now / Next (fw/ent:575,576) | missing in HA | |
| Price | Spot / dynamic prices | `GET /api/tariff/spot` (4093) | — | `GET /api/tariff/spot` (nem_api:76), `/spot/settings` GET / PUT (:110,116), `/dynamic` (:160) | — | `/api/pricing/status`, `/current`, `/forecast`, `/config`, `/test`, `/refresh`, `/models*`, `/amber/*` (pricing:90-1130) | — | missing in REST (price forecast, dynamic tariff, provider models) | |
| Solar fcst | Forecast and location | `GET /api/solar/forecast` (5643), `POST /api/solar/sync-location` (5659) | — | `GET /api/solar/forecast` (solar_api:76), `/settings` GET / PUT (:114,120), `POST /location/from-ha` (:133) | — | `/api/solar/config`, `/status`, `/test`, `/forecast`, `/actuals`, `/sync_location` (solar:147-225,1450) | — | none (settings inferred in `/api/settings`) | |
| Solar | Third-party PV (Enphase, DPEL, sources) | — | — | — | — | `/api/solar/enphase/*`, `/gateways/{id}/sources*`, `/topology`, `/utility-link`, `/capabilities` (solar:362-1532) | Remote Solar PV1 / PV2, MPPT Active Power / Status (fw/ent:532-537) | missing entirely | MB has Solar Remote 1 / 2 and Solar Proximal sensors (mb/ent:800-828); Direct reads `/api/solar` (3652) but does not publish these |
| Weather | Weather config / current / forecast | — | — | — | — | `/api/weather/config` GET / PUT, `/current`, `/forecast`, `/test` (weather:90-812) | — | missing entirely | FWHAI only; feeds storm hedge |

### 1.17 Users, auth, settings, backup, logs, audit, setup, multi-gateway

| Area | Capability / operation | Direct REST | Direct MQTT/HA | MB REST | MB MQTT/HA | FWHAI REST | FWHAI MQTT/HA | Gap for Direct | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Auth | Login / logout / session | — (no auth; HA ingress path only, app:5858) | — | `POST /api/auth/login` / `logout`, `GET /session-status`, `/me` (auth:255-416) | — | `POST /api/security/login` / `logout`, `GET /status`, `POST /setup` (security:131-462) | — | **missing entirely** | Write safety relies on `allow_writes` and `confirm` only |
| Auth | Users CRUD and roles | — | — | `/api/users` CRUD (users_api:70-142); roles admin / control / viewer (main:1187, `_REQUIRE_CONTROL`) (inferred role names) | — | `/api/security/users` CRUD, change-password, reset-mfa (security:568-720) | — | missing entirely | |
| Auth | Password / MFA | — | — | `POST /api/auth/password` (auth:384) | — | `POST /api/security/change-password`, `/totp/setup`, `/verify`, `/disable` (account:32-148) | — | missing entirely | |
| Auth | **API tokens** | — | — | — | — | `POST /api/security/tokens` (security:473), `DELETE /tokens/{id}` (:502) | — | missing entirely | Needed for safe HA `rest_command` use of the scheduler (Direct's #128) |
| Auth | Sessions / auth audit | — | — | `GET /api/auth/sessions` (:430), revoke (:438), `GET /auth/events` (:451) | — | `GET /api/system/security-audit-logs` (system:134) | — | missing entirely | |
| Auth | TLS certificates | — | — | — | — | `POST /api/security/certificates` (:513) | — | missing entirely | |
| Settings | Settings read / write | `GET/PUT /api/settings` (5146,5219), `/api/constants`, `/api/system-setup` GET / PUT (2971,2979), `/api/integrations` GET / PUT (1503,1525), `/api/providers` (1353), `/api/capabilities` (4473) | — | `GET /api/config/{section}`, `PUT /api/config/{key}` (admin:91,110), `/api/modules` GET / PATCH (modules_api:27,39) | — | `GET /api/config/safe` (mqtt:30), `/api/system/features` GET / POST (system:312,426), `/instance_label` (:233,240), `/map/basemap` (map:57,71) | — | none | |
| Backup | Create / list / download / delete / restore | `POST /api/admin/backup` (5756), `GET /backups` (5775), `GET /backup/{n}` (5779), `DELETE` (5786), `POST /restore` (5794, W+c) | — | `POST /backup/create` (admin:981), `GET /list` (:996), `POST /restore` (:1019), `GET /download/{n}` (:1037) | — | `GET /api/system/backups` (system:522), `POST /run` (:551), `DELETE` (:568), `GET /probe` (:587), `POST /restore` (:652) | — | none (FWHAI probe is extra) | |
| DB | DB browser / query | — | — | — | — | `GET /api/system/db/tables*` (system:720,789), `POST /db/query` (:933) | — | missing entirely (low priority; risky) | |
| Logs | Logs | `GET /api/logs` (5531) | — | `GET /api/logs` (admin:587) | — | `GET /api/logs`, `/recent`, `/startup`, `/file`, `/logs/settings` GET / PATCH (metrics:82-504) | — | missing in REST (log-level setting) | |
| Audit | Control audit trail | `GET /api/control-log` (4297) | — | `GET /dispatch-outcomes`, schedule log, `GET /api/disclaimer/acks` (disclaimer_api:129) | — | `GET /api/system/audit-logs` (system:115), `/api/scheduler/audit` | — | none (but HA-path writes and the aGate Modbus TCP Server (1205) write are not audited; see §4) | |
| Support | Support info / diagnostics bundle | `GET /api/support-info` (5331) | — | `GET /api/support/info` (support_api:32), `POST /gateways/{id}/diagnose` (gateways_api:1094) | — | `GET /api/diag` (mqtt:39), `/system/dependencies` (system:80), telemetry (:1005-1072) | — | none | |
| Disclaimer | Show / acknowledge | `GET /api/disclaimer` (5472), `POST /ack` (5511) | — | `GET/POST /api/disclaimer`, `/acks` (disclaimer_api:64-129) | — | — | — | none | |
| Docs | In-app guide | `GET /api/guide` (1258) | — | OpenAPI description | — | `GET /docs`, `/docs/{name}` (docs:153,173) | — | none | |
| Setup | Setup wizard state | `GET /api/setup` (2743), `POST /state` (2750), `/expected` (2762), `/cloud` (2817), `GET /ha-checks` (2842), `/capabilities` (2957) | — | `GET/POST /api/setup/state` (setup:111,118), `/connect` (:400), `/use-ha` (:539), `/publish-to-ha` (:557), `/checklist` (:585), `/accounts` (:682) | — | `GET /api/setup/state` (setup:499), `/prefix` (:534), `/complete` (:568), `/reopen` (:580), `/skip` (:601), `POST /api/system/onboard` (gateways:112) | — | none | |
| Multi-GW | Gateways CRUD | `/api/gateways` GET / POST / PATCH / DELETE (1692-1773) | one HA device per gateway (ent:165-179) | `/api/gateways` CRUD incl. `GET /{id}` (gateways_api:702-915) | per gateway | `/api/gateways` CRUD (gateways:273-621), start / stop / poll (:660-685) | per gateway | none | |
| Multi-GW | Sites / meters | `/api/sites` CRUD (1790-1814), `/api/meters` CRUD (1825-1856) | — | `GET/PATCH /api/site` (gateways_api:88,108) | — | `/api/gateway-sites` (pricing:663) | — | none | |
| Mocks | Mock / demo gateway | `POST /api/gateways` with `is_mock`, `mock_seed`, `mock_units` (app:396-416) | mock publishes only if asked | `POST /api/setup/demo` (setup:462) | — | — (`mock_topology.py` exists, no route found) (inferred) | — | none | |
| Persona | Usage persona detection | — | — | — | — | `/api/persona*` (persona:32-131) | — | missing entirely (low priority) | |
| Terminal | Shell execute | — | — | — | — | `POST /api/terminal/execute` (terminal:15) | — | missing entirely (do not add) | security risk |

---

## §2 Prioritised gap list for Direct (largest user-visible gaps first)

**A. Scheduler and dispatch in Home Assistant**

1. **No scheduler in HA at all.** Direct has the richest scheduler REST of the three: CRUD, run, stop, pause, resume, test, evaluate, presets, import/export, timeline, log, runs, stats. Yet it publishes zero schedule entities. The references publish none either. FWHAI only has TOU Now/Next sensors and a TOU Preset select.
   - *Proposal:* per-schedule `switch` (enabled), `button`s (Run now / Stop / Pause / Resume), and `sensor`s (state: idle / active / paused / missed; next fire; last result).
   - Also site-level sensors: Active Schedule and Next Schedule (start/end), as in FWHAI fw/ent:565-571.
2. **Battery command / dispatch not in HA (C4).** Both MB (mb/ent:1090-1152) and FWHAI (fw/ent:395,488-491) publish it.
   - *Proposal:* a Battery Command select plus Power, Duration and Target-SoC numbers backed by `POST /api/battery/command`.
   - Add status sensors (active, remaining, setpoint) from `GET /api/battery/command`.
3. **No dispatch outcome ledger.** MB `GET /gateways/{id}/dispatch-outcomes` (gateways_api:1230) records sent / verified / not_effective / released / superseded and who asked.
   - *Proposal:* `GET /api/battery/outcomes` over `store.record_dispatch`, with a verification state.
   - Add a "Last Command Result" HA sensor.
4. **The scheduler's reserve-SoC action is always skipped** (scheduler.py:1806), even when the cloud path behind `POST /api/cloud/reserve` is configured. MB schedules can set reserves.
   - *Proposal:* route `reserve_soc` through the cloud provider when one is configured. Otherwise keep the skip and its reason.

**B. Reserves and mode in HA**

5. **Reserve SoC not in HA.** Both references publish read and write.
   - *Proposal:* an Active Reserve sensor from local 1726. Add Self / TOU reserve `number`s **only when a cloud provider is configured**, because local 1405 is discarded.
6. **Mode select bypasses confirm and audit.**
   - *Proposal:* write an `_audit` entry for HA-originated mode changes.
   - Owner to decide whether confirm applies (HA_CONTROL_GAP §3.2).

**C. Gateway TOU programme (FWHAI-only today)**

7. **TOU programme write, presets, snapshots, optimise, savings, health** (phase9:326-1364). Direct only reads (`/api/cloud/tou`).
   - *Proposal:* first a read-only HA "TOU now/next" set from the local 1726/1408 read.
   - Then investigate whether a local TOU write exists. Otherwise offer the write via the cloud provider.

**D. Read-only HA sensors that Direct already reads over REST** (cheap; no new device work)

8. **Grid:** Grid Status / Connection; electricals (V, Hz, A, PF); import/export limit sensors.
9. **Relays:** 7 binary_sensors (1707/1710).
10. **Smart circuits:** per-circuit Power and Daily Energy (1411).
11. **Battery:** capacity total/available, SoH, current, aPower count/online, per-aPower devices, heater, max charge/discharge rate.
12. **Run status as text**, generator enabled/relay, firmware versions, update available, flow breakdown sensors, lifetime counters, battery hours.

**E. Security**

13. **No auth, users, roles or API tokens** (MB auth:255-451, users_api; FWHAI security:131-720, account). HA automations driving the scheduler over REST (#128) currently need an open, unauthenticated write API.
    - *Proposal:* API tokens with at least a read / control / admin split, and HA-ingress bypass.

**F. HA / MQTT administration**

14. **Namespace / prefix change with migration** (MB mqtt_api:139-147; FWHAI mqtt:741-910).
    - *Proposal:* `GET/POST /api/mqtt/namespace` that tombstones old discovery and republishes.
15. **MQTT reconnect, test and topic browser** (MB mqtt_api:198,251,281).
    - *Proposal:* add `POST /api/mqtt/reconnect`, `POST /api/mqtt/test` and `GET /api/mqtt/topics`.
16. **Custom entity groups and promoted raw points** (MB groups_api, promoted_points).
    - *Proposal:* allow any `/api/cmd` field to be promoted to a diagnostic sensor.
17. **HA entity analyse / repair / rename** (FWHAI ha:548-840).
    - *Proposal:* lower priority. Only the rename plan matters if the namespace changes.

**G. Scheduler REST polish**

18. **`GET /api/schedules/{sid}`** for a single rule (MB :596).
19. **Timeline for another weekday** (MB `?day=`).
20. **Execute with `force`** to bypass conditions (MB :514).
21. **Site / service targeting** (MB `target_type`).
22. **Priority reorder** route (FWHAI automation:330).

**H. Tariffs and pricing**

23. **Billing history CSV** (MB tariff_api:323).
24. **Price forecast and dynamic tariff** (MB nem_api:160; FWHAI pricing:184).
25. **Price / cost HA sensors**, e.g. tariff now/next.
26. Standing charges, if not already in the tariff model (unverified).

**I. Ops**

27. **Alarm / event history** store and route (MB admin:451,484).
28. **Metrics import** (MB admin:1095).
29. **Log-level setting** (FWHAI metrics:490-504).
30. **Bridge diagnostic HA sensors:** MQTT status, last restart, startup time, data provider.

**J. Not proposed** (cloud-only or FWHAI engines)

Emergency-backup duration / resume, storm hedge, weather, smart dispatch, Enphase / DPEL, persona, WiFi / mobile signal, terminal, DB query, e-ink dashboards, actionable notification callbacks.

Off-grid and grid-limit writes in HA: **owner decision: not in HA**.

---

## §3 What Direct has that the others don't

- **aGate Modbus TCP Server (1205) enable/disable** (`GET/POST /api/der-comms`, app:2262,4782). Local is the only path, and it gates MB's whole control plane.
- **Reboot the aGate** (`POST /api/reboot`, 1721).
- **Generator configuration:** enable, charge windows, exercise schedule and SoC thresholds (app:3594-3639).
- **Full local read surface:** 36 `GET /api/cmd/<name>`, `POST /api/call/{cmd}`, `/api/raw` with a catalogue, `/api/schema`, `/api/catalog`.
- **Cloud-compatible local endpoints:** `/api/cloud/*` re-shaped from local reads, needing no cloud.
- **Smart circuits without the cloud** (1409 RMW, verified), with HA switches.
- **Off-grid locally** (1723) and grid limits locally (1701, unverified).
- **Scheduler extras:** Pause / Resume distinct from Stop; per-rule `test`; `stats`; the `runs` queue (ran / pending / missed); presets limited to locally possible actions; a timeline that overlays the real mode band, SoC line and fire markers; export in MB's `franklinwh-automations` format for interop.
- **Firmware for all devices** (`/api/firmware/all`).
- **BMS recording sessions** (FWHAI has an equivalent; MB has none).
- **Billing extras:** period close, history import, and import from MB (`/api/billing/import-modbus`).
- **Sites and meters CRUD.**
- **Link health:** hourly link history and worker restart.
- **MQTT operations:** broker conflict detection across all three bridges' devices (`/api/mqtt/conflicts`), orphan purge, Supervisor broker auto-enable.
- **Mock gateways via REST**, with HA publishing off by default.
- **Network:** ping and cloud POP checks.
- **`/api/apower-specs`**, and a per-gateway HA device name.

---

## §4 Open questions / unverified

1. **FWHAI 0.6.80 HA export was not available.** The brief's "FranklinWH Cloud" files are not in Downloads. FWHAI HA columns come from **code** (`src/models/entities.py`), which may publish conditionally (`get_entities_for_profile`). Which entities 0.6.80 actually publishes on this site is unverified.
2. **FWHAI REST was grepped, not generated.** Paths assume `mount(..., prefix="/api")` from main.py:862-888. Routers with their own prefix (solar, weather, map) were mounted without one, and `smart_dispatch` was mounted with `/api/smart_dispatch`.
3. **Direct enable/disable of a schedule** is assumed to go via `PUT` with `enabled`; there is no dedicated route. MB's `PATCH` is assumed to do the same. Not read line by line.
4. **No audit entry for the aGate Modbus TCP Server (1205) write** (`POST /api/der-comms`). Inferred from no `_audit(` call in app:4782-4814. The `/api/control-log` docstring's "Modbus toggle" is the Modbus client (this bridge) flag (`modbus_toggle`, app:4338).
5. **Direct dispatch record.** `store.record_dispatch` exists (app:3542), but no route was found that lists it. A route may exist under another name.
6. **MB reserve writes** (ext 15508/15509) over the aGate Modbus TCP Server (:502). That the TOU reserve applies is unverified (HA_CONTROL_GAP §3.4).
7. **Local TOU programme write** (1726/1408 family) is untested. Whether Direct could match FWHAI's TOU editing without the cloud is unknown.
8. **Local grid-limit write (1701)** is still marked UNVERIFIED in code.
9. **Settings-backed items** were not checked field by field and may already be in `GET/PUT /api/settings`: poll interval, retention, MQTT broker write, spot / solar settings, standing charges.
10. **Role names in MB** (admin / control / viewer) are inferred from `require_role("admin")` and `_REQUIRE_CONTROL`.
11. **Direct HA entity count.** Code defines 18 sensors and 4 controls (22). The v0.4.5 export shows 21 per device. The difference is unexplained, possibly the circuit count.
12. **One site, one firmware, one export set**, as in all earlier analyses. Treat reference entity behaviour as candidate evidence only.
