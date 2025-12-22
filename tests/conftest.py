import pytest


@pytest.fixture(autouse=True)
def default_test_environment(monkeypatch):
    """
    A fixture that runs for every test to set default environment variables.
    Ensures tests run in SAFE mode with the dummy LLM unless overridden.
    """
    monkeypatch.setenv("CRIRA_SAFE_MODE", "true")
    monkeypatch.setenv("CRIRA_USE_REAL_LLM", "false")
