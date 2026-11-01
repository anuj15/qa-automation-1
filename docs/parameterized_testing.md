# Parameterized Testing Guide

This guide explains how to use pytest parameterization with test data files in this QA automation framework.

## Overview

Parameterized testing allows you to run the same test logic multiple times with different input data. This approach:

- ✅ Reduces code duplication
- ✅ Loads test data from external files (JSON, YAML, CSV, Excel)
- ✅ Makes tests data-driven
- ✅ Improves test coverage with minimal code
- ✅ Makes test reports easier to read (each variant gets its own result)

## Quick Start

### 1. Load Test Data

```python
from pathlib import Path
from features.utils.test_data_manager import TestDataManager

test_data_dir = Path(__file__).parent.parent.parent / "test_data"
test_data_manager = TestDataManager()

# Load from different formats
users_data = test_data_manager.load_json("users.json")
products_data = test_data_manager.load_yaml("products.yml")
records_data = test_data_manager.load_csv("data_records.csv")
payments_data = test_data_manager.load_yaml("payments.yml")
```

### 2. Parameterize Your Test

```python
import pytest

@pytest.mark.parametrize(
    "login_data",
    [
        {"username": "john_doe", "password": "SecurePass123!", "expected": "success"},
        {"username": "jane_smith", "password": "JaneSecure456!", "expected": "success"},
        {"username": "invalid", "password": "wrong", "expected": "failure"}
    ],
    ids=["user-john", "user-jane", "user-invalid"]  # Custom test IDs
)
def test_login(login_data):
    """Test login with multiple credentials"""
    username = login_data["username"]
    password = login_data["password"]
    # ... test logic
```

### 3. Run Parameterized Tests

```bash
# Run all tests
pytest features/tests/ -v

# Run specific parameterized test variant
pytest features/tests/users/test_user_authentication.py::test_user_login_success[login-john_doe] -v

# Run only parameterized tests for a marker
pytest -m user_authentication -v

# Filter by test ID substring
pytest -k "login-john" -v
```

## Real-World Examples in This Template

### Example 1: User Authentication Tests

**File:** `features/tests/users/test_user_authentication.py`

**Test Data File:** `features/test_data/users.json`

```json
{
  "users": [
    {"id": 1, "username": "john_doe", "email": "john.doe@example.com", "password": "SecurePass123!"},
    {"id": 2, "username": "jane_smith", "email": "jane.smith@example.com", "password": "JaneSecure456!"},
    {"id": 3, "username": "bob_johnson", "email": "bob.johnson@example.com", "password": "BobPass789!"}
  ],
  "test_credentials": {
    "valid_user": {"username": "john_doe", "password": "SecurePass123!"},
    "invalid_user": {"username": "john_doe", "password": "WrongPassword"}
  }
}
```

**Parameterized Test:**

```python
login_success_data = [
    {
        "username": "john_doe",
        "password": "SecurePass123!",
        "expected_page": "dashboard",
        "expected_message": "Welcome, John Doe"
    },
    {
        "username": "jane_smith",
        "password": "JaneSecure456!",
        "expected_page": "dashboard",
        "expected_message": "Welcome, Jane Smith"
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
    """Test successful user login with different credentials"""
    # Test runs twice: once for each login_scenario item
```

**Test Output:**

```
test_user_authentication.py::test_user_login_success[login-john_doe] PASSED
test_user_authentication.py::test_user_login_success[login-jane_smith] PASSED
test_user_authentication.py::test_user_login_failure[login-fail-0] PASSED
test_user_authentication.py::test_user_login_failure[login-fail-1] PASSED
test_user_authentication.py::test_user_login_failure[login-fail-2] PASSED
test_user_authentication.py::test_user_logout[user-john_doe] PASSED
test_user_authentication.py::test_user_logout[user-jane_smith] PASSED
test_user_authentication.py::test_user_logout[user-bob_johnson] PASSED
```

### Example 2: Product Search Tests

**File:** `features/tests/products/test_product_search.py`

**Test Data File:** `features/test_data/products.yml`

```yaml
products:
  - id: 1
    name: Laptop Pro
    category: Electronics
    price: 1299.99
    stock: 15
    status: active

search_scenarios:
  - keyword: "laptop"
    expected_results: 1
    expected_category: "Electronics"
  - keyword: "phone"
    expected_results: 0
    expected_category: null
```

**Parameterized Test:**

