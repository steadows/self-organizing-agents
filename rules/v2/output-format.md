# Output Format Requirements

## File Structure
Each task output directory should contain:
- `{function_name}.py` — the implementation
- `test_{function_name}.py` — the tests

## Implementation File
- Module-level docstring describing the utility
- The main function with type hints and docstring
- Any helper functions needed

## Test File
- Import the function from the implementation file
- Use pytest style (plain functions, not classes)
- Test function names should describe what they test

## General
- No external dependencies unless the task spec requires them
- Use only standard library imports
- Files should be self-contained and runnable
