Feature: Show version

  Scenario: when using --version
    When I run tsktsk --version
    Then its exit code should be 0
     And its output should match ^\d+\.\d+(\.(dev)?\d+)?$