```python
search_scenarios = products_data.get("search_scenarios", [])

@pytest.mark.parametrize(
    "search_data",
    [
        {
            "keyword": s["keyword"],
            "expected_results": s["expected_results"],
            "expected_category": s["expected_category"]
        }
        for s in search_scenarios
    ],
    ids=[f"search-{s['keyword']}" for s in search_scenarios]
)
@pytest.mark.api
@pytest.mark.product_search
def test_search_products_by_keyword(search_data):
    """Test product search with different keywords"""
```

### Example 3: Database Operations with CSV Data

**File:** `features/tests/data_management/test_data_operations.py`

**Test Data File:** `features/test_data/data_records.csv`

```csv
id,name,description,category,price,status,quantity
1,Sample Data 1,First test data record,Active Records,99.99,active,10
2,Sample Data 2,Second test data record,Active Records,199.99,active,20
3,Sample Data 3,Third test data record,Archive,299.99,inactive,0
```

**Parameterized Test:**

```python
data_records = test_data_manager.load_csv("data_records.csv")
active_records = [r for r in data_records if r.get("status") == "active"]

@pytest.mark.parametrize(
    "test_record",
    active_records,
    ids=[f"read-{record['id']}" for record in active_records]
)
@pytest.mark.database
@pytest.mark.data_management
def test_read_data_record(test_record):
    """Test reading database records"""
```

### Example 4: Payment Processing with Multiple Test Cards

**File:** `features/tests/payment/test_payment_processing.py`

**Test Data File:** `features/test_data/payments.yml`

```yaml
payment_scenarios:
  - transaction_id: TXN-12345
    amount: 99.99
    card_number: "4111111111111111"
    card_valid: true
    status: completed
  - transaction_id: TXN-12347
    amount: 49.99
    card_number: "4000000000000002"
    card_valid: false
    status: failed

test_cards:
  valid:
    number: "4111111111111111"
    expiry: "12/25"
  invalid:
    number: "4000000000000002"
    expiry: "12/25"
```

**Parameterized Test:**

```python
successful_payments = [p for p in payment_scenarios if p.get("card_valid")]
failed_payments = [p for p in payment_scenarios if not p.get("card_valid")]

@pytest.mark.parametrize(
    "payment_scenario",
    successful_payments,
    ids=[f"payment-{p['transaction_id']}" for p in successful_payments]
)
@pytest.mark.api
@pytest.mark.payment_processing
def test_process_payment_success(payment_scenario):
    """Test successful payments from test data"""

@pytest.mark.parametrize(
    "payment_scenario",
    failed_payments,
    ids=[f"payment-fail-{p['transaction_id']}" for p in failed_payments]
)
@pytest.mark.api
@pytest.mark.payment_processing
def test_process_payment_failure(payment_scenario):
    """Test failed payments from test data"""
```

## Advanced Patterns

### 1. Indirect Parameterization

```python
@pytest.mark.parametrize("user_type", ["admin", "user", "guest"])
def test_access_control(user_type):
    # Test runs 3 times with different user_type values
    pass
```

### 2. Multiple Parameters

```python
@pytest.mark.parametrize(
    "username,password,expected",
    [
        ("john_doe", "SecurePass123!", True),
        ("invalid", "wrong", False),
        ("jane_smith", "JaneSecure456!", True)
    ]
)
def test_login(username, password, expected):
    # Test runs 3 times with different parameter combinations
    pass
```

### 3. Filtering Test Data

```python
# Only test active products
active_products = [p for p in products_list if p.get("status") == "active"]

@pytest.mark.parametrize(
    "product",
    active_products,
    ids=[f"product-{p['id']}" for p in active_products]
)
def test_active_products(product):
    pass
```

### 4. Dynamic Parameterization from Multiple Sources

```python
# Combine data from multiple files
users = test_data_manager.load_json("users.json")["users"]
products = test_data_manager.load_yaml("products.yml")["products"]

user_product_combinations = [
    (user, product) 
    for user in users 
    for product in products
]

@pytest.mark.parametrize(
    "user,product",
    user_product_combinations,
    ids=[f"{u['username']}-{p['name']}" for u, p in user_product_combinations]
)
def test_user_product_interaction(user, product):
    pass
```

## Best Practices

### ✅ DO

1. **Use meaningful test IDs** for easy identification in reports
   ```python
   ids=[f"login-{data['username']}" for data in login_data]
   ```

2. **Load data from external files** to keep tests maintainable
   ```python
   test_data = test_data_manager.load_json("test_data.json")
   ```

