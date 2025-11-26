# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
Simple integration tests that don't require external services.

These tests verify basic integration patterns without Docker dependencies.
"""

import uuid

import pytest

from tests.unit.conftest import create_jwt_token


@pytest.mark.integration
class TestBasicIntegration:
    """Basic integration tests without external service dependencies."""

    def test_version_endpoint_with_guardian_disabled(self, app, client):
        """Test version endpoint when Guardian is disabled."""
        # Configure app to disable Guardian
        app.config["USE_GUARDIAN_SERVICE"] = False

        company_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        token = create_jwt_token(company_id, user_id)
        client.set_cookie("access_token", token, domain="localhost")

        response = client.get("/version")

        # Should succeed when Guardian is disabled
        assert response.status_code == 200
        data = response.get_json()
        assert "version" in data

    def test_health_endpoint(self, client):
        """Test health endpoint is accessible."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_api_endpoints_without_auth(self, client):
        """Test that protected endpoints require authentication."""
        # Try to access /dummies without JWT
        response = client.get("/dummies")

        # Should get 400 (missing user_id) or 401 depending on decorator implementation
        assert response.status_code in [400, 401]
