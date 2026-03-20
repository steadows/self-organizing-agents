# LLM-as-Judge Scoring Rubric

Score each dimension on a 1-10 scale. Provide a brief justification for each score.

## Dimensions

### 1. Correctness (cross-checked against acceptance tests)
Does the implementation handle all specified requirements?

- **9-10:** All requirements met, all examples produce correct output
- **7-8:** Most requirements met, minor gaps in spec coverage
- **5-6:** Core functionality works but missing significant requirements
- **3-4:** Partial implementation, major requirements missing
- **1-2:** Fundamentally broken or incomplete

**Constraint:** If acceptance tests FAIL, this score MUST be <= 5.

### 2. Edge Cases (cross-checked against acceptance tests)
Does the implementation handle boundary conditions, empty inputs, and error states?

- **9-10:** All edge cases from the spec handled correctly with appropriate responses
- **7-8:** Most edge cases handled, minor gaps
- **5-6:** Happy path works but several edge cases missed
- **3-4:** Minimal edge case handling
- **1-2:** No edge case handling

**Constraint:** If acceptance tests for edge cases FAIL, this score MUST be <= 5.

### 3. Code Quality
Type hints, naming, structure, immutability, readability.

- **9-10:** Excellent naming, clean structure, full type hints, idiomatic Python
- **7-8:** Good quality, minor style issues
- **5-6:** Functional but messy, inconsistent style, missing type hints
- **3-4:** Hard to read, poor naming, no structure
- **1-2:** Unreadable or severely malformed

### 4. Documentation
Docstrings, usage examples, inline comments where needed.

- **9-10:** Comprehensive docstrings with parameters, return values, examples, and edge case notes
- **7-8:** Good docstrings, minor gaps in parameter descriptions
- **5-6:** Basic docstrings present but lacking detail
- **3-4:** Minimal or missing docstrings
- **1-2:** No documentation

### 5. Test Coverage
Quality of the agent's own tests (separate from acceptance tests). Happy path + edge cases.

- **9-10:** Thorough tests covering happy path, edge cases, error paths, boundary conditions
- **7-8:** Good test coverage with some gaps
- **5-6:** Basic tests for happy path only
- **3-4:** Minimal tests or tests that don't assert meaningful behavior
- **1-2:** No tests or non-functional tests

### 6. Robustness
Error handling, input validation, graceful degradation.

- **9-10:** Validates all inputs, raises clear errors, handles all failure modes gracefully
- **7-8:** Good error handling with minor gaps
- **5-6:** Some error handling but missing validation on key inputs
- **3-4:** Minimal error handling, crashes on bad input
- **1-2:** No error handling

## Output Format

Return scores as JSON:

```json
{
  "task_id": "task-001",
  "scores": {
    "correctness": {"score": 8, "justification": "..."},
    "edge_cases": {"score": 7, "justification": "..."},
    "code_quality": {"score": 9, "justification": "..."},
    "documentation": {"score": 6, "justification": "..."},
    "test_coverage": {"score": 7, "justification": "..."},
    "robustness": {"score": 8, "justification": "..."}
  },
  "overall": 7.5,
  "acceptance_test_pass": true,
  "acceptance_test_details": "15/16 passed, 1 edge case failed"
}
```

## Scoring Rules

1. Score each dimension independently
2. `overall` is the arithmetic mean of all 6 dimension scores, rounded to 1 decimal
3. If acceptance tests fail, correctness and edge_cases scores are capped at 5
4. Provide specific examples from the code to justify each score
5. Do not inflate scores — a 10 means genuinely exceptional work
