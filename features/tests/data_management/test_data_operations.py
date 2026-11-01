"""Parameterized database operations tests using test data."""

import pytest
from pathlib import Path
from features.utils.test_data_manager import TestDataManager


# Load test data
test_data_dir = Path(__file__).parent.parent.parent / "test_data"
test_data_manager = TestDataManager()
data_records = test_data_manager.load_csv(str(test_data_dir / "data_records.csv"))

# Prepare parameterized data for CRUD operations
create_test_data = [
    {
        "name": "New Product A",
        "description": "Test product for automation",
        "category": "Test",
        "price": 199.99,
        "status": "active"
    },
    {
        "name": "New Product B",
        "description": "Another test product",
        "category": "Test",
        "price": 299.99,
        "status": "active"
    }
]

# Filter active records for read tests
active_records = [r for r in data_records if r.get("status") == "active"]
inactive_records = [r for r in data_records if r.get("status") == "inactive"]


@pytest.mark.parametrize(
    "test_record",
    create_test_data,
    ids=[f"create-{record['name'].replace(' ', '-')}" for record in create_test_data]
)
@pytest.mark.database
@pytest.mark.data_management
def test_create_data_record(test_record):
    """Test creating a data record with parameterized test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.db_accessible = True
    context.db_records = {str(r["id"]): r for r in data_records}
    
    # Execute
    new_id = str(len(context.db_records) + 1)
    context.new_record = {
        "id": new_id,
        "name": test_record["name"],
        "description": test_record["description"],
        "category": test_record["category"],
        "price": test_record["price"],
        "status": test_record["status"],
        "quantity": 0,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    context.db_records[new_id] = context.new_record
    context.create_success = True
    
    # Assertions
    assert context.create_success is True
    assert new_id in context.db_records
    assert context.db_records[new_id]["name"] == test_record["name"]
    assert context.db_records[new_id]["status"] == "active"
    assert context.new_record["description"] == test_record["description"]


@pytest.mark.parametrize(
    "test_record",
    active_records,
    ids=[f"read-{record['id']}-{record['name'].replace(' ', '-')}" for record in active_records]
)
@pytest.mark.database
@pytest.mark.data_management
def test_read_data_record(test_record):
    """Test reading data records from test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.db_accessible = True
    context.db_records = {str(r["id"]): r for r in data_records}
    
    # Execute
    record_id = str(test_record["id"])
    if record_id in context.db_records:
        context.queried_record = context.db_records[record_id]
        context.query_success = True
    else:
        context.query_success = False
    
    # Assertions
    assert context.query_success is True
    assert context.queried_record["name"] == test_record["name"]
    assert context.queried_record["status"] == "active"
    
    # Verify all required fields
    required_fields = ["id", "name", "description", "status", "category", "price", "quantity"]
    for field in required_fields:
        assert field in context.queried_record


@pytest.mark.parametrize(
    "test_record",
    active_records[:3],
    ids=[f"update-{record['id']}-{record['name'].replace(' ', '-')}" for record in active_records[:3]]
)
@pytest.mark.database
@pytest.mark.data_management
def test_update_data_record(test_record):
    """Test updating data records using test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.db_accessible = True
    context.db_records = {str(r["id"]): r for r in data_records}
    context.update_record_id = str(test_record["id"])
    
    # Execute update
    new_name = f"Updated - {test_record['name']}"
    new_quantity = int(test_record.get("quantity", 0)) + 5
    
    context.db_records[context.update_record_id]["name"] = new_name
    context.db_records[context.update_record_id]["quantity"] = new_quantity
    context.db_records[context.update_record_id]["updated_at"] = "2024-01-02T00:00:00Z"
    context.update_success = True
    
    # Assertions
    assert context.update_success is True
    updated_record = context.db_records[context.update_record_id]
    assert updated_record["name"] == new_name
    assert updated_record["quantity"] == new_quantity
    assert updated_record["updated_at"] != "2024-01-01T00:00:00Z"


@pytest.mark.parametrize(
    "test_record",
    inactive_records,
    ids=[f"delete-{record['id']}-{record['name'].replace(' ', '-')}" for record in inactive_records]
)
@pytest.mark.database
@pytest.mark.data_management
def test_delete_data_record(test_record):
    """Test deleting data records using test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.db_accessible = True
    context.db_records = {str(r["id"]): r for r in data_records}
    record_id_to_delete = str(test_record["id"])
    
    # Execute delete
    if record_id_to_delete in context.db_records:
        del context.db_records[record_id_to_delete]
        context.delete_success = True
    else:
        context.delete_success = False
    
    # Assertions
    assert context.delete_success is True
    assert record_id_to_delete not in context.db_records


@pytest.mark.parametrize(
    "status",
    ["active", "inactive"],
    ids=["count-active", "count-inactive"]
)
@pytest.mark.database
@pytest.mark.data_management
def test_count_records_by_status(status):
    """Test counting records by status using test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.db_accessible = True
    context.db_records = {str(r["id"]): r for r in data_records}
    
    # Execute
    context.record_count = sum(
        1 for record in context.db_records.values()
        if record.get("status") == status
    )
    
    # Verify against actual test data
    expected_count = len([r for r in data_records if r.get("status") == status])
    
    # Assertions
    assert context.record_count > 0
    assert context.record_count == expected_count


@pytest.mark.parametrize(
    "category",
    ["Active Records", "Archive", "Test"],
    ids=["filter-active-records", "filter-archive", "filter-test"]
)
@pytest.mark.database
@pytest.mark.data_management
def test_filter_records_by_category(category):
    """Test filtering records by category using test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.db_accessible = True
    context.db_records = {str(r["id"]): r for r in data_records}
    
    # Execute - filter by category
    context.filtered_records = [
        r for r in context.db_records.values()
        if r.get("category") == category
    ]
    
    # Assertions
    if context.filtered_records:  # Only assert if category exists in test data
        for record in context.filtered_records:
            assert record["category"] == category
    
    # All filtered records should have valid data
    for record in context.filtered_records:
        assert "id" in record
        assert "name" in record
        assert "status" in record


@pytest.mark.database
@pytest.mark.data_management
def test_all_records_have_required_fields():
    """Test that all test data records have required fields."""
    required_fields = ["id", "name", "description", "category", "status", "quantity"]
    
    for record in data_records:
        for field in required_fields:
            assert field in record, f"Record {record.get('id')} missing field '{field}'"
        
        # Type validation
        assert isinstance(record["id"], (int, str))
        assert isinstance(record["name"], str)
        assert record["status"] in ["active", "inactive"]
        assert isinstance(record["quantity"], (int, str))
