# Code Quality Standards

## Style
- Follow PEP 8 conventions
- Use meaningful variable names
- Keep functions reasonably short
- Before finalizing, verify that every assigned variable and every import is actually referenced; remove any that are not

## Type Hints
- Add type hints to function signatures
- Use standard library types where possible
- Prefer specific generic forms over bare container types: use `tuple[type[Exception], ...]` rather than bare `tuple`, and annotate `Callable` with parameter and return types (`Callable[..., T]` or a concrete signature) when the signature is known

## Documentation
- Include a docstring on the main function
- Describe parameters and return values
- Include an `Examples:` section showing at least one typical call and its expected return value
- Private helper functions should include at minimum a one-line summary docstring; for helpers with multiple parameters or non-obvious behavior, also document parameters and return values concisely

## Structure
- One function per file unless helpers are needed
- Imports at the top of the file
- Constants in UPPER_CASE
