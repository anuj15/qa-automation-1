@api
@payment_processing
Feature: Payment Processing API
  As a user
  I want to process payments
  So that I can complete my purchase

  @bvt
  @process_payment_success
  Scenario: Process payment successfully with valid card
    Given the payment API is available
    When I submit a payment with amount 99.99 and valid card details
    Then I should receive a 200 status code
    And the response should include a transaction_id
    And the payment status should be "completed"
    And the order should be created in the database

  @bvt
  @process_payment_failure
  Scenario: Payment fails with invalid card
    Given the payment API is available
    When I submit a payment with amount 50.00 and invalid card details
    Then I should receive a 400 status code
    And the response should include error message "Invalid card number"
    And no transaction should be created

  @payment_insufficient_funds
  Scenario: Payment fails due to insufficient funds
    Given the payment API is available
    When I submit a payment with amount 10000.00 and valid card
    Then I should receive a 402 status code
    And the response should include error message "Insufficient funds"
    And the payment status should be "failed"

  @bvt
  @retrieve_payment_status
  Scenario: Retrieve payment status
    Given the payment API is available
    And a payment with transaction_id "TXN-12345" exists
    When I query the payment status for transaction_id "TXN-12345"
    Then I should receive a 200 status code
    And the payment status should be "completed"
    And the response should include payment details
