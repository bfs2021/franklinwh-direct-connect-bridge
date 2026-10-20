"""#233 / #248: the cloud status loop logs in once, backs off on failure, and never guesses an aGate.

The library's network edges (PasswordAuth's login, the Client's HTTP calls) are replaced
with fakes; the bridge code under test is real."""
import pytest

pytest.importorskip("franklinwh_cloud")
import franklinwh_cloud.auth as fauth  # noqa: E402
import franklinwh_cloud.client as fclient  # noqa: E402
import franklinwh_cloud.wrapper as fwrapper  # noqa: E402

from franklinwh_direct_connect_bridge import cloud_status as cs  # noqa: E402


class _Auth:
    logins = 0

    def __init__(self, email, password, *a, **kw):
        self.email, self.password, self.info = email, password, None

    async def get_token(self, force_refresh=False):
        if self.info and not force_refresh:
            return self.info["token"]
        _Auth.logins += 1
        if self.password == "wrong":
            raise RuntimeError("401 invalid credentials")
        self.info = {"token": "t"}
        return "t"


class _Stats:
    class current:
        run_status, tou_mode, effective_mode, run_status_desc = 0, 0, "Self", ""


class _Client:
    gateways = ["10060006A02F00000001"]
    bound: list = []

    def __init__(self, auth, gateway, **kw):
        self.auth, self.gateway, self.session = auth, gateway, None
        _Client.bound.append(gateway)

    async def get_home_gateway_list(self):
        return {"result": [{"id": g} for g in _Client.gateways]}

    async def get_stats(self, **kw):
        assert self.gateway != "placeholder", "a gateway call on the placeholder"
        return _Stats()

    async def get_programme_info(self):
        return []

    def get_metrics(self):
        return {}


@pytest.fixture(autouse=True)
def fakes(monkeypatch):
    _Auth.logins = 0
    _Client.gateways = ["10060006A02F00000001"]
    _Client.bound = []
    monkeypatch.setattr(fauth, "PasswordAuth", _Auth)
    monkeypatch.setattr(fclient, "Client", _Client)
    # The library's facade imports both by name; patch it too, so no test reaches the network.
    monkeypatch.setattr(fwrapper, "PasswordAuth", _Auth)
    monkeypatch.setattr(fwrapper, "Client", _Client)
    monkeypatch.setattr(cs, "_AUTH", {}, raising=False)


# -- #233: one login, many passes ---------------------------------------------------------
def test_twelve_passes_make_one_login():
    for _ in range(12):
        cs._read_sync("a@example.com", "pw", "10060006a02f00000001")
    assert _Auth.logins == 1
    assert set(_Client.bound) == {"10060006A02F00000001"}       # uppercased


def test_new_credentials_log_in_again():
    cs._read_sync("a@example.com", "pw", "SN1")
    cs._read_sync("a@example.com", "pw2", "SN1")
    assert _Auth.logins == 2


@pytest.mark.parametrize("fails,want", [(1, 600), (2, 1200), (3, 1800), (9, 1800)])
def test_failed_passes_back_off_and_never_beat_the_interval(fails, want):
    assert cs.retry_delay(300, fails) == want
    assert cs.retry_delay(300, fails) >= 300


def test_the_45s_retry_is_gone():
    import pathlib
    src = pathlib.Path(cs.__file__).with_name("app.py").read_text()
    assert "min(interval, 45)" not in src
    assert "cloud_status.retry_delay(interval, _fail_streak)" in src


# -- #248: the serial ---------------------------------------------------------------------
def test_no_serial_and_one_agate_uses_it():
    cs._read_sync("a@example.com", "pw", None)
    assert _Client.bound[-1] == "10060006A02F00000001"


def test_no_serial_and_several_agates_never_guesses():
    _Client.gateways = ["SN1", "SN2"]
    with pytest.raises(cs.GatewayChoiceNeeded) as e:
        cs._read_sync("a@example.com", "pw", None)
    assert e.value.serials == ["SN1", "SN2"]
    assert _Client.bound == ["placeholder"]                     # only the account-level list


def test_verify_settles_the_serial():
    _Client.gateways = ["SN1"]
    assert cs.verify_credentials("a@example.com", "pw")["gateway"] == "SN1"
    _Client.gateways = ["SN1", "SN2"]
    v = cs.verify_credentials("a@example.com", "pw")
    assert v["ok"] is False and "SN1" in v["detail"] and "SN2" in v["detail"]
    v = cs.verify_credentials("a@example.com", "pw", "sn2")
    assert v["ok"] is True and v["gateway"] == "SN2"
    v = cs.verify_credentials("a@example.com", "pw", "SN9")
    assert v["ok"] is False and "not on this account" in v["detail"]


def test_verify_reports_a_bad_password():
    v = cs.verify_credentials("a@example.com", "wrong")
    assert v["ok"] is False and v["rejected"] is True


def test_a_rejected_password_says_how_many_attempts_are_left(monkeypatch):
    """FranklinWH counts wrong passwords and then locks the owner's real account
    (2026-10-21: "Incorrect password, you still have 2 chances to enter")."""
    class AccountLockedException(Exception):
        pass

    async def _locked(self, force_refresh=False):
        raise AccountLockedException("Incorrect password, you still have 2 chances to enter.")
    monkeypatch.setattr(_Auth, "get_token", _locked)
    v = cs.verify_credentials("a@example.com", "pw")
    assert v["ok"] is False and v["rejected"] is True and v["attempts_left"] == 2
    assert "2 more attempts" in v["detail"] and "before trying again" in v["detail"]


def test_the_card_blocks_a_retry_of_a_rejected_password_and_can_show_it():
    import pathlib
    root = pathlib.Path(cs.__file__).parent
    js = (root / "static/js/settings_tab.js").read_text()
    html = (root / "templates/tabs/settings.html").read_text()
    assert "get cloudBlocked()" in js and "if (this.cloudBlocked) return;" in js
    assert "cloudBlocked" in html.split("saveCloud()")[1][:400]
    assert "cloudShowPw ? 'text' : 'password'" in html
    assert 'autocomplete="new-password"' in html


def test_verify_hands_its_login_to_the_poller():
    cs.verify_credentials("a@example.com", "pw", "SN1")
    cs._read_sync("a@example.com", "pw", "SN1")
    assert _Auth.logins == 1


# -- #248: the card saves through the sign-in check ---------------------------------------
def test_cloud_card_saves_through_setup_cloud():
    import pathlib
    root = pathlib.Path(cs.__file__).parent
    js = (root / "static/js/settings_tab.js").read_text()
    html = (root / "templates/tabs/settings.html").read_text()
    body = js[js.index("async saveCloud()"):js.index("get cloudOk()")]
    assert "'api/setup/cloud'" in body
    assert "fwh_cloud_email" in body and "fwh_cloud_password" in body and "fwh_cloud_gateway" in body
    assert 'saveCloud()' in html
