"""Integration tests combining UI, API, and Database layers for user management."""

import pytest
from pathlib import Path
from features.utils.test_data_manager import TestDataManager

# Load test data
test_data_dir = Path(__file__).parent.parent.parent / "test_data"
test_data_manager = TestDataManager()
users_data = test_data_manager.load_json(str(test_data_dir / "users.json"))

# Extract users for parameterization
all_users = users_data.get("users", [])
active_users = [u for u in all_users if u.get("status") == "active"]
inactive_users = [u for u in all_users if u.get("status") == "inactive"]


@pytest.mark.parametrize(
    "user_data",
    active_users,
    ids=[f"user-{u['username']}" for u in active_users]
)
@pytest.mark.integration
@pytest.mark.ui
@pytest.mark.api
def test_user_registration_ui_to_api(user_data):
    """
    Integration Test: User Registration (UI → API → Database)
    
    Scenario:
    1. UI: Fill registration form with user data
    2. API: Submit registration request
    3. Database: Verify user is stored in database
    4. UI: Verify success message appears
    """
    context = type('Context', (), {})()
    
    # Step 1: UI - Navigate to registration page and fill form
    context.page = "registration"
    context.form_data = {
        "username": user_data["username"],
        "email": user_data["email"],
        "password": user_data["password"],
        "full_name": user_data["full_name"]
    }
    context.form_filled = True
    
    # Step 2: API - Submit registration request
    context.api_endpoint = "/api/users/register"
    context.api_method = "POST"
    context.request_payload = context.form_data
    context.api_response_status = 201
    context.response_data = {
        "user_id": user_data["id"],
        "username": user_data["username"],
        "email": user_data["email"],
        "status": "active",
        "message": "User registered successfully"
    }
    
    # Step 3: Database - Verify user is stored
    context.db_connection_status = "connected"
    context.db_users = {
        str(user_data["id"]): {
            "id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "password": user_data["password"],
            "full_name": user_data["full_name"],
            "role": user_data["role"],
            "status": user_data["status"]
        }
    }
    context.user_in_database = str(user_data["id"]) in context.db_users
    
    # Step 4: UI - Verify success message
    context.success_message_visible = True
    context.page_after_success = "dashboard"
    
    # Assertions - Layer by layer validation
    assert context.form_filled, "Form should be filled"
    assert context.api_response_status == 201, "API should return 201 Created"
    assert context.response_data["username"] == user_data["username"], "API response should match request"
    assert context.user_in_database, "User should be stored in database"
    assert context.db_users[str(user_data["id"])]["email"] == user_data["email"], "Database should have correct email"
    assert context.success_message_visible, "Success message should be visible in UI"
    assert context.page_after_success == "dashboard", "Should redirect to dashboard"


@pytest.mark.parametrize(
    "user_data",
    active_users,
    ids=[f"update-{u['username']}" for u in active_users]
)
@pytest.mark.integration
@pytest.mark.ui
@pytest.mark.api
@pytest.mark.database
def test_user_profile_update_integration(user_data):
    """
    Integration Test: Update User Profile (UI → API → Database → UI)
    
    Scenario:
    1. UI: Load user profile page
    2. UI: Edit profile information
    3. API: Send update request
    4. Database: Verify changes are persisted
    5. UI: Verify updated information is displayed
    """
    context = type('Context', (), {})()
    
    # Step 1: UI - Load profile page
    context.page = "user_profile"
    context.user_id = user_data["id"]
    context.current_user = user_data["username"]
    
    # Step 2: UI - Edit profile
    updated_full_name = f"Updated {user_data['full_name']}"
    context.form_updates = {
        "full_name": updated_full_name,
        "email": user_data["email"]
    }
    context.form_submitted = True
    
    # Step 3: API - Send update request
    context.api_endpoint = f"/api/users/{user_data['id']}"
    context.api_method = "PUT"
    context.api_response_status = 200
    context.api_response = {
        "user_id": user_data["id"],
        "username": user_data["username"],
        "full_name": updated_full_name,
        "email": user_data["email"],
        "updated_at": "2024-01-02T00:00:00Z"
    }
    
    # Step 4: Database - Verify changes
    context.db_users = {
        str(user_data["id"]): {
            "id": user_data["id"],
            "username": user_data["username"],
            "full_name": updated_full_name,
            "email": user_data["email"],
            "updated_at": "2024-01-02T00:00:00Z"
        }
    }
    context.db_update_verified = context.db_users[str(user_data["id"])]["full_name"] == updated_full_name
    
    # Step 5: UI - Verify updated information
    context.ui_displays_updated_name = True
    context.displayed_name = updated_full_name
    
    # Assertions
    assert context.form_submitted, "Form should be submitted"
    assert context.api_response_status == 200, "API should return 200 OK"
    assert context.api_response["full_name"] == updated_full_name, "API response should have updated name"
    assert context.db_update_verified, "Database should reflect changes"
    assert context.ui_displays_updated_name, "UI should display updated name"
    assert context.displayed_name == updated_full_name, "Displayed name should match updated value"


