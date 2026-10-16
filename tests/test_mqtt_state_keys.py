"""#96 — every Home Assistant entity's template key is in the state the poller publishes.

Before 0.4.3 the poller published the raw ``summary["power"]`` dict, while the discovery
templates read the names ``entities.build_state`` produces — a function only the tests
called. 8 of the 21 entities (daily kWh, ambient temperature, battery state) never had a
value in Home Assistant, on real gateways and mocks alike. The old tests passed because
they called ``build_state`` directly; these build the payload the way the POLLER does,
from a real poll of the library's in-process Emulator.
"""
import pytest

from franklinwh_direct_connect_bridge import client, config, mockgw
from franklinwh_direct_connect_bridge.publish import entities

#: Read from the smart-circuit config (1409), which the poll does not fetch. Publishing
#: their state needs an extra device read per poll — a separate change (#96 follow-up).
NOT_IN_POLL = {"circuit_1_on", "circuit_2_on", "circuit_3_on"}


@pytest.fixture
def mock_summary():
    host = mockgw.start_mock("t96", seed=4242, units=1)
    try:
        yield client.summary(config.get_settings(), host, mock=True)
    finally:
        mockgw.stop_mock("t96")


def test_the_poll_succeeds(mock_summary):
    assert mock_summary.get("ok") is True, mock_summary.get("error")


def test_every_sensor_template_key_is_published(mock_summary):
    st = entities.state_payload(mock_summary)
    missing = [e["key"] for e in entities.ENTITIES if e["key"] not in st]
    assert not missing, f"entities whose template key is never published: {missing}"


def test_published_values_are_real_values_not_none(mock_summary):
    """A key that is present but always None is the same defect in disguise."""
    st = entities.state_payload(mock_summary)
    nones = [e["key"] for e in entities.ENTITIES if st.get(e["key"]) is None]
    assert not nones, f"published as null: {nones}"


def test_every_control_state_key_is_published_except_the_unpolled_circuits(mock_summary):
    st = entities.state_payload(mock_summary)
    missing = [c["state_key"] for c in entities.CONTROLS
               if c["state_key"] not in st and c["state_key"] not in NOT_IN_POLL]
    assert not missing


def test_daily_energy_maps_from_the_raw_counters():
    st = entities.state_payload({"power": {"kwh_sun": 22.4, "kwh_uti_in": 0.04,
                                           "kwh_uti_out": 4.7, "kwh_fhp_chg": 11.8,
                                           "kwh_fhp_di": 1.3, "kwh_load": 5.8,
                                           "battery_w": -1500},
                                 "battery": {"t_amb": 27.3}, "latency_ms": 12})
    assert st["solar_today_kwh"] == 22.4 and st["grid_export_today_kwh"] == 4.7
    assert st["battery_charge_today_kwh"] == 11.8 and st["load_today_kwh"] == 5.8
    assert st["ambient_temp_c"] == 27.3 and st["battery_status"] == "charging"
    assert st["kwh_sun"] == 22.4          # raw keys kept for the bridge's own UI


def test_unknown_values_stay_absent_rather_than_invented():
    st = entities.state_payload({"power": {}, "latency_ms": None})
    assert "ambient_temp_c" not in st and "battery_status" not in st
