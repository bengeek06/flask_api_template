"""
import.py
---------

This module defines resources for importing data into the application
from CSV and JSON files via REST endpoints.
"""
import csv
import json
from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from app.models import Dummy, db
from app.schemas import DummySchema


class ImportJSONResource(Resource):
    """
    Resource for importing data from a JSON file.

    Methods:
        post():
            Import data from a JSON file and return a success message.
    """

    def post(self):
        """
        Import data from a JSON file uploaded via multipart/form-data.

        Expects:
            A file field named 'file' containing a JSON file with a list of dummy items.

        Returns:
            dict: A success message indicating the number of records imported, or an error message.
        """
        if 'file' not in request.files:
            return {"message": "No file part in the request."}, 400

        file = request.files['file']
        if file.filename == '':
            return {"message": "No selected file."}, 400

        try:
            data = json.load(file)
            if not isinstance(data, list):
                return {"message": "JSON must be a list of objects."}, 400

            schema = DummySchema()
            count = 0
            errors = []
            for idx, item in enumerate(data):
                # Validate each item
                try:
                    validated = schema.load(item)
                    Dummy.create(name=validated['name'], description=validated.get('description'))
                    count += 1
                except ValidationError as e:
                    errors.append({"index": idx, "error": str(e)})

            if errors:
                return {
                    "message": f"{count} records imported, {len(errors)} errors.",
                    "errors": errors
                }, 400 if count == 0 else 207  # 207: Multi-Status

            return {"message": f"{count} records imported successfully."}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": f"Import failed: {str(e)}"}, 400

class ImportCSVResource(Resource):
    """
    Resource for importing data from a CSV file.
    
    Methods:
        post():
            Import data from a CSV file and return a success message.
    """

    def post(self):
        """
        Import data from a CSV file uploaded via multipart/form-data.

        Expects:
            A file field named 'file' containing a CSV file with columns: name, description.

        Returns:
            dict: A success message indicating the number of records imported, or an error message.
        """
        if 'file' not in request.files:
            return {"message": "No file part in the request."}, 400

        file = request.files['file']
        if file.filename == '':
            return {"message": "No selected file."}, 400

        try:
            # Read CSV file
            stream = file.stream.read().decode('utf-8').splitlines()
            reader = csv.DictReader(stream)
            schema = DummySchema()
            count = 0
            errors = []
            for idx, row in enumerate(reader):
                try:
                    validated = schema.load(row)
                    Dummy.create(name=validated['name'], description=validated.get('description'))
                    count += 1
                except ValidationError as e:
                    errors.append({"index": idx, "error": str(e)})

            if errors:
                return {
                    "message": f"{count} records imported, {len(errors)} errors.",
                    "errors": errors
                }, 400 if count == 0 else 207  # 207: Multi-Status

            return {"message": f"{count} records imported successfully."}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": f"Import failed: {str(e)}"}, 400
