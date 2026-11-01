Feature: Sample Authentication Tests
  Test basic login and authentication flows

  @bvt @ui @authentication
  Scenario: User can login with valid credentials
    Given User is on the login page
    When User enters valid credentials
    And User clicks the login button
    Then User should be logged in successfully
    And User should see the dashboard

  @ui @authentication
  Scenario: User cannot login with invalid credentials
    Given User is on the login page
    When User enters invalid credentials
    And User clicks the login button
    Then User should see an error message
    And User should remain on the login page
