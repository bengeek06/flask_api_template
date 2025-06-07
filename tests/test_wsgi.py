import pytest
import importlib
import sys
import os

@pytest.mark.parametrize("env,expected_config", [
    ("production", "app.config.ProductionConfig"),
    ("staging", "app.config.StagingConfig"),
    ("testing", "app.config.TestingConfig"),
    ("development", "app.config.DevelopmentConfig"),
    ("unknown", "app.config.DevelopmentConfig"),
])
def test_wsgi_config_class(monkeypatch, env, expected_config):
    # Patch load_dotenv pour éviter de charger de vrais fichiers .env
    monkeypatch.setattr("wsgi.load_dotenv", lambda *args, **kwargs: None)

    # Patch app.create_app AVANT d'importer wsgi
    captured = {}
    def fake_create_app(config_class):
        captured["config_class"] = config_class
        class DummyApp:
            pass
        return DummyApp()
    monkeypatch.setattr("app.create_app", fake_create_app)

    if "wsgi" in sys.modules:
        del sys.modules["wsgi"]
    os.environ["FLASK_ENV"] = env

    wsgi = importlib.import_module("wsgi")

    assert hasattr(wsgi, "app")
    assert "config_class" in captured, f"create_app was not called for env={env}"
    assert captured["config_class"] == expected_config