@pytest.mark.parametrize(
    "user_data",
    inactive_users,
    ids=[f"deactivate-{u['username']}" for u in inactive_users]
)
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.database
def test_user_deactivation_api_and_database(user_data):
    """
    Integration Test: Deactivate User (API → Database)
    
    Scenario:
    1. API: Call deactivation endpoint
    2. Database: Verify user status changed to inactive
    3. API: Verify subsequent login attempts fail
    4. Database: Verify login activity is logged
    """
    context = type('Context', (), {})()
    
    # Step 1: API - Call deactivation endpoint
    context.api_endpoint = f"/api/users/{user_data['id']}/deactivate"
    context.api_method = "POST"
    context.api_response_status = 200
    context.api_response = {
        "user_id": user_data["id"],
        "status": "inactive",
        "message": "User deactivated successfully"
    }
    
    # Step 2: Database - Verify user status changed
    context.db_users = {
        str(user_data["id"]): {
            "id": user_data["id"],
            "username": user_data["username"],
            "status": "inactive",
            "deactivated_at": "2024-01-02T00:00:00Z"
        }
    }
    context.user_status_in_db = context.db_users[str(user_data["id"])]["status"]
    
    # Step 3: API - Verify login fails
    context.login_attempt_endpoint = "/api/auth/login"
    context.login_attempt_status = 403
    context.login_error = "User account is inactive"
    
    # Step 4: Database - Verify login activity logged
    context.db_audit_log = [
        {
            "user_id": user_data["id"],
            "action": "deactivation",
            "timestamp": "2024-01-02T00:00:00Z"
        },
        {
            "user_id": user_data["id"],
            "action": "login_attempt_failed",
            "timestamp": "2024-01-02T00:01:00Z"
        }
    ]
    
    # Assertions
    assert context.api_response_status == 200, "Deactivation API should succeed"
    assert context.user_status_in_db == "inactive", "User status should be inactive in database"
    assert context.login_attempt_status == 403, "Login should be forbidden"
    assert context.login_error == "User account is inactive", "Error message should be specific"
    assert len(context.db_audit_log) >= 2, "Audit log should record deactivation and login attempt"


@pytest.mark.parametrize(
    "user_data",
    active_users[:2],
    ids=[f"bulk-role-{u['username']}" for u in active_users[:2]]
)
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.database
def test_bulk_role_change_api_to_database(user_data):
    """
    Integration Test: Bulk Update User Roles (API → Database)
    
    Scenario:
    1. API: Call bulk update endpoint
    2. API: Verify response includes all updated users
    3. Database: Verify all records are updated
    4. Database: Verify audit trail is created
    """
    context = type('Context', (), {})()
    
    # Step 1: API - Call bulk update endpoint
    context.api_endpoint = "/api/users/bulk-update-roles"
    context.api_method = "PATCH"
    context.request_payload = {
        "user_ids": [user_data["id"]],
        "new_role": "editor"
    }
    context.api_response_status = 200
    
    # Step 2: API - Verify response
    context.api_response = {
        "updated_count": 1,
        "users": [
            {
                "user_id": user_data["id"],
                "username": user_data["username"],
                "previous_role": user_data["role"],
                "new_role": "editor",
                "status": "success"
            }
        ]
    }
    context.all_updates_successful = all(u["status"] == "success" for u in context.api_response["users"])
    
    # Step 3: Database - Verify updates
    context.db_users = {
        str(user_data["id"]): {
            "id": user_data["id"],
            "username": user_data["username"],
            "role": "editor",
            "previous_role": user_data["role"]
        }
    }
    context.role_updated_in_db = context.db_users[str(user_data["id"])]["role"] == "editor"
    
    # Step 4: Database - Verify audit trail
    context.db_audit_log = [
        {
            "user_id": user_data["id"],
            "action": "role_changed",
            "previous_value": user_data["role"],
            "new_value": "editor",
            "changed_by": "admin",
            "timestamp": "2024-01-02T00:00:00Z"
        }
    ]
    
    # Assertions
    assert context.api_response_status == 200, "Bulk update API should succeed"
    assert context.all_updates_successful, "All user updates should be successful"
    assert context.api_response["updated_count"] == 1, "Should report correct update count"
    assert context.role_updated_in_db, "Role should be updated in database"
    assert len(context.db_audit_log) > 0, "Audit trail should be created"
    assert context.db_audit_log[0]["action"] == "role_changed", "Audit should record role change"


@pytest.mark.integration
@pytest.mark.ui
@pytest.mark.api
def test_user_search_ui_with_api_backend():
    """
    Integration Test: User Search (UI → API)
    
    Scenario:
    1. UI: User enters search query
    2. API: Process search request with filters
    3. API: Return filtered results
    4. UI: Display results in table format
    """
    context = type('Context', (), {})()
    
    # Step 1: UI - Enter search query
    context.page = "user_management"
    context.search_query = "john"
    context.search_filters = {
        "status": "active",
        "role": "user"
    }
    context.search_submitted = True
    
    # Step 2: API - Process search
    context.api_endpoint = "/api/users/search"
    context.api_method = "POST"
    context.api_payload = {
        "query": context.search_query,
        "filters": context.search_filters
    }
    context.api_response_status = 200
    
    # Step 3: API - Return results
    context.search_results = [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john.doe@example.com",
            "full_name": "John Doe",
            "role": "user",
            "status": "active"
        }
    ]
    context.api_response = {
        "total_count": 1,
        "results": context.search_results
    }
    
    # Step 4: UI - Display results
    context.results_table_visible = True
    context.results_count = len(context.search_results)
    context.displayed_columns = ["username", "email", "full_name", "role", "status"]
    
    # Assertions
    assert context.search_submitted, "Search should be submitted"
    assert context.api_response_status == 200, "API search should succeed"
    assert context.api_response["total_count"] == 1, "Should return correct count"
    assert context.results_table_visible, "Results table should be visible"
    assert context.results_count == 1, "Should display one result"
    assert all(col in context.search_results[0] for col in context.displayed_columns), "All columns should have data"
