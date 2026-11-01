# Test Data Management

This guide explains how to load and manage test data from multiple file formats.

## Supported Formats

- **JSON** — Flexible, nested data structures
- **YAML** — Human-readable, configuration-friendly
- **CSV** — Simple tabular data
- **Excel (.xlsx/.xls)** — Spreadsheets with multiple sheets

## Setup

Test data files should be stored in `features/test_data/`.

```
features/test_data/
├── users.json
├── users.xlsx
├── users.csv
├── users.yml
├── scenarios.json
└── test_cases.xlsx
```

## Basic Usage

### Load JSON

```python
from features.utils.test_data_manager import TestDataManager

# Load entire JSON file
data = TestDataManager().load_json("users.json")
# Returns: {"users": [{"name": "John", "email": "john@example.com"}, ...]}
```

**Example JSON file:**
```json
{
  "users": [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "status": "active"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "status": "inactive"}
  ]
}
```

### Load YAML

```python
from features.utils.test_data_manager import TestDataManager

# Load YAML file
data = TestDataManager().load_yaml("users.yml")
# Returns: {"users": [...]}
```

**Example YAML file:**
```yaml
users:
  - id: 1
    name: John Doe
    email: john@example.com
    status: active
  - id: 2
    name: Jane Smith
    email: jane@example.com
    status: inactive
```

### Load CSV

```python
from features.utils.test_data_manager import TestDataManager

# Load CSV file (returns list of dicts)
data = TestDataManager().load_csv("users.csv")
# Returns: [{"id": "1", "name": "John Doe", "email": "john@example.com"}, ...]
```

**Example CSV file:**
```csv
id,name,email,status
1,John Doe,john@example.com,active
2,Jane Smith,jane@example.com,inactive
3,Bob Johnson,bob@example.com,active
```

### Load Excel

```python
from features.utils.test_data_manager import TestDataManager

# Load Excel file (specify sheet name, default: first sheet)
data = TestDataManager().load_excel("users.xlsx", sheet_name="Users")
# Returns: [{"id": 1, "name": "John Doe", "email": "john@example.com"}, ...]
```

**Features:**
- Auto-detects sheet if `sheet_name` not provided
- Normalizes NaN values to empty strings
- Converts whole-number floats to integers
- Skips empty rows

## Auto-Detect Format

```python
from features.utils.test_data_manager import TestDataManager

# Automatically detect format by file extension
data = TestDataManager().load("users.json")      # JSON
data = TestDataManager().load("users.yml")       # YAML
data = TestDataManager().load("users.csv")       # CSV
data = TestDataManager().load("users.xlsx")      # Excel (first sheet)
data = TestDataManager().load("users.xlsx", sheet_name="Users")  # Specific sheet
```

## Get Test Cases

Convert test data to list of dictionaries (always returns list):

```python
from features.utils.test_data_manager import TestDataManager

# Load test cases from any format
cases = TestDataManager().get_test_cases("users.json")
# Returns: [{"id": 1, "name": "John", ...}, {"id": 2, "name": "Jane", ...}]

for case in cases:
    print(f"Testing user: {case['name']}")
```

## Filter Test Cases

Filter test cases by column values:

```python
from features.utils.test_data_manager import TestDataManager

# Get only active users
active_users = TestDataManager().filter_test_cases("users.csv", status="active")

# Get users by role
admins = TestDataManager().filter_test_cases("users.xlsx", role="admin")

# Multiple filters
results = TestDataManager().filter_test_cases(
    "users.csv",
    status="active",
    role="admin"
)
```

## Slice Test Cases

Load a subset of test cases by index range:

```python
from features.utils.test_data_manager import TestDataManager

# Get first 10 rows
cases = TestDataManager().slice_test_cases("users.csv", start_index=0, end_index=10)

# Get rows 100-200
cases = TestDataManager().slice_test_cases("users.csv", start_index=100, end_index=200)

# Get from index 50 to end
cases = TestDataManager().slice_test_cases("users.csv", start_index=50)
```

## Usage in Tests

### Parameterized Tests with pytest

```python
import pytest
from features.utils.test_data_manager import TestDataManager

@pytest.mark.parametrize("user", TestDataManager().get_test_cases("users.csv"))
def test_user_creation(user):
    """Test user creation with multiple test cases"""
    assert user['name']
    assert user['email']
    assert '@' in user['email']
```

### BDD with pytest-bdd

```python
from pytest_bdd import scenario, given, when, then
from features.utils.test_data_manager import TestDataManager

@given('test user data is loaded')
def step_load_user_data(context):
    context.test_users = TestDataManager().get_test_cases("users.csv")

@when('I create a user from test data')
def step_create_user_from_data(context):
    user = context.test_users[0]
    context.api_service = UserAPI()
    context.response = context.api_service.create_user(
        name=user['name'],
        email=user['email']
    )

@then('the user should be created successfully')
def step_verify_user_created(context):
    assert context.response.status_code == 201
    assert context.response.json()['email'] == context.test_users[0]['email']
```

