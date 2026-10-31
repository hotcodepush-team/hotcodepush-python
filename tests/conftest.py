import pytest


@pytest.fixture(autouse=True)
def recorded_sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    sleeps: list[float] = []
    monkeypatch.setattr("hotcodepush._http.sleep", sleeps.append)
    return sleeps


@pytest.fixture(autouse=True)
def unset_token_environment_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    # A token set in the developer's shell would end up in the requests the tests assert on.
    monkeypatch.delenv("HOTCODEPUSH_TOKEN", raising=False)
