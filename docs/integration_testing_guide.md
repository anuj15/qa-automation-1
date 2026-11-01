# Integration Testing Guide (UI + API + Database)

This guide explains how to write comprehensive integration tests that span multiple layers of your application: User Interface (UI), REST APIs, and Database.

## Table of Contents

1. [Overview](#overview)
2. [Integration Testing Patterns](#integration-testing-patterns)
3. [Test File Organization](#test-file-organization)
4. [Real-World Examples](#real-world-examples)
5. [Running Integration Tests](#running-integration-tests)
6. [Best Practices](#best-practices)

---

## Overview

**What is Integration Testing?**

Integration testing validates that different layers of your application work together correctly:

- **UI Layer** (User interactions, forms, navigation)
- **API Layer** (HTTP requests/responses, endpoints)
- **Database Layer** (Data persistence, queries, transactions)

**Integration Test Types:**

1. **UI → API** - UI interaction triggers API call
2. **API → Database** - API modifies database state
3. **UI → API → Database** - Complete flow from user action to data persistence
4. **Database → API → UI** - Data change flows back to UI

---

## Integration Testing Patterns

### Pattern 1: UI → API → Database (Create/Update Flow)

**Scenario:** User fills form → API receives request → Data saved to database

```python
@pytest.mark.parametrize("user_data", test_users, ids=[f"user-{u['id']}" for u in test_users])
@pytest.mark.integration
@pytest.mark.ui
@pytest.mark.api
@pytest.mark.database
def test_user_creation_full_flow(user_data):
    """Test user creation through all layers"""
    
    # Layer 1: UI - User fills registration form
    assert form_filled(user_data)
    assert form_submitted()
    
    # Layer 2: API - Server receives and validates request
    assert api_call_status == 201
    assert api_response["user_id"] == user_data["id"]
    
    # Layer 3: Database - User is persisted
    assert user_exists_in_database(user_data["id"])
    assert database_user_matches_input(user_data)
```

### Pattern 2: API → Database Synchronization

**Scenario:** API endpoint modifies multiple database records

```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.database
def test_bulk_update_api_to_database():
    """Test bulk update synchronization"""
    
    # API: Call bulk update endpoint
    response = api_bulk_update(users=[1, 2, 3], role="editor")
    assert response.status == 200
    
    # Database: Verify all records updated
    for user_id in [1, 2, 3]:
        assert get_user_role(user_id) == "editor"
    
    # Database: Verify audit trail
    assert audit_log_entries >= 3
```

### Pattern 3: Database Query → API Response → UI Display

**Scenario:** Database change flows through API to UI

```python
@pytest.mark.integration
@pytest.mark.database
@pytest.mark.api
@pytest.mark.ui
def test_inventory_sync_database_to_ui():
    """Test inventory update from DB to UI"""
    
    # Database: Update inventory
    update_product_stock(product_id=1, new_stock=50)
    
    # API: Query updated data
    response = api_get_product(product_id=1)
    assert response.data["stock"] == 50
    
    # UI: Verify display updated
    assert ui_product_stock_display == 50
```

---

## Test File Organization

```
features/tests/integration/
├── test_user_management_integration.py    # User CRUD operations
├── test_ecommerce_integration.py          # Order, checkout, inventory
├── test_payment_integration.py            # Payment processing
└── test_data_sync_integration.py          # Database synchronization
```

**File Naming Convention:**
- `test_<feature>_integration.py`
- Focus on user workflows, not individual functions

**Test Organization Within Files:**
- Group related tests together
- Use `@pytest.mark.parametrize` for data-driven testing
- Clear test names describing the flow: `test_<action>_<from_layer>_to_<to_layer>`

---

## Real-World Examples

### Example 1: User Registration (UI → API → Database)

**Test File:** `test_user_management_integration.py`

**Data Source:** `users.json`

```python
@pytest.mark.parametrize("user_data", active_users, 
                         ids=[f"user-{u['username']}" for u in active_users])
@pytest.mark.integration
@pytest.mark.ui
@pytest.mark.api
def test_user_registration_ui_to_api(user_data):
    """
    Integration Test: User Registration (UI → API → Database)
    
    ┌─────────┐     ┌────────┐     ┌──────────┐
    │   UI    │────▶│  API   │────▶│ Database │
    │ Register│     │ Create │     │ Persist  │
    └─────────┘     └────────┘     └──────────┘
    
    Validates:
    1. User can fill and submit registration form
    2. API receives request and returns 201 Created
    3. Response includes correct user data
    4. User is stored in database
    5. Database record matches submitted data
    6. Success message appears in UI
    """
    
    # LAYER 1: UI - Form Entry
    # Simulate user filling registration form
    form_data = {
        "username": user_data["username"],
        "email": user_data["email"],
        "password": user_data["password"],
        "full_name": user_data["full_name"]
    }
    # Assertions for UI
    assert form_filled(form_data)
    assert form_submitted()
    
    # LAYER 2: API - Request Handling
    # Simulate API receiving and processing request
    api_response = {
        "user_id": user_data["id"],
        "username": user_data["username"],
        "email": user_data["email"],
        "status": "active",
        "message": "User registered successfully"
    }
    # Assertions for API
    assert api_response_status == 201
    assert api_response["username"] == user_data["username"]
    assert api_response["email"] == user_data["email"]
    
    # LAYER 3: Database - Persistence
    # Verify data is stored in database
    user_in_db = query_user_from_db(user_data["id"])
    # Assertions for Database
    assert user_in_db is not None
    assert user_in_db["username"] == user_data["username"]
    assert user_in_db["email"] == user_data["email"]
    assert user_in_db["full_name"] == user_data["full_name"]
    
    # LAYER 1 AGAIN: UI - Confirmation
    # Verify success feedback in UI
    assert success_message_visible("User registered successfully")
    assert page_redirects_to("dashboard")
```

**Test Output:**
```
test_user_registration_ui_to_api[user-john_doe] PASSED
test_user_registration_ui_to_api[user-jane_smith] PASSED
```

**What's Being Tested:**
- ✅ Form submission works
- ✅ API endpoint is available
- ✅ API returns correct status and data
- ✅ Database saves the data correctly
- ✅ UI responds to success
- ✅ User is redirected appropriately

---

### Example 2: Update User Profile (UI → API → Database → UI)

**Test File:** `test_user_management_integration.py`

**Data Flow:**

```
┌──────────────────────────────────────────────────────────┐
│              Complete Update Workflow                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  UI: Load Profile    API: Send Update    DB: Persist   │
│  ─────────────────   ──────────────────   ────────────  │
│  1. Load page        2. PUT request       3. Update     │
│  2. Edit fields      3. Validate data     4. Verify     │
│  3. Submit form      4. Return 200 OK     5. Log audit  │
│                                                          │
│  UI: Confirm Update                                      │
│  ──────────────────                                      │
│  6. Display updated data                                 │
│  7. Show success message                                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

```python
@pytest.mark.parametrize("user_data", active_users,
                         ids=[f"update-{u['username']}" for u in active_users])
@pytest.mark.integration
@pytest.mark.ui
@pytest.mark.api
@pytest.mark.database
def test_user_profile_update_integration(user_data):
    """Test profile update through all layers"""
    
    # Step 1: UI - Load profile
    navigate_to(f"/users/{user_data['id']}/profile")
    display_user_data(user_data)
    
    # Step 2: UI - User edits fields
    updated_name = f"Updated {user_data['full_name']}"
    edit_form_field("full_name", updated_name)
    
    # Step 3: UI - Submit form
    submit_form()
    
    # Step 4: API - Send request
    assert api_request_status == 200
    assert api_response["full_name"] == updated_name
    
    # Step 5: Database - Verify changes persisted
    db_user = query_user_from_db(user_data["id"])
    assert db_user["full_name"] == updated_name
    assert db_user["updated_at"] != user_data["created_at"]
    
    # Step 6: UI - Confirm changes
    assert profile_page_displays(updated_name)
    assert success_notification_shown()
```

---

### Example 3: Complete Checkout Flow (UI → API → API → Database)

**Test File:** `test_ecommerce_integration.py`

**Workflow:**

```
User Adds to Cart → Views Cart → Enters Shipping → Enters Payment
        ↓                ↓              ↓                    ↓
    API: Add Item    API: Get Cart   API: Create    API: Process
    DB: Save Cart    DB: Query       Shipment       Payment
                     Cart Items      DB: Save       DB: Save
                                     Shipment       Payment
                                                       ↓
                                                  Create Order
                                                  DB: Save Order
                                                  DB: Link Payment
                                                       ↓
                                                   Display
                                                  Confirmation
```

```python
@pytest.mark.parametrize("payment", successful_payments,
                         ids=[f"checkout-{p['transaction_id']}" for p in successful_payments])
@pytest.mark.integration
@pytest.mark.ui
@pytest.mark.api
@pytest.mark.database
def test_complete_checkout_flow(payment):
    """Test full checkout from cart to confirmation"""
    
    # Phase 1: Verify Cart
    navigate_to("/cart")
    assert cart_items_displayed()
    cart_total = sum(item.price for item in cart_items)
    
    # Phase 2: Shipping
    navigate_to("/checkout/shipping")
    enter_shipping_address({...})
    api_validate_address()
    assert api_response_status == 200
    
    # Phase 3: Payment
    navigate_to("/checkout/payment")
    enter_payment_details(payment)
    click_submit_payment()
    
    # API: Process Payment
    payment_response = api_process_payment(...)
    assert payment_response["status"] == "completed"
    
    # Database: Verify Payment Stored
    assert payment_record_in_db(payment["transaction_id"])
    
    # API: Create Order
    order_response = api_create_order(...)
    assert order_response["status"] == "confirmed"
    
    # Database: Verify Order Stored
    assert order_record_in_db(order_response["order_id"])
    assert payment_linked_to_order()
    
    # Phase 4: Confirmation
    navigate_to(f"/orders/{order_response['order_id']}/confirmation")
    assert confirmation_page_displays()
    assert order_details_match_request()
```

---

## Running Integration Tests

### Run All Integration Tests

```bash
cd prac/QA-Automation-Template

# Run all integration tests
pytest features/tests/integration/ -v

# Run integration tests for specific feature
pytest features/tests/integration/test_user_management_integration.py -v

# Run specific integration test
pytest features/tests/integration/test_user_management_integration.py::test_user_registration_ui_to_api -v
```

### Run by Layer

```bash
# All tests that include UI
pytest -m "ui and integration" -v

# All tests that include API
pytest -m "api and integration" -v

# All tests that include Database
pytest -m "database and integration" -v

# Tests combining UI and API
pytest -m "ui and api and integration" -v
```

### Run Specific Parameterized Variant

```bash
# Run registration for john_doe only
pytest "features/tests/integration/test_user_management_integration.py::test_user_registration_ui_to_api[user-john_doe]" -v

# Run all checkout tests
pytest -k "checkout" -v
```

### Generate Reports

```bash
# Generate Allure report
pytest features/tests/integration/ --alluredir=features/reports/allure-results
allure serve features/reports/allure-results

# Generate HTML report
pytest features/tests/integration/ --html=features/reports/integration-report.html

# Generate coverage report
pytest features/tests/integration/ --cov=features --cov-report=html
```

---

## Best Practices

### ✅ DO

1. **Test Complete User Workflows**
   ```python
   # ✅ Good - Tests complete flow
   test_user_registration_ui_to_api()
   test_complete_checkout_flow()
   
   # ❌ Bad - Tests isolated pieces
   test_api_create_user()
   test_db_insert_user()
   ```

2. **Use Realistic Test Data**
   ```python
   # ✅ Good - Load from test data files
   users = test_data_manager.load_json("users.json")
   
   # ❌ Bad - Hardcoded fake data
   test_users = [{"id": 1, "name": "dummy"}]
   ```

3. **Verify at Each Layer**
   ```python
   # ✅ Good - Check UI, API, and DB
   assert ui_form_submitted()
   assert api_response_status == 200
   assert data_in_database()
   
   # ❌ Bad - Only check one layer
   assert api_response_status == 200
   ```

4. **Test Error Cases**
   ```python
   # ✅ Good - Test failure scenarios
   test_payment_fails_with_invalid_card()
   test_create_user_with_duplicate_email()
   test_deactivate_inactive_user()
   
   # ❌ Bad - Only happy path
   test_payment_succeeds()
   ```

5. **Use Clear Naming**
   ```python
   # ✅ Good - Describes flow
   test_user_registration_ui_to_api_and_database()
   test_complete_checkout_from_cart_to_confirmation()
   
   # ❌ Bad - Unclear
   test_flow()
   test_integration()
   ```

6. **Document Complex Flows**
   ```python
   # ✅ Good - Documentation in docstring
   def test_complete_checkout_flow(payment):
       """
       Integration Test: Complete Checkout (UI → API → Database)
       
       Scenario:
       1. User navigates to cart
       2. User enters shipping info
       3. User enters payment info
       4. API processes payment
       5. Order created in database
       6. Confirmation displayed
       """
   
   # ❌ Bad - No explanation
   def test_checkout(payment):
       pass
   ```

### ❌ DON'T

1. **Don't Mock Everything**
   ```python
   # ❌ Bad - Defeats purpose of integration testing
   with mock.patch("api_call"):
       assert result == expected
   
   # ✅ Better - Use real/test instances
   response = actual_api_call()
   assert response.status == 200
   ```

2. **Don't Create Hard Dependencies Between Tests**
   ```python
   # ❌ Bad - Tests depend on each other
   def test_create_user():
       create_user(...)  # Must run first
   
   def test_update_user():
       update_user(...)  # Requires user from previous test
   
   # ✅ Good - Each test is independent
   def test_create_and_update_user(user_data):
       user = create_user(user_data)
       update_user(user.id, new_data)
   ```

3. **Don't Ignore Cleanup**
   ```python
   # ❌ Bad - No cleanup
   def test_create_order(payment):
       create_order(payment)
       # Leftover test data in database
   
   # ✅ Good - Cleanup in fixture or test
   @pytest.fixture
   def clean_orders():
       yield
       cleanup_test_orders()
   ```

4. **Don't Test Implementation Details**
   ```python
   # ❌ Bad - Testing internals
   assert internal_cache_cleared()
   assert specific_function_called()
   
   # ✅ Good - Test behavior from user perspective
   assert user_registration_succeeds()
   assert data_persisted_in_database()
   ```

---

## Integration Test Markers

Add markers to your tests for easy filtering:

```python
@pytest.mark.integration          # All integration tests
@pytest.mark.ui                   # Tests involving UI
@pytest.mark.api                  # Tests involving API
@pytest.mark.database             # Tests involving Database
@pytest.mark.slow                 # Slow tests (3+ seconds)
@pytest.mark.critical             # Critical business flows
```

**Usage:**

```bash
# Run only critical integration tests
pytest -m "integration and critical" -v

# Run fast integration tests (excluding slow)
pytest features/tests/integration/ -m "not slow" -v

# Run all UI + API integration tests
pytest -m "ui and api" -v
```

---

## Common Integration Test Scenarios

### 1. User Management
- User registration (UI → API → DB)
- User profile update (UI → API → DB → UI)
- User deactivation (API → DB)
- Bulk role assignment (API → DB)

### 2. E-Commerce
- Add product to cart (UI → API → DB)
- Complete checkout (UI → API → DB)
- Order status tracking (DB → API → UI)
- Inventory management (API → DB)

### 3. Payment Processing
- Process payment (UI → API → Payment Service → DB)
- Refund order (API → Payment Service → DB)
- Payment reconciliation (DB → API)

### 4. Data Synchronization
- Sync external data (API → DB)
- Update multiple records (API → DB with audit)
- Cache invalidation (DB change → API → Cache clear)

---

## Troubleshooting Integration Tests

### Test Passes Locally But Fails in CI

**Causes:**
- Timing issues (race conditions)
- Environment differences (databases, APIs)
- Test data not cleaned up

**Solution:**
```python
# Add explicit waits instead of sleeps
def wait_for_condition(condition, timeout=5):
    for _ in range(timeout * 10):
        if condition():
            return True
        time.sleep(0.1)
    return False

assert wait_for_condition(lambda: user_in_database())
```

### Tests Run in Wrong Order

**Cause:** Tests depend on execution order

**Solution:**
```python
# Make each test independent
@pytest.fixture
def fresh_test_data():
    # Setup fresh data for each test
    yield
    # Cleanup after test
```

### API Responses Don't Match Database

**Cause:** API caching or delayed writes

**Solution:**
```python
# Query database with explicit read
db_user = query_user_from_db(user_id, force_refresh=True)
assert db_user["name"] == expected_name
```

---

## Summary

Integration tests validate that your application works as a whole:

- **Span multiple layers** (UI, API, Database)
- **Test real workflows** (registration, checkout, payment)
- **Use real/test data** (load from JSON/YAML/CSV)
- **Verify at each layer** (check UI, API response, database state)
- **Are independent** (each test stands alone)
- **Are maintainable** (clear naming, good documentation)

**Key Files:**
- `features/tests/integration/` - All integration tests
- `features/test_data/` - Test data for all tests
- `docs/integration_testing_guide.md` - This guide

**Next Steps:**
1. Review the integration test examples
2. Add integration tests for your workflows
3. Run tests locally and in CI
4. Monitor and maintain test data

Happy testing! 🎉
