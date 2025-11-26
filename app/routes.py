# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
routes.py
-----------
Routes for the Flask application.
# This module is responsible for registering the routes of the REST API
# and linking them to the corresponding resources.
"""

from flask_restful import Api

from app.logger import logger
from app.resources.config import ConfigResource
from app.resources.dummy import DummyListResource, DummyResource
from app.resources.health import HealthResource
from app.resources.version import VersionResource


def register_routes(app):
    """
    Register the REST API routes on the Flask application.

    Args:
        app (Flask): The Flask application instance.

    This function creates a Flask-RESTful Api instance, adds the resource
    endpoints for managing dummy items, and logs the successful registration
    of routes.
    """
    api = Api(app)

    api.add_resource(DummyListResource, "/dummies")
    api.add_resource(DummyResource, "/dummies/<int:dummy_id>")

    api.add_resource(VersionResource, "/version")
    api.add_resource(ConfigResource, "/config")
    api.add_resource(HealthResource, "/health")

    logger.info("Routes registered successfully.")
