@api
@product_search
Feature: Product Search API
  As a user
  I want to search for products
  So that I can find what I'm looking for

  @bvt
  @search_by_keyword
  Scenario: User can search products by keyword
    Given the product search API is available
    When I search for products with keyword "laptop"
    Then I should receive a 200 status code
    And the response should contain a list of products
    And each product should have "id", "name", "price" fields

  @bvt
  @search_by_category
  Scenario: User can filter products by category
    Given the product search API is available
    When I search for products in category "Electronics"
    Then I should receive a 200 status code
    And all returned products should be in category "Electronics"

  @search_empty_results
  Scenario: API returns empty results for no matches
    Given the product search API is available
    When I search for products with keyword "nonexistent_product_xyz"
    Then I should receive a 200 status code
    And the response should contain an empty list of products

  @bvt
  @search_with_pagination
  Scenario: User can paginate search results
    Given the product search API is available
    When I search for products with keyword "phone" and page 1
    Then I should receive a 200 status code
    And the response should include pagination metadata
    And pagination should have "page", "limit", "total_count" fields
