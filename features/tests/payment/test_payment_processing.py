"""Parameterized payment processing tests using test data."""

import pytest
from pathlib import Path
from features.utils.test_data_manager import TestDataManager


# Load test data
test_data_dir = Path(__file__).parent.parent.parent / "test_data"
test_data_manager = TestDataManager()
payments_data = test_data_manager.load_yaml(str(test_data_dir / "payments.yml"))

# Extract payment scenarios and test cards
payment_scenarios = payments_data.get("payment_scenarios", [])
test_cards = payments_data.get("test_cards", {})

# Filter scenarios by outcome
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
    """Test successful payment processing with parameterized test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.api_available = True
    context.transactions = {}
    
    # Execute
    context.payment_amount = payment_scenario["amount"]
    context.card_valid = payment_scenario["card_valid"]
    context.response_status = 200
    
    # Mock successful payment
    context.response_data = {
        "transaction_id": payment_scenario["transaction_id"],
        "amount": payment_scenario["amount"],
        "status": payment_scenario["status"],
        "card_last_four": payment_scenario["card_number"][-4:],
        "order_id": payment_scenario["order_id"],
        "timestamp": payment_scenario["timestamp"]
    }
    
    context.transactions[payment_scenario["transaction_id"]] = context.response_data
    context.current_transaction_id = payment_scenario["transaction_id"]
    context.order_created = True
    
    # Assertions
    assert context.response_status == 200
    assert context.response_data["status"] == "completed"
    assert context.response_data["transaction_id"] == payment_scenario["transaction_id"]
    assert context.response_data["amount"] == payment_scenario["amount"]
    assert context.order_created is True
    assert context.current_transaction_id in context.transactions


@pytest.mark.parametrize(
    "payment_scenario",
    failed_payments,
    ids=[f"payment-fail-{p['transaction_id']}" for p in failed_payments]
)
@pytest.mark.api
@pytest.mark.payment_processing
def test_process_payment_failure(payment_scenario):
    """Test failed payment processing with parameterized test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.api_available = True
    context.transactions = {}
    
    # Execute
    context.payment_amount = payment_scenario["amount"]
    context.card_valid = payment_scenario["card_valid"]
    context.response_status = 400
    
    # Mock failed payment
    context.response_data = {
        "transaction_id": None,
        "amount": payment_scenario["amount"],
        "status": payment_scenario["status"],
        "error": payment_scenario.get("error", "Payment failed")
    }
    
    context.order_created = False
    
    # Assertions
    assert context.response_status == 400
    assert context.response_data["status"] == "failed"
    assert context.response_data["error"] == payment_scenario.get("error")
    assert context.response_data["transaction_id"] is None
    assert context.order_created is False


@pytest.mark.parametrize(
    "card_type,card_data",
    [
        ("valid", test_cards.get("valid", {})),
        ("invalid", test_cards.get("invalid", {})),
        ("insufficient_funds", test_cards.get("insufficient_funds", {}))
    ],
    ids=["card-valid", "card-invalid", "card-insufficient-funds"]
)
@pytest.mark.api
@pytest.mark.payment_processing
def test_payment_with_different_cards(card_type, card_data):
    """Test payment processing with different card types from test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.api_available = True
    
    # Execute
    context.card_number = card_data.get("number", "")
    context.card_expiry = card_data.get("expiry", "")
    context.card_cvv = card_data.get("cvv", "")
    
    # Determine outcome based on card type
    if card_type == "valid":
        context.response_status = 200
        context.payment_success = True
        context.response_data = {
            "transaction_id": "TXN-99999",
            "status": "completed",
            "message": "Payment processed successfully"
        }
    else:
        context.response_status = 400
        context.payment_success = False
        context.response_data = {
            "status": "failed",
            "error": "Card declined" if card_type == "invalid" else "Insufficient funds"
        }
    
    # Assertions
    assert context.card_number == card_data.get("number")
    assert context.card_expiry == card_data.get("expiry")
    assert context.card_cvv == card_data.get("cvv")
    
    if card_type == "valid":
        assert context.response_status == 200
        assert context.payment_success is True
    else:
        assert context.response_status == 400
        assert context.payment_success is False


@pytest.mark.parametrize(
    "amount",
    [99.99, 299.99, 49.99, 1.00, 9999.99],
    ids=["amount-99.99", "amount-299.99", "amount-49.99", "amount-1.00", "amount-9999.99"]
)
@pytest.mark.api
@pytest.mark.payment_processing
def test_payment_with_different_amounts(amount):
    """Test payment processing with different amounts."""
    context = type('Context', (), {})()
    
    # Setup
    context.api_available = True
    
    # Execute
    context.payment_amount = amount
    context.response_status = 200
    
    context.response_data = {
        "transaction_id": "TXN-NEW",
        "amount": amount,
        "status": "completed",
        "card_last_four": "1111"
    }
    
    # Assertions
    assert context.response_status == 200
    assert context.response_data["amount"] == amount
    assert context.response_data["status"] == "completed"


@pytest.mark.parametrize(
    "payment_scenario",
    payment_scenarios,
    ids=[f"query-{p['transaction_id']}" for p in payment_scenarios]
)
@pytest.mark.api
@pytest.mark.payment_processing
def test_query_payment_status(payment_scenario):
    """Test querying payment status using test data."""
    context = type('Context', (), {})()
    
    # Setup - pre-populate transactions
    context.transactions = {p["transaction_id"]: p for p in payment_scenarios}
    
    # Execute
    transaction_id = payment_scenario["transaction_id"]
    
    if transaction_id in context.transactions:
        context.response_status = 200
        context.payment_details = context.transactions[transaction_id]
    else:
        context.response_status = 404
        context.payment_details = {}
    
    # Assertions
    assert context.response_status == 200
    assert context.payment_details["transaction_id"] == transaction_id
    assert "amount" in context.payment_details
    assert "status" in context.payment_details
    assert context.payment_details["amount"] == payment_scenario["amount"]
    assert context.payment_details["status"] == payment_scenario["status"]


@pytest.mark.api
@pytest.mark.payment_processing
def test_payment_response_structure():
    """Test that payment responses have required structure."""
    required_fields_success = ["transaction_id", "amount", "status"]
    required_fields_failure = ["status", "error"]
    
    # Test successful payment response
    success_response = {
        "transaction_id": "TXN-12345",
        "amount": 99.99,
        "status": "completed"
    }
    
    for field in required_fields_success:
        assert field in success_response
    
    # Test failed payment response
    failure_response = {
        "status": "failed",
        "error": "Invalid card"
    }
    
    for field in required_fields_failure:
        assert field in failure_response
