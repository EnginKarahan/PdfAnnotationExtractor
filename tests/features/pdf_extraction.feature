Feature: PDF Annotation Extraction

  Scenario: User extracts annotations from valid PDF
    Given a PDF file with annotations exists
    When the user selects the file and clicks Extract
    Then a markdown file should be created with all annotations

  Scenario: User tries to extract from non-existent file
    Given no PDF file is selected
    When the user clicks Extract
    Then an error message should be displayed

  Scenario: User changes page offset manually
    Given a PDF file is selected
    When the user sets page offset to 5
    And clicks Extract
    Then the output should reflect the custom page offset
