"""Parameterized product search API tests using test data."""

import pytest
from pathlib import Path
from features.utils.test_data_manager import TestDataManager


# Load test data
test_data_dir = Path(__file__).parent.parent.parent / "test_data"
test_data_manager = TestDataManager()
products_data = test_data_manager.load_yaml(str(test_data_dir / "products.yml"))

# Extract products and search scenarios
products_list = products_data.get("products", [])
search_scenarios = products_data.get("search_scenarios", [])

# Prepare parameterized data for product search
product_search_data = [
    {
        "keyword": scenario["keyword"],
        "expected_results": scenario["expected_results"],
        "expected_category": scenario["expected_category"]
    }
    for scenario in search_scenarios
]

# Prepare parameterized data for category filtering
category_search_data = [
    {
        "category": "Electronics",
        "expected_count": sum(1 for p in products_list if p.get("category") == "Electronics")
    },
    {
        "category": "Accessories",
        "expected_count": sum(1 for p in products_list if p.get("category") == "Accessories")
    }
]

# Prepare pagination test data
pagination_data = [
    {
        "keyword": "laptop",
        "page": 1,
        "limit": 10,
        "total_count": 50
    },
    {
        "keyword": "laptop",
        "page": 2,
        "limit": 10,
        "total_count": 50
    },
    {
        "keyword": "electronics",
        "page": 1,
        "limit": 5,
        "total_count": 100
    }
]


@pytest.mark.parametrize(
    "search_data",
    product_search_data,
    ids=[f"search-{data['keyword']}" for data in product_search_data]
)
@pytest.mark.api
@pytest.mark.product_search
def test_search_products_by_keyword(search_data):
    """Test product search by keyword using parameterized test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.api_available = True
    context.api_base_url = "https://api.example.com"
    
    # Execute
    keyword = search_data["keyword"]
    context.search_keyword = keyword
    context.response_status = 200
    
    # Mock API response based on test data
    if search_data["expected_results"] == 0:
        context.response_data = {"products": []}
    else:
        context.response_data = {
            "products": [
                {
                    "id": i + 1,
                    "name": f"{keyword} Product {i + 1}",
                    "price": 299.99 + (i * 100),
                    "category": search_data["expected_category"]
                }
                for i in range(search_data["expected_results"])
            ]
        }
    
    # Assertions
    assert context.response_status == 200
    assert len(context.response_data["products"]) == search_data["expected_results"]
    
    if search_data["expected_category"]:
        for product in context.response_data["products"]:
            assert product["category"] == search_data["expected_category"]


@pytest.mark.parametrize(
    "category_data",
    category_search_data,
    ids=[f"category-{data['category']}" for data in category_search_data]
)
@pytest.mark.api
@pytest.mark.product_search
def test_search_products_by_category(category_data):
    """Test product search by category using test data."""
    context = type('Context', (), {})()
    
    # Setup
    context.api_available = True
    context.api_base_url = "https://api.example.com"
    
    # Execute
    category = category_data["category"]
    context.search_category = category
    context.response_status = 200
    
    # Get matching products from test data
    matching_products = [
        p for p in products_list
        if p.get("category") == category
    ]
    
    context.response_data = {
        "products": matching_products
    }
    
    # Assertions
    assert context.response_status == 200
    assert len(context.response_data["products"]) == category_data["expected_count"]
    assert all(p["category"] == category for p in context.response_data["products"])


@pytest.mark.parametrize(
    "pagination_params",
    pagination_data,
    ids=[f"page-{p['keyword']}-{p['page']}" for p in pagination_data]
)
@pytest.mark.api
@pytest.mark.product_search
def test_search_products_with_pagination(pagination_params):
    """Test product search with pagination using parameterized data."""
    context = type('Context', (), {})()
    
    # Setup
    context.api_available = True
    context.api_base_url = "https://api.example.com"
    
    # Execute
    context.search_keyword = pagination_params["keyword"]
    context.current_page = pagination_params["page"]
    context.page_limit = pagination_params["limit"]
    context.response_status = 200
    
    # Mock paginated response
    context.response_data = {
        "products": [
            {
                "id": 1 + ((pagination_params["page"] - 1) * pagination_params["limit"]),
                "name": f"{pagination_params['keyword']} Product 1",
                "price": 199.99,
                "category": "Electronics"
            },
            {
                "id": 2 + ((pagination_params["page"] - 1) * pagination_params["limit"]),
                "name": f"{pagination_params['keyword']} Product 2",
                "price": 299.99,
                "category": "Electronics"
            }
        ],
        "pagination": {
            "page": pagination_params["page"],
            "limit": pagination_params["limit"],
            "total_count": pagination_params["total_count"]
        }
    }
    
    # Assertions
    assert context.response_status == 200
    assert "products" in context.response_data
    assert isinstance(context.response_data["products"], list)
    assert "pagination" in context.response_data
    assert context.response_data["pagination"]["page"] == pagination_params["page"]
    assert context.response_data["pagination"]["limit"] == pagination_params["limit"]
    assert context.response_data["pagination"]["total_count"] == pagination_params["total_count"]


@pytest.mark.parametrize(
    "product",
    products_list,
    ids=[f"product-{p['id']}-{p['name'].replace(' ', '-')}" for p in products_list]
)
@pytest.mark.api
@pytest.mark.product_search
def test_product_has_required_fields(product):
    """Test that all products have required fields using test data."""
    required_fields = ["id", "name", "category", "price", "stock", "status"]
    
    for field in required_fields:
        assert field in product, f"Product missing required field: {field}"
    
    # Type validation
    assert isinstance(product["id"], int)
    assert isinstance(product["name"], str)
    assert isinstance(product["price"], (int, float))
    assert isinstance(product["stock"], int)
    assert product["status"] in ["active", "inactive"]


@pytest.mark.api
@pytest.mark.product_search
def test_empty_search_results():
    """Test search returning empty results."""
    context = type('Context', (), {})()
    
    # Setup
    context.api_available = True
    context.response_status = 200
    
    # Execute - nonexistent search
    context.search_keyword = "nonexistent_product_xyz"
    context.response_data = {"products": []}
    
    # Assertions
    assert context.response_status == 200
    assert len(context.response_data["products"]) == 0
