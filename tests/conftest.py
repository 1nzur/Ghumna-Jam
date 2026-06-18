import pytest

from app import create_app
from app.config import Config


@pytest.fixture()
def app(tmp_path, monkeypatch):
    db_path = tmp_path / "test.sqlite"
    monkeypatch.setattr(Config, "DB_TYPE", "sqlite")
    monkeypatch.setattr(Config, "SQLITE_DB_PATH", str(db_path))
    monkeypatch.setattr(Config, "TESTING", True, raising=False)
    app = create_app(Config)
    app.config.update(TESTING=True)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
