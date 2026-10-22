import pytest


@pytest.fixture(autouse=True)
def recorded_sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """The waits between retry attempts, recorded instead of slept."""
    sleeps: list[float] = []
    monkeypatch.setattr("hotcodepush._http.sleep", sleeps.append)
    return sleeps


@pytest.fixture(autouse=True)
def unset_token_environment_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keeps a token of the developer's shell out of the requests a test asserts on."""
    monkeypatch.delenv("HOTCODEPUSH_TOKEN", raising=False)
