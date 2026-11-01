# Style Guide for {{PROJECT_NAME}} QA Automation

## Python Style (PEP 8)

### Code Formatting

- **Line length:** 150 characters maximum
- **Indentation:** 4 spaces (no tabs)
- **Quotes:** Double quotes (`"`) for strings
- **Imports:** Sorted and grouped (stdlib, third-party, local)

### Naming Conventions

| Construct | Convention | Example |
|-----------|-----------|---------|
| Variables | `snake_case` | `user_name`, `test_data` |
| Functions | `snake_case` | `get_user_by_id()`, `verify_login()` |
| Classes | `PascalCase` | `LoginPage`, `UserService` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_TIMEOUT`, `DEFAULT_BROWSER` |
| Private | `_leading_underscore` | `_internal_method()` |

### Docstrings

All public functions and classes must have docstrings:

```python
def get_user_credentials(user_type: str = "default") -> dict:
    """
    Retrieve user credentials for the specified user type.

    :param user_type: User type identifier (default, admin, etc.)
    :return: Dictionary with username and password
    :raises ValueError: If credentials not found for user type
    """
    pass
```

### Type Hints

Use type hints for function parameters and return values:

```python
def calculate_timeout(multiplier: int) -> int:
    """Calculate timeout value."""
    return multiplier * 1000

def fetch_data(user_id: int | str) -> dict | None:
    """Fetch data for user."""
    pass
```

### Comments

- Write comments only when logic is non-obvious
- Avoid redundant comments that restate the code
- Use single-space comment formatting

```python
# Good: Explains why, not what
# Retry on 429 status (rate limiting)
if response.status_code == 429:
    time.sleep(backoff)

# Avoid: Restates the code
# Set x to 5
x = 5
```

## Test Automation Best Practices

### Page Objects

Page objects encapsulate UI interactions and locators:

```python
from features.pages.ui_base_class import UIBaseClass

class LoginPage(UIBaseClass):
    """Page object for the login page."""

    # Locators as class-level constants
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_MESSAGE = "#error-message"

    async def enter_username(self, username: str) -> None:
        """Enter username in the login form."""
        await self.fill(self.USERNAME_INPUT, username)

    async def enter_password(self, password: str) -> None:
        """Enter password in the login form."""
        await self.fill(self.PASSWORD_INPUT, password)

    async def click_login(self) -> None:
        """Click the login button."""
        await self.click(self.LOGIN_BUTTON)

    async def is_error_displayed(self) -> bool:
        """Check if error message is displayed."""
        return await self.is_visible(self.ERROR_MESSAGE)
```

**Guidelines:**
- Use role-based selectors when possible (`role=button`)
- Use text-based selectors for stable elements (`text=Login`)
- Use test-id attributes for unstable elements (`test-id=my-button`)
- Avoid raw CSS/XPath unless absolutely necessary
- Keep one action per method

### API Services

API service classes encapsulate API interactions:

```python
from features.services.api_base_class import APIBaseClass

class UserService(APIBaseClass):
    """Service for user-related API endpoints."""

    def get_user(self, user_id: int) -> dict:
        """Retrieve user by ID."""
        response = self.get(f"/api/users/{user_id}")
        response.raise_for_status()
        return response.json()

    def create_user(self, user_data: dict) -> dict:
        """Create a new user."""
        response = self.post("/api/users", json=user_data)
        response.raise_for_status()
        return response.json()

    def update_user(self, user_id: int, user_data: dict) -> dict:
        """Update an existing user."""
        response = self.put(f"/api/users/{user_id}", json=user_data)
        response.raise_for_status()
        return response.json()
```

**Guidelines:**
- Extend `APIBaseClass`
- Use meaningful method names
- Validate response status codes
- Log all requests for debugging
- Return parsed JSON responses

### BDD Test Structure

```python
from pytest_bdd import given, when, then, scenario

@scenario("features.feature", "Scenario name")
def test_scenario():
    """Test scenario."""
    pass

@given("Initial state")
def initial_state(page):
    """Set up initial state."""
    pass

@when("Action is performed")
def action_performed(page):
    """Perform an action."""
    pass

@then("Result is verified")
def result_verified(page):
    """Verify the result."""
    pass
```

**Guidelines:**
- Use Gherkin syntax in feature files
- Keep step definitions thin (call page/service methods)
- Use meaningful step descriptions
- Avoid hardcoded values in steps

### Assertions

Use explicit assertions:

```python
# Good: Clear assertion message
assert response.status_code == 200, f"Expected 200, got {response.status_code}"

# Good: Multiple specific assertions
assert "success" in response.json()["message"]
assert response.json()["user_id"] is not None

# Avoid: Generic assertions
assert response  # Too vague
assert bool(data)  # Unclear intent
```

### Test Data Management

Store test data separately from test code:

```yaml
# features/test_data/users.yaml
valid_user:
  username: "test_user"
  password: "test_password"
  email: "test@example.com"

invalid_user:
  username: "invalid"
  password: "wrong"
```

```python
# features/tests/test_example.py
import yaml

with open("features/test_data/users.yaml") as f:
    test_data = yaml.safe_load(f)

def test_login_valid():
    """Test login with valid user."""
    user = test_data["valid_user"]
    # ...
```

### Markers and Tags

Tag tests with appropriate markers:

```python
@pytest.mark.bvt
@pytest.mark.ui
@pytest.mark.authentication
def test_user_login():
    """Test user login."""
    pass
```

See `pytest.ini` for available markers.

## File Organization

### Directory Structure

```
features/
├── pages/
│   ├── __init__.py
│   ├── ui_base_class.py
│   └── login/
│       ├── __init__.py
│       ├── ui_login_locators.py
│       └── ui_login_page.py
├── services/
│   ├── __init__.py
│   ├── api_base_class.py
│   └── user/
│       ├── __init__.py
│       └── api_user_service.py
├── tests/
│   ├── conftest.py
│   ├── shared_steps.py
│   └── authentication/
│       ├── login.feature
│       └── test_login.py
├── test_data/
│   ├── users.yaml
│   └── login_scenarios.json
└── utils/
    ├── config_manager.py
    ├── log_manager.py
    └── auth_setup.py
```

### Naming Conventions

- **Page objects:** `ui_<feature>_page.py`
- **Locators:** `ui_<feature>_locators.py`
- **API services:** `api_<resource>_service.py`
- **Test files:** `test_<feature>.py`
- **Feature files:** `<feature>.feature`

## Error Handling

Catch specific exceptions:

```python
# Good: Specific exception handling
try:
    response = self.get("/api/users/123")
except requests.Timeout:
    self.logger.error("Request timed out")
except requests.RequestException as e:
    self.logger.error(f"Request failed: {e}")

# Avoid: Bare except
try:
    result = do_something()
except:
    pass  # Never do this
```

## Logging

Use the provided logger:

```python
from features.utils.log_manager import get_logger

logger = get_logger()

logger.info("Starting test")
logger.warning("Unexpected behavior")
logger.error("Test failed")
```

## Code Review Checklist

- [ ] Follows PEP 8 style guidelines
- [ ] All functions have docstrings
- [ ] Type hints are present
- [ ] No hardcoded values or credentials
- [ ] Error handling is present
- [ ] Tests have meaningful names and markers
- [ ] Page objects use locator constants
- [ ] API calls validate status codes
- [ ] Test data is externalized
- [ ] Comments explain "why", not "what"

## Tools

- **Formatter:** `ruff format`
- **Linter:** `ruff check --fix`
- **Type checker:** `mypy`

```powershell
# Format code
ruff format features/

# Lint and fix
ruff check --fix features/

# Type checking
mypy features/
```
