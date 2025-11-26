# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""Utility functions for the Flask API Template."""

from app.utils.check_access import check_access, check_access_required
from app.utils.helpers import camel_to_snake
from app.utils.jwt_auth import extract_jwt_data, require_jwt_auth

__all__ = [
    "camel_to_snake",
    "extract_jwt_data",
    "require_jwt_auth",
    "check_access",
    "check_access_required",
]
