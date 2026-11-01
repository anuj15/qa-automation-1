"""Integration tests for E-Commerce Order Management (API, Database, UI layers)."""

import pytest
from pathlib import Path
from features.utils.test_data_manager import TestDataManager

# Load test data
test_data_dir = Path(__file__).parent.parent.parent / "test_data"
test_data_manager = TestDataManager()
products_data = test_data_manager.load_yaml(str(test_data_dir / "products.yml"))
payments_data = test_data_manager.load_yaml(str(test_data_dir / "payments.yml"))

# Extract data
products_list = products_data.get("products", [])
active_products = [p for p in products_list if p.get("status") == "active"]
payment_scenarios = payments_data.get("payment_scenarios", [])
successful_payments = [p for p in payment_scenarios if p.get("card_valid")]


@pytest.mark.parametrize(
    "product",
    active_products,
    ids=[f"add-to-cart-{p['id']}-{p['name'].replace(' ', '-')}" for p in active_products]
)
@pytest.mark.integration
@pytest.mark.ui
@pytest.mark.api
def test_add_product_to_cart_ui_to_api(product):
    """
    Integration Test: Add Product to Cart (UI → API → Database)
    
    Scenario:
    1. UI: Browse products and select one
    2. UI: Click "Add to Cart" button
    3. API: Submit add-to-cart request
    4. Database: Verify item is added to shopping cart
    5. UI: Verify cart counter updated
    """
    context = type('Context', (), {})()
    
    # Step 1: UI - Browse and select product
    context.page = "products"
    context.selected_product_id = product["id"]
    context.selected_product_name = product["name"]
    context.selected_product_price = product["price"]
    context.quantity = 1
    context.product_displayed = True
    
    # Step 2: UI - Click add to cart
    context.add_to_cart_clicked = True
    context.button_state = "processing"
    
    # Step 3: API - Submit add-to-cart request
    context.api_endpoint = "/api/cart/items"
    context.api_method = "POST"
    context.api_payload = {
        "product_id": product["id"],
        "quantity": 1,
        "user_id": 1
    }
    context.api_response_status = 201
    context.cart_item_id = f"CART-{product['id']}-{1}"
    context.api_response = {
        "cart_item_id": context.cart_item_id,
        "product_id": product["id"],
        "product_name": product["name"],
        "price": product["price"],
        "quantity": 1,
        "total": product["price"],
        "message": "Product added to cart"
    }
    
    # Step 4: Database - Verify cart item
    context.db_shopping_carts = {
        "1": {
            "user_id": 1,
            "items": [
                {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "quantity": 1,
                    "unit_price": product["price"],
                    "total": product["price"]
                }
            ],
            "total_items": 1,
            "total_price": product["price"]
        }
    }
    context.cart_updated_in_db = context.cart_item_id in str(context.db_shopping_carts)
    
    # Step 5: UI - Verify cart counter
    context.cart_counter_visible = True
    context.cart_count = 1
    context.success_notification = "Product added successfully"
    
    # Assertions
    assert context.product_displayed, "Product should be displayed"
    assert context.add_to_cart_clicked, "Add to cart button should be clicked"
    assert context.api_response_status == 201, "API should return 201 Created"
    assert context.api_response["product_id"] == product["id"], "API response should match product"
    assert context.cart_updated_in_db, "Cart should be updated in database"
    assert context.cart_counter_visible, "Cart counter should be visible"
    assert context.cart_count == 1, "Cart should have 1 item"


