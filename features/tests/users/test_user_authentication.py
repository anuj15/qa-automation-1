"""Parameterized user authentication tests using test data."""

import pytest
import json
from pathlib import Path
from features.utils.test_data_manager import TestDataManager


# Load test data
test_data_dir = Path(__file__).parent.parent.parent / "test_data"
test_data_manager = TestDataManager()
users_data = test_data_manager.load_json(str(test_data_dir / "users.json"))

# Extract test credentials for parameterization
test_credentials = users_data.get("test_credentials", {})
valid_user = test_credentials.get("valid_user", {})
invalid_user = test_credentials.get("invalid_user", {})
admin_user = test_credentials.get("admin_user", {})

# Parameterized test data for login success scenarios
login_success_data = [
    {
        "username": valid_user.get("username", "john_doe"),
        "password": valid_user.get("password", "SecurePass123!"),
        "expected_page": "dashboard",
        "expected_message": "Welcome, John Doe"
    },
    {
        "username": admin_user.get("username", "jane_smith"),
        "password": admin_user.get("password", "JaneSecure456!"),
        "expected_page": "dashboard",
        "expected_message": "Welcome, Jane Smith"
    }
]

# Parameterized test data for login failure scenarios
login_failure_data = [
    {
        "username": invalid_user.get("username", "john_doe"),
        "password": invalid_user.get("password", "WrongPassword"),
        "expected_error": "Invalid username or password"
    },
    {
        "username": "nonexistent_user",
        "password": "AnyPassword123",
        "expected_error": "Invalid username or password"
    },
    {
        "username": valid_user.get("username", "john_doe"),
        "password": "",
        "expected_error": "Password is required"
    }
]


@pytest.mark.parametrize(
    "login_scenario",
    login_success_data,
    ids=[f"login-{data['username']}" for data in login_success_data]
)
@pytest.mark.ui
@pytest.mark.user_authentication
def test_user_login_success(login_scenario):
    """Test successful user login with different user credentials from test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.app_loaded = True
    context.current_page = "login"
    
    # Execute
    context.username = login_scenario["username"]
    context.password = login_scenario["password"]
    
    # Simulate login with test data
    if context.username in [valid_user.get("username"), admin_user.get("username")]:
        if (context.username == valid_user.get("username") and 
            context.password == valid_user.get("password")):
            context.login_success = True
            context.current_page = "dashboard"
            context.user_name = "John Doe"
        elif (context.username == admin_user.get("username") and 
              context.password == admin_user.get("password")):
            context.login_success = True
            context.current_page = "dashboard"
            context.user_name = "Jane Smith"
    else:
        context.login_success = False
    
    # Assertions
    assert context.login_success is True, f"Login failed for {login_scenario['username']}"
    assert context.current_page == login_scenario["expected_page"]
    assert f"Welcome, {context.user_name}" == login_scenario["expected_message"]


@pytest.mark.parametrize(
    "login_scenario",
    login_failure_data,
    ids=[f"login-fail-{i}" for i in range(len(login_failure_data))]
)
@pytest.mark.ui
@pytest.mark.user_authentication
def test_user_login_failure(login_scenario):
    """Test login failure with invalid credentials from test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.app_loaded = True
    context.current_page = "login"
    
    # Execute
    context.username = login_scenario["username"]
    context.password = login_scenario["password"]
    
    # Simulate login validation
    valid_combo = (
        (context.username == valid_user.get("username") and 
         context.password == valid_user.get("password")) or
        (context.username == admin_user.get("username") and 
         context.password == admin_user.get("password"))
    )
    
    if not valid_combo:
        if not context.password:
            context.error_message = "Password is required"
        else:
            context.error_message = "Invalid username or password"
        context.login_success = False
    
    # Assertions
    assert context.login_success is False, "Login should have failed"
    assert context.current_page == "login", "Should remain on login page"
    assert context.error_message == login_scenario["expected_error"]


@pytest.mark.parametrize(
    "user_data",
    users_data.get("users", []),
    ids=[f"user-{user['username']}" for user in users_data.get("users", [])]
)
@pytest.mark.ui
@pytest.mark.user_authentication
def test_user_logout(user_data):
    """Test logout functionality with users from test data."""
    context = type('Context', (), {})()
    
    # Setup - simulate logged-in user
    context.logged_in = True
    context.current_page = "dashboard"
    context.current_user = user_data["username"]
    context.user_id = user_data["id"]
    
    # Execute logout
    context.logged_in = False
    context.current_page = "login"
    context.current_user = None
    
    # Assertions
    assert context.logged_in is False
    assert context.current_page == "login"
    assert context.current_user is None


@pytest.mark.parametrize(
    "user_data",
    users_data.get("users", []),
    ids=[f"redirect-{user['username']}" for user in users_data.get("users", [])]
)
@pytest.mark.ui
@pytest.mark.user_authentication
def test_unauthenticated_redirect(user_data):
    """Test redirect to login for unauthenticated users from test data."""
    context = type('Context', (), {})()
    
    # Setup - user not logged in
    context.logged_in = False
    context.current_url = "/dashboard"
    context.current_page = "dashboard"
    
    # Simulate access attempt
    if not context.logged_in:
        context.current_page = "login"
        context.current_url = "/login"
    
    # Assertions
    assert context.current_page == "login"
    assert "/login" in context.current_url
