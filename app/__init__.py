"""
__init__.py
-----------

Main entry point for initializing the Flask application.

This module is responsible for:
    - Configuring Flask extensions (SQLAlchemy, Migrate, Marshmallow)
    - Registering custom error handlers
    - Registering REST API routes
    - Creating the Flask application via the `create_app` factory

Functions:
    - register_extensions(app): Initialize and register Flask extensions.
    - register_error_handlers(app): Register custom error handlers for the app.
    - create_app(config_class): Application factory that creates and configures
      the Flask app.
"""

import os
from flask import Flask
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

from .models import db
from .logger import logger
from .routes import register_routes

# Initialisation des extensions Flask
migrate = Migrate()
ma = Marshmallow()


def register_extensions(app):
    """
    Initialize and register Flask extensions on the application.

    Args:
        app (Flask): The Flask application instance.
    """
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    logger.info("Extensions registered successfully.")


def register_error_handlers(app):
    """
    Register custom error handlers for the Flask application.

    Args:
        app (Flask): The Flask application instance.
    """
    @app.errorhandler(404)
    def not_found(_):
        """Handler for 404 (resource not found) errors."""
        return {"message": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(_):
        """Handler for 500 (internal server) errors."""
        return {"message": "Internal server error"}, 500

    @app.errorhandler(400)
    def bad_request(_):
        """Handler for 400 (bad request) errors."""
        return {"message": "Bad request"}, 400

    logger.info("Error handlers registered successfully.")


def create_app(config_class):
    """
    Factory to create and configure the Flask application.

    Args:
        config_class: The configuration class or import path to use for Flask.

    Returns:
        Flask: The configured and ready-to-use Flask application instance.
    """
    env = os.getenv('FLASK_ENV')
    logger.info("Creating app in %s environment.", env)
    app = Flask(__name__)
    app.config.from_object(config_class)

    register_extensions(app)
    register_error_handlers(app)
    register_routes(app)
    logger.info("App created successfully.")

    return app