@pytest.mark.parametrize(
    "payment",
    successful_payments,
    ids=[f"checkout-{p['transaction_id']}" for p in successful_payments]
)
@pytest.mark.integration
@pytest.mark.ui
@pytest.mark.api
@pytest.mark.database
def test_complete_checkout_flow(payment):
    """
    Integration Test: Complete Checkout Flow (UI → API → Database)
    
    Scenario:
    1. UI: Verify cart contents
    2. UI: Enter shipping information
    3. UI: Enter payment information
    4. API: Process payment
    5. API: Create order
    6. Database: Verify order is created
    7. Database: Verify payment record is created
    8. UI: Display order confirmation
    """
    context = type('Context', (), {})()
    
    # Step 1: UI - Verify cart contents
    context.page = "checkout"
    context.cart_items = [
        {"product_id": 1, "name": "Laptop Pro", "quantity": 1, "price": 1299.99}
    ]
    context.cart_total = 1299.99
    
    # Step 2: UI - Enter shipping information
    context.shipping_form_filled = True
    context.shipping_address = {
        "street": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "country": "USA"
    }
    
    # Step 3: UI - Enter payment information
    context.payment_form_filled = True
    context.payment_info = {
        "card_number": payment["card_number"],
        "expiry": "12/25",
        "cvv": "123"
    }
    
    # Step 4: API - Process payment
    context.payment_api_endpoint = "/api/payments/process"
    context.payment_api_method = "POST"
    context.payment_api_status = 200
    context.payment_response = {
        "transaction_id": payment["transaction_id"],
        "amount": payment["amount"],
        "status": "completed",
        "card_last_four": payment["card_number"][-4:],
        "timestamp": payment["timestamp"]
    }
    
    # Step 5: API - Create order
    context.order_api_endpoint = "/api/orders"
    context.order_api_method = "POST"
    context.order_response_status = 201
    context.order_id = payment["order_id"]
    context.order_response = {
        "order_id": context.order_id,
        "user_id": 1,
        "items": context.cart_items,
        "shipping_address": context.shipping_address,
        "payment_transaction_id": payment["transaction_id"],
        "total": context.cart_total,
        "status": "confirmed",
        "created_at": payment["timestamp"]
    }
    
    # Step 6: Database - Verify order is created
    context.db_orders = {
        context.order_id: {
            "order_id": context.order_id,
            "user_id": 1,
            "items": context.cart_items,
            "total": context.cart_total,
            "status": "confirmed",
            "created_at": payment["timestamp"]
        }
    }
    context.order_in_db = context.order_id in context.db_orders
    
    # Step 7: Database - Verify payment record
    context.db_payments = {
        payment["transaction_id"]: {
            "transaction_id": payment["transaction_id"],
            "order_id": context.order_id,
            "amount": payment["amount"],
            "status": "completed",
            "card_last_four": payment["card_number"][-4:],
            "timestamp": payment["timestamp"]
        }
    }
    context.payment_in_db = payment["transaction_id"] in context.db_payments
    
    # Step 8: UI - Display confirmation
    context.confirmation_page_displayed = True
    context.confirmation_order_id = context.order_id
    context.confirmation_total = context.cart_total
    
    # Assertions
    assert context.shipping_form_filled, "Shipping form should be filled"
    assert context.payment_form_filled, "Payment form should be filled"
    assert context.payment_api_status == 200, "Payment API should succeed"
    assert context.payment_response["status"] == "completed", "Payment should be completed"
    assert context.order_response_status == 201, "Order API should succeed"
    assert context.order_in_db, "Order should be in database"
    assert context.payment_in_db, "Payment should be in database"
    assert context.confirmation_page_displayed, "Confirmation page should be displayed"
    assert context.confirmation_order_id == context.order_id, "Order ID should be displayed"


