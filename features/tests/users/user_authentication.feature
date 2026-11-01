@ui
@user_authentication
Feature: User Authentication
  As a user
  I want to login to the application
  So that I can access my account

  Background:
    Given the application is loaded
    And I am on the login page

  @bvt
  @login_success
  Scenario: User logs in successfully with valid credentials
    When I enter username "john_doe"
    And I enter password "SecurePass123!"
    And I click the login button
    Then I should see the dashboard
    And I should see "Welcome, John Doe"

  @bvt
  @login_failure
  Scenario: User cannot login with invalid password
    When I enter username "john_doe"
    And I enter password "WrongPassword"
    And I click the login button
    Then I should see an error message "Invalid username or password"
    And I should remain on the login page

  @login_required
  Scenario: User is redirected to login when accessing protected page
    Given I am not logged in
    When I navigate to "/dashboard"
    Then I should be redirected to the login page

  @bvt
  @logout
  Scenario: User can logout successfully
    Given I am logged in as "john_doe"
    When I click the logout button
    Then I should be redirected to the login page
    And the session should be cleared
