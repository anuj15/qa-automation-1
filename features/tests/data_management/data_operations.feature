@database
@data_management
Feature: Data Management Database Operations
  As a system administrator
  I want to manage data records
  So that the database stays organized

  @bvt
  @create_record
  Scenario: Create a new data record in database
    Given the database is accessible
    When I create a new data record with name "Sample Data 1" and description "Test record"
    Then the record should be created successfully
    And the record should be stored in the database
    And the record status should be "active"

  @bvt
  @read_record
  Scenario: Retrieve data record from database
    Given the database is accessible
    And a data record with id "1" exists in the database
    When I query for the data record with id "1"
    Then I should get the record with name "Sample Data 1"
    And the record should have all required fields

  @bvt
  @update_record
  Scenario: Update existing data record
    Given the database is accessible
    And a data record with id "1" exists
    When I update the record with name "Updated Sample Data 1"
    Then the update should be successful
    And the database should reflect the new name
    And the updated_at timestamp should change

  @delete_record
  Scenario: Delete data record from database
    Given the database is accessible
    And a data record with id "99" exists
    When I delete the record with id "99"
    Then the deletion should be successful
    And the record should no longer be accessible
    And the deletion should be logged

  @bvt
  @count_records
  Scenario: Count total records in database
    Given the database is accessible
    When I count all data records with status "active"
    Then the count should be greater than 0
    And the count should match the actual number of records