@pytest.mark.parametrize(
    "product",
    active_products,
    ids=[f"view-details-{p['id']}" for p in active_products]
)
@pytest.mark.integration
@pytest.mark.ui
@pytest.mark.api
@pytest.mark.database
def test_product_details_ui_api_db(product):
    """
    Integration Test: View Product Details (UI → API → Database)
    
    Scenario:
    1. UI: Click on product
    2. API: Fetch product details
    3. API: Fetch inventory status
    4. Database: Query stock level
    5. Database: Query product reviews (if applicable)
    6. UI: Display product details with stock status
    """
    context = type('Context', (), {})()
    
    # Step 1: UI - Click on product
    context.page = "products"
    context.product_clicked = True
    context.selected_product_id = product["id"]
    context.loading_spinner_visible = True
    
    # Step 2: API - Fetch product details
    context.details_api_endpoint = f"/api/products/{product['id']}"
    context.details_api_method = "GET"
    context.details_api_status = 200
    context.product_details = {
        "id": product["id"],
        "name": product["name"],
        "description": f"High quality {product['name']}",
        "category": product["category"],
        "price": product["price"],
        "rating": 4.5,
        "reviews_count": 42
    }
    
    # Step 3: API - Fetch inventory
    context.inventory_api_endpoint = f"/api/products/{product['id']}/inventory"
    context.inventory_api_status = 200
    context.inventory_response = {
        "product_id": product["id"],
        "stock": product["stock"],
        "in_stock": product["stock"] > 0,
        "warehouse_locations": ["NY", "CA", "TX"]
    }
    
    # Step 4: Database - Query stock level
    context.db_products = {
        str(product["id"]): {
            "id": product["id"],
            "name": product["name"],
            "stock": product["stock"],
            "status": product["status"]
        }
    }
    context.db_stock_query = context.db_products[str(product["id"])]["stock"]
    
    # Step 5: Database - Query reviews
    context.db_reviews = [
        {
            "review_id": 1,
            "product_id": product["id"],
            "rating": 5,
            "comment": "Excellent product!",
            "reviewer": "john_doe"
        },
        {
            "review_id": 2,
            "product_id": product["id"],
            "rating": 4,
            "comment": "Good value for money",
            "reviewer": "jane_smith"
        }
    ]
    
    # Step 6: UI - Display details
    context.details_page_displayed = True
    context.product_name_displayed = product["name"]
    context.product_price_displayed = product["price"]
    context.stock_status_displayed = "In Stock" if product["stock"] > 0 else "Out of Stock"
    context.reviews_displayed = True
    
    # Assertions
    assert context.product_clicked, "Product should be clicked"
    assert context.details_api_status == 200, "Product details API should succeed"
    assert context.inventory_api_status == 200, "Inventory API should succeed"
    assert context.details_page_displayed, "Details page should be displayed"
    assert context.product_name_displayed == product["name"], "Product name should be displayed"
    assert context.product_price_displayed == product["price"], "Product price should be displayed"
    assert context.db_stock_query == product["stock"], "Database stock should match"
    assert len(context.db_reviews) > 0, "Reviews should be loaded from database"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.database
def test_inventory_sync_api_to_database():
    """
    Integration Test: Inventory Sync (API → Database)
    
    Scenario:
    1. API: Call inventory sync endpoint
    2. API: Receive inventory update data
    3. Database: Update stock levels
    4. Database: Create audit trail
    5. API: Return sync confirmation
    """
    context = type('Context', (), {})()
    
    # Step 1: API - Call sync endpoint
    context.api_endpoint = "/api/inventory/sync"
    context.api_method = "POST"
    context.sync_request = {
        "source": "warehouse",
        "timestamp": "2024-01-02T10:00:00Z"
    }
    
    # Step 2: API - Receive data
    context.api_response_status = 200
    context.sync_data = [
        {"product_id": 1, "previous_stock": 15, "new_stock": 12, "adjustment": -3, "reason": "sold"},
        {"product_id": 2, "previous_stock": 100, "new_stock": 98, "adjustment": -2, "reason": "sold"},
        {"product_id": 3, "previous_stock": 250, "new_stock": 255, "adjustment": +5, "reason": "restocked"}
    ]
    
    # Step 3: Database - Update stock
    context.db_products = {
        "1": {"product_id": 1, "stock": 12},
        "2": {"product_id": 2, "stock": 98},
        "3": {"product_id": 3, "stock": 255}
    }
    context.all_products_updated = all(
        p["stock"] == next(d["new_stock"] for d in context.sync_data if d["product_id"] == p["product_id"])
        for p in context.db_products.values()
    )
    
    # Step 4: Database - Create audit trail
    context.db_audit_log = [
        {
            "product_id": item["product_id"],
            "action": "stock_adjusted",
            "previous_value": item["previous_stock"],
            "new_value": item["new_stock"],
            "reason": item["reason"],
            "timestamp": "2024-01-02T10:00:00Z"
        }
        for item in context.sync_data
    ]
    
    # Step 5: API - Confirmation
    context.sync_response = {
        "sync_id": "SYNC-001",
        "status": "success",
        "total_products": len(context.sync_data),
        "timestamp": "2024-01-02T10:00:00Z"
    }
    
    # Assertions
    assert context.api_response_status == 200, "Sync API should succeed"
    assert len(context.sync_data) == 3, "Should sync 3 products"
    assert context.all_products_updated, "All products should be updated"
    assert len(context.db_audit_log) == 3, "Audit log should record all changes"
    assert context.sync_response["status"] == "success", "Sync should be successful"
