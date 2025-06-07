"""
routes.py
-----------
Routes for the Flask application.
# This module is responsible for registering the routes of the REST API
# and linking them to the corresponding resources.
"""
from flask_restful import Api
from .logger import logger
from .resources import DummyResource, DummyListResource


def register_routes(app):
    """
    Register the REST API routes on the Flask application.

    Args:
        app (Flask): The Flask application instance.

    This function creates a Flask-RESTful Api instance, adds the resource
    endpoints for managing dummy items, and logs the successful registration
    of routes.
    """
    api = Api(app)  # Create an instance of Flask-RESTful Api

    api.add_resource(DummyListResource, '/dummies')
    api.add_resource(DummyResource, '/dummies/<int:dummy_id>')

    logger.info("Routes registered successfully.")
