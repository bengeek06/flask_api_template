# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
Integration tests for check_access with Guardian service.

These tests verify the interaction between the Flask API and the Guardian service
for access control. They require Docker services to be running.
"""

import os
import uuid

import pytest
import requests

from tests.unit.conftest import create_jwt_token


@pytest.mark.integration
class TestCheckAccessIntegration:
    """Integration tests for check_access with real Guardian service."""

    @pytest.fixture(autouse=True)
    def check_guardian_available(self):
        """Check if Guardian service is available and skip tests if not."""
        use_guardian = os.environ.get(
            "USE_GUARDIAN_SERVICE", "false"
        ).lower() in ("true", "yes", "1")

        if not use_guardian:
            pytest.skip(
                "Guardian service is disabled (USE_GUARDIAN_SERVICE=false)"
            )

        guardian_url = os.environ.get(
            "GUARDIAN_SERVICE_URL", "http://localhost:5002"
        )

        # Wait for Guardian to be ready
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{guardian_url}/health", timeout=2)
                if response.status_code == 200:
                    return
            except requests.RequestException:
                if i == max_retries - 1:
                    pytest.skip("Guardian service not available")
                import time

                time.sleep(1)

    def test_check_access_with_guardian_service(self, client):
        """Test check_access_required decorator with real Guardian service."""
        company_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        token = create_jwt_token(company_id, user_id)
        client.set_cookie("access_token", token, domain="localhost")

        # Make request to /version endpoint which uses check_access_required
        response = client.get("/version")

        # The response depends on Guardian configuration
        # If Guardian denies access, we get 403
        # If Guardian allows access, we get 200
        assert response.status_code in [200, 403]

        if response.status_code == 403:
            data = response.get_json()
            assert "error" in data
            assert data["error"] == "Access denied"

    def test_check_access_without_jwt_token(self, client):
        """Test check_access_required decorator without JWT token."""
        # Make request without JWT token
        response = client.get("/version")

        # Should get 400 because user_id is missing
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
