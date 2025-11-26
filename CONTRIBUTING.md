# Contributing to Guardian Service

Thank you for your interest in contributing to the **Guardian Service**!

> **Note**: This service is part of the larger [Waterfall](../../README.md) project. For the overall development workflow, branch strategy, and contribution guidelines, please refer to the [main CONTRIBUTING.md](../../CONTRIBUTING.md) in the root repository.

## Table of Contents

- [Service Overview](#service-overview)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [API Development](#api-development)
- [RBAC Concepts](#rbac-concepts)
- [Common Tasks](#common-tasks)

## Service Overview

The **Guardian Service** provides Role-Based Access Control (RBAC) for the Waterfall platform:

- **Technology Stack**: Python 3.13+, Flask 3.1+, SQLAlchemy, PostgreSQL
- **Port**: 5003 (containerized) / 5000 (standalone)
- **Responsibilities**:
  - Role management
  - Policy management
  - Permission management
  - User-role assignments
  - Access control checks
  - Resource protection

**RBAC Model:**
- **Roles** → **Policies** → **Permissions**
- Users are assigned Roles
- Roles contain multiple Policies
- Policies contain multiple Permissions
- Permissions define actions on resources

**Key Dependencies:**
- Flask 3.1+ for REST API
- SQLAlchemy for ORM
- Marshmallow for serialization
- PostgreSQL for data persistence

## Development Setup

### Prerequisites

- Python 3.13+
- PostgreSQL 16+ (or use Docker)
- pip and virtualenv

### Local Setup

```bash
# Navigate to service directory
cd services/guardian_service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment configuration
cp env.example .env.development
```

### Environment Configuration

```bash
# Flask environment
FLASK_ENV=development
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://guardian_user:guardian_pass@localhost:5432/guardian_dev

# Security
JWT_SECRET=dev-jwt-secret
INTERNAL_AUTH_TOKEN=dev-internal-secret
```

### Database Setup

```bash
# Create database
createdb guardian_dev

# Run migrations
flask db upgrade

# Or use Docker
docker run -d \
  --name guardian_db_dev \
  -e POSTGRES_USER=guardian_user \
  -e POSTGRES_PASSWORD=guardian_pass \
  -e POSTGRES_DB=guardian_dev \
  -p 5432:5432 \
  postgres:16-alpine
```

### Running the Service

```bash
# Development mode
python run.py

# Production-style
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## Coding Standards

### Python Style Guide

Follow **PEP 8** with Black formatting:

```bash
# Format code
black app/ tests/

# Check quality
pylint app/ tests/

# Sort imports
isort app/ tests/
```

### RBAC-Specific Conventions

**Permission Naming:**
```python
# Format: resource:action
PERMISSIONS = [
    'users:create',
    'users:read',
    'users:update',
    'users:delete',
    'projects:create',
    'projects:read',
    'projects:update',
    'projects:delete',
    'roles:manage',
    'policies:manage'
]
```

**Policy Naming:**
```python
# Descriptive, action-oriented names
POLICIES = [
    'user_management',      # Manage users
    'project_full_access',  # Full project CRUD
    'project_read_only',    # Read-only project access
    'admin_access'          # Administrative functions
]
```

**Role Naming:**
```python
# Clear hierarchy and purpose
ROLES = [
    'super_admin',          # System administrator
    'company_admin',        # Company administrator
    'project_manager',      # Project management
    'team_member',          # Regular team member
    'viewer'                # Read-only access
]
```

### Type Hints and Documentation

```python
from typing import List, Dict, Optional, Any
from app.models import Role, Policy, Permission

def check_user_permission(
    user_id: int,
    resource: str,
    action: str,
    company_id: Optional[int] = None
) -> bool:
    """Check if user has permission for resource action.
    
    Args:
        user_id: User's database ID
        resource: Resource type (e.g., 'users', 'projects')
        action: Action to perform (e.g., 'create', 'read')
        company_id: Optional company context for multi-tenancy
    
    Returns:
        True if user has permission, False otherwise
    
    Example:
        >>> check_user_permission(1, 'projects', 'create', company_id=5)
        True
    """
    permission_name = f"{resource}:{action}"
    # Implementation
    return has_permission(user_id, permission_name, company_id)
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test category
pytest tests/test_roles.py -v
pytest tests/test_access_control.py -v
```

### Test Structure

```python
import pytest
from app.models import Role, Policy, Permission, UserRole

class TestAccessControl:
    """Test suite for access control checks."""
    
    @pytest.fixture(autouse=True)
    def setup(self, client):
        """Setup test RBAC data."""
        # Create permission
        perm = Permission(
            name='projects:create',
            description='Create projects'
        )
        db.session.add(perm)
        
        # Create policy
        policy = Policy(name='project_management')
        db.session.add(policy)
        db.session.commit()
        
        # Link permission to policy
        policy.permissions.append(perm)
        
        # Create role
        role = Role(name='project_manager')
        db.session.add(role)
        db.session.commit()
        
        # Link policy to role
        role.policies.append(policy)
        db.session.commit()
        
        self.role_id = role.id
        self.perm_id = perm.id
        
        yield
        
        # Cleanup
        db.session.query(Permission).delete()
        db.session.query(Policy).delete()
        db.session.query(Role).delete()
        db.session.commit()
    
    def test_user_has_permission_through_role(self, client):
        """Test permission check through role assignment."""
        # Assign role to user
        user_role = UserRole(user_id=1, role_id=self.role_id)
        db.session.add(user_role)
        db.session.commit()
        
        # Check access
        response = client.post('/check-access', json={
            'user_id': 1,
            'resource': 'projects',
            'action': 'create'
        })
        
        assert response.status_code == 200
        assert response.json['has_access'] is True
```

### Critical Test Cases

1. **Permission Inheritance**: User → Role → Policy → Permission
2. **Multi-role Permissions**: User with multiple roles
3. **Negative Cases**: Users without permissions
4. **Company Scoping**: Multi-tenant permission checks
5. **Circular Dependencies**: Prevent policy/role loops

## API Development

### Access Control Endpoint

```python
# app/resources/access_control.py
from flask import Blueprint, request, jsonify
from app.models import UserRole, Permission

access_bp = Blueprint('access', __name__)

@access_bp.route('/check-access', methods=['POST'])
def check_access():
    """Check if user has permission for resource action.
    
    Request Body:
        {
            "user_id": 1,
            "resource": "projects",
            "action": "create",
            "company_id": 5  // optional
        }
    
    Response:
        {
            "has_access": true,
            "reason": "User has 'projects:create' permission via 'project_manager' role"
        }
    """
    data = request.get_json()
    user_id = data['user_id']
    resource = data['resource']
    action = data['action']
    company_id = data.get('company_id')
    
    # Check permission
    has_access, reason = check_user_permission(
        user_id, resource, action, company_id
    )
    
    return jsonify({
        'has_access': has_access,
        'reason': reason
    }), 200
```

### Role Management

```python
@roles_bp.route('/roles', methods=['POST'])
def create_role():
    """Create a new role.
    
    Request Body:
        {
            "name": "project_manager",
            "description": "Manages projects",
            "company_id": 5
        }
    """
    data = role_schema.load(request.json)
    role = Role(**data)
    db.session.add(role)
    db.session.commit()
    
    return jsonify(role_schema.dump(role)), 201

@roles_bp.route('/roles/<int:role_id>/policies', methods=['POST'])
def assign_policy_to_role(role_id):
    """Assign policy to role.
    
    Request Body:
        {
            "policy_id": 10
        }
    """
    role = Role.query.get_or_404(role_id)
    policy_id = request.json['policy_id']
    policy = Policy.query.get_or_404(policy_id)
    
    if policy not in role.policies:
        role.policies.append(policy)
        db.session.commit()
    
    return jsonify({'message': 'Policy assigned to role'}), 200
```

## RBAC Concepts

### Permission Structure

Permissions follow the pattern: `resource:action`

```python
# Examples of well-formed permissions
'users:create'              # Create users
'users:read'                # Read user data
'users:update'              # Update user data
'users:delete'              # Delete users
'projects:create'           # Create projects
'projects:manage_members'   # Manage project members
'roles:assign'              # Assign roles
'*:*'                       # Wildcard (super admin)
```

### Permission Hierarchy

```
Role: Super Admin
  └─ Policy: Full System Access
      ├─ Permission: *:*
      └─ (grants all permissions)

Role: Company Admin
  ├─ Policy: User Management
  │   ├─ Permission: users:create
  │   ├─ Permission: users:read
  │   ├─ Permission: users:update
  │   └─ Permission: users:delete
  └─ Policy: Company Management
      ├─ Permission: companies:update
      └─ Permission: organization_units:*

Role: Project Manager
  ├─ Policy: Project Full Access
  │   ├─ Permission: projects:create
  │   ├─ Permission: projects:read
  │   ├─ Permission: projects:update
  │   ├─ Permission: projects:delete
  │   └─ Permission: projects:manage_members
  └─ Policy: Team Member Read
      └─ Permission: users:read

Role: Team Member
  └─ Policy: Project Read Access
      ├─ Permission: projects:read
      └─ Permission: tasks:read
```

### Multi-tenancy

All RBAC objects should be scoped by company:

```python
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    company_id = db.Column(db.Integer, nullable=False)
    
    # Unique constraint per company
    __table_args__ = (
        db.UniqueConstraint('name', 'company_id', name='uq_role_name_company'),
    )
```

## Common Tasks

### Creating a Complete RBAC Setup

```python
def setup_rbac_for_company(company_id: int):
    """Initialize RBAC structure for a new company."""
    
    # 1. Create permissions
    permissions = [
        Permission(name='users:create', description='Create users'),
        Permission(name='users:read', description='Read users'),
        Permission(name='projects:create', description='Create projects'),
        Permission(name='projects:read', description='Read projects'),
    ]
    db.session.add_all(permissions)
    db.session.commit()
    
    # 2. Create policies
    user_mgmt_policy = Policy(
        name='user_management',
        description='Manage users',
        company_id=company_id
    )
    db.session.add(user_mgmt_policy)
    db.session.commit()
    
    # 3. Link permissions to policy
    user_mgmt_policy.permissions.extend([
        permissions[0],  # users:create
        permissions[1],  # users:read
    ])
    db.session.commit()
    
    # 4. Create role
    admin_role = Role(
        name='company_admin',
        description='Company administrator',
        company_id=company_id
    )
    db.session.add(admin_role)
    db.session.commit()
    
    # 5. Link policy to role
    admin_role.policies.append(user_mgmt_policy)
    db.session.commit()
    
    return admin_role
```

### Checking Permissions

```python
def has_permission(user_id: int, permission_name: str, company_id: int) -> bool:
    """Check if user has specific permission."""
    
    # Get user's roles
    user_roles = UserRole.query.filter_by(
        user_id=user_id,
        company_id=company_id
    ).all()
    
    if not user_roles:
        return False
    
    # Check wildcard permission
    if Permission.query.join(Policy.permissions).join(Role.policies).join(
        UserRole, UserRole.role_id == Role.id
    ).filter(
        UserRole.user_id == user_id,
        Permission.name == '*:*'
    ).first():
        return True
    
    # Check specific permission
    has_perm = Permission.query.join(Policy.permissions).join(Role.policies).join(
        UserRole, UserRole.role_id == Role.id
    ).filter(
        UserRole.user_id == user_id,
        Permission.name == permission_name,
        Role.company_id == company_id
    ).first()
    
    return has_perm is not None
```

## Service-Specific Guidelines

### Performance Considerations

1. **Cache permission checks** for frequently accessed resources
2. **Use database indexes** on foreign keys and lookup fields
3. **Batch role assignments** when possible
4. **Avoid N+1 queries** with proper eager loading

### Security Best Practices

1. **Always validate company_id** in multi-tenant scenarios
2. **Log all permission denials** for audit trails
3. **Implement rate limiting** on access checks
4. **Use transactions** for role/policy assignments
5. **Validate permission names** against a registry

## Getting Help

- **Main Project**: See [root CONTRIBUTING.md](../../CONTRIBUTING.md)
- **Issues**: Use GitHub issues with `service:guardian` label
- **Code of Conduct**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Documentation**: [README.md](README.md)
- **OpenAPI Spec**: [openapi.yml](openapi.yml)

---

**Remember**: Always refer to the [main CONTRIBUTING.md](../../CONTRIBUTING.md) for branch strategy, commit conventions, and pull request process!