3. **Filter test data appropriately**
   ```python
   successful_tests = [t for t in all_tests if t["expected"] == "pass"]
   ```

4. **Use pytest markers** for selective test execution
   ```python
   @pytest.mark.parametrize(...)
   @pytest.mark.api
   @pytest.mark.slow
   def test_something(data):
       pass
   ```

5. **Keep test data organized** in logical files
   ```
   test_data/
   ├── users.json
   ├── products.yml
   ├── payments.yml
   └── data_records.csv
   ```

### ❌ DON'T

1. **Hardcode test data** in test files
   ```python
   # BAD
   test_users = [{"username": "john", "password": "123"}]
   
   # GOOD
   test_users = test_data_manager.load_json("users.json")["users"]
   ```

2. **Create parameter combinations explosively**
   ```python
   # BAD - 100 test variants when you only need 5
   @pytest.mark.parametrize("user", users)
   @pytest.mark.parametrize("product", products)
   @pytest.mark.parametrize("status", statuses)
   def test_something(user, product, status):
       pass
   
   # GOOD - targeted combinations
   targeted_combos = [(u, p) for u, p in zip(users, products)]
   @pytest.mark.parametrize("user,product", targeted_combos)
   def test_something(user, product):
       pass
   ```

3. **Skip cleaning up test data** between runs
   ```python
   # Use fixtures for setup/teardown
   @pytest.fixture
   def clean_test_data():
       # setup
       yield
       # cleanup
   ```

## Test Data File Organization

```
features/test_data/
├── users.json                  # User credentials and profiles
├── products.yml                # Product catalog and search scenarios
├── data_records.csv            # Database records for CRUD tests
├── payments.yml                # Payment scenarios and test cards
└── test_data.xlsx              # Multi-sheet Excel test data
```

## TestDataManager API

```python
from features.utils.test_data_manager import TestDataManager

manager = TestDataManager()

# Load different formats
json_data = manager.load_json("file.json")
yaml_data = manager.load_yaml("file.yml")
csv_data = manager.load_csv("file.csv")
excel_data = manager.load_excel("file.xlsx", sheet_name="Sheet1")

# Auto-detect format
data = manager.load("file.json")  # Works with any format

# Filter and slice data
filtered = manager.filter_test_cases(data, column="status", value="active")
sliced = manager.slice_test_cases(data, start=0, end=10)

# Get specific test cases
test_cases = manager.get_test_cases(data, ["case1", "case2"])
```

## Running Parameterized Tests

```bash
# Run all parameterized tests
pytest features/tests/ -v

# Run specific feature area
pytest features/tests/users/ -v

# Run specific test function with all parameters
pytest features/tests/users/test_user_authentication.py::test_user_login_success -v

# Run specific parameter variant
pytest "features/tests/users/test_user_authentication.py::test_user_login_success[login-john_doe]" -v

# Run tests matching pattern
pytest -k "login_success" -v

# Run tests by marker
pytest -m user_authentication -v

# Run with coverage
pytest features/tests/ --cov=features --cov-report=html

# Generate Allure report
pytest features/tests/ --alluredir=features/reports/allure-results
allure serve features/reports/allure-results
```

## Troubleshooting

### Issue: Tests not being discovered

**Solution:** Ensure test file name starts with `test_` and test function names start with `test_`

```python
# ✅ Correct
def test_user_login(data):
    pass

# ❌ Wrong
def verify_user_login(data):
    pass
```

### Issue: Test IDs not displaying correctly

**Solution:** Use custom IDs that are URL-safe (no special characters)

```python
# ✅ Correct
ids=[f"user-{u['username']}" for u in users]  # "user-john_doe"

# ❌ Wrong
ids=[f"user-{u['name']}" for u in users]  # "user-John Doe" (has spaces)
```

### Issue: Too many test variants

**Solution:** Filter test data before parameterizing

```python
# ✅ Only parameterize necessary data
successful_tests = [t for t in all_tests if t["expected"] == "pass"]

@pytest.mark.parametrize("test", successful_tests)
def test_success(test):
    pass
```

## Summary

Parameterized testing with test data files provides:

- 📊 **Data-driven testing** - separate concerns (test logic vs. test data)
- 🔄 **DRY principle** - write test once, run with many datasets
- 📈 **Better coverage** - test more scenarios with less code
- 📋 **Easy maintenance** - update test data without changing code
- 📄 **Clear reports** - each variant shows as separate test result
- 🎯 **Focused debugging** - run specific parameter variants

Start using parameterization today for more maintainable, scalable tests!
