# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
# conftest.py
# -----------
# Configuration and fixtures for integration tests.
"""

import os

from dotenv import load_dotenv
from pytest import fixture

from app import create_app
from app.models.db import db

# Load integration test environment
os.environ["FLASK_ENV"] = "testing"
load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(__file__), "..", "..", ".env.test"
    )
)


@fixture
def app():  # pylint: disable=redefined-outer-name
    """
    Fixture to create and configure a Flask application for integration testing.
    """
    app = create_app("app.config.TestingConfig")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@fixture
def client(app):
    """
    Fixture to create a test client for the Flask application.
    """
    return app.test_client()


@fixture
def session(app):
    """
    Fixture to provide a database session for integration tests.
    """
    with app.app_context():
        yield db.session
