# Task Executor Rules

You are implementing a Python utility function based on a task specification.

## Process
1. Read the task specification carefully
2. Implement the function in a single Python file
3. Write tests alongside the implementation
4. Ensure the function works for the examples given in the spec

## Implementation Guidelines
- Use Python 3.11+ features where appropriate
- Include type hints on the function signature
- Write a docstring for the main function
- Handle basic error cases
- For parameters where the task spec explicitly or implicitly constrains valid values (e.g., a count or length that must be non-negative), add a guard at function entry raising `ValueError` with a descriptive message; do not add validation for parameters the spec leaves unconstrained

## Testing
- Write tests using pytest
- Cover the happy path
- Include at least one edge case test
- For functions with I/O or external dependencies (file system, network, time), include at least one test that simulates a failure or error path using mocks (e.g., mock an `OSError` or a raised exception from a dependency); do not limit tests to value-space edge cases alone

## Output
- Place your implementation in the designated output directory
- Name the main file after the function (e.g., `slugify.py`)
- Name the test file with a `test_` prefix (e.g., `test_slugify.py`)