### With Fixtures

```python
import pytest
from features.utils.test_data_manager import TestDataManager

@pytest.fixture
def user_test_data():
    """Load user test data once for all tests"""
    return TestDataManager().get_test_cases("users.csv")

def test_user_validation(user_test_data):
    """Validate each test user"""
    for user in user_test_data:
        assert len(user['name']) > 0
        assert '@' in user['email']
```

## Configuration Integration

Load test data start/end indices from config:

```python
from features.utils.config_manager import ConfigManager
from features.utils.test_data_manager import TestDataManager

config = ConfigManager()
start = config.get('test_data_start_index', 0)
end = config.get('test_data_end_index', None)

test_cases = TestDataManager().slice_test_cases("users.csv", start_index=start, end_index=end)
```

**In config.yml:**
```yaml
test_data_start_index: 0
test_data_end_index: 100
```

## Best Practices

### ✅ DO

- Store test data in appropriate format (CSV for simple, Excel for complex)
- Use descriptive filenames (`users_active.csv`, not `test1.csv`)
- Organize by feature area (`features/test_data/users/`, `features/test_data/orders/`)
- Use YAML for configuration-like data (environment settings)
- Use Excel for non-technical stakeholders (easier to edit)
- Use CSV for simple tabular data
- Use JSON for complex nested structures and APIs
- Filter/slice large datasets to improve test performance
- Add headers/metadata row in Excel/CSV files
- Normalize test data (consistent date formats, casing, etc.)

### ❌ DON'T

- Hardcode test data in step definitions
- Mix multiple entity types in one file
- Use Excel formulas that break on export
- Create massive test data files (slice instead)
- Store sensitive data (use ConfigManager instead)
- Commit large binary files (use .gitignore)

## File Format Comparison

| Format | Best For | Complexity | Size | Speed | Edit |
|--------|----------|-----------|------|-------|------|
| CSV | Simple tabular data | Low | Small | Fast | Excel |
| JSON | APIs, nested data | Medium | Medium | Medium | Text editor |
| YAML | Config, readable format | Medium | Small | Fast | Text editor |
| Excel | Non-technical users | High | Large | Slow | Excel app |

## Troubleshooting

### "FileNotFoundError: test data file not found"
- Verify file is in `features/test_data/` directory
- Check filename spelling
- Use absolute path or adjust `data_dir` in TestDataManager

### "Invalid JSON/YAML"
- Check file syntax (use online JSON/YAML validators)
- Verify file encoding is UTF-8
- Check for special characters that need escaping

### "No sheet named 'X' in Excel file"
- Check sheet name spelling
- List available sheets: `openpyxl.load_workbook(path).sheetnames`
- Excel sheet names are case-sensitive

### "NaN or unexpected values from Excel"
- TestDataManager normalizes NaN to empty strings automatically
- Float values that are whole numbers (1.0) are converted to integers (1)
- Dates may need custom formatting

### "CSV values are strings not numbers"
- CSV format doesn't have type info (all values are strings)
- Convert manually: `int(value)`, `float(value)`, `datetime.strptime(value, "%Y-%m-%d")`
- Use JSON/Excel for typed data

## Advanced Patterns

### Data Fixtures with Setup/Teardown

```python
from features.utils.test_data_manager import TestDataManager
from features.queries.base_queries import UserQueries

@pytest.fixture
def user_test_data():
    """Load test data and create users in database"""
    test_data = TestDataManager().get_test_cases("users.csv")
    queries = UserQueries()
    
    # Create users in database
    for user_data in test_data:
        queries.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password']
        )
    
    yield test_data
    
    # Cleanup: Delete created users
    for user_data in test_data:
        queries.delete_user_by_email(user_data['email'])
```

### Environment-Specific Test Data

```python
from features.utils.config_manager import ConfigManager
from features.utils.test_data_manager import TestDataManager

config = ConfigManager()
env = config.get('environment')  # dev, stage, prod

# Load environment-specific data
test_data = TestDataManager().load_json(f"users_{env}.json")
```

### Test Data Builders

```python
class UserTestDataBuilder:
    """Builder pattern for flexible test data creation"""
    
    def __init__(self):
        self.data = TestDataManager().get_test_cases("users.csv")[0]
    
    def with_name(self, name):
        self.data['name'] = name
        return self
    
    def with_email(self, email):
        self.data['email'] = email
        return self
    
    def build(self):
        return self.data

# Usage
user = UserTestDataBuilder().with_name("John").with_email("john@example.com").build()
```

## Resources

- [JSON Schema Documentation](https://json-schema.org/)
- [YAML Specification](https://yaml.org/)
- [CSV Format RFC 4180](https://tools.ietf.org/html/rfc4180)
- [openpyxl Documentation](https://openpyxl.readthedocs.io/)
- [PyYAML Documentation](https://pyyaml.org/)

---

**Last Updated:** {{DATE}}
