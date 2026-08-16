# /implement — Code Implementation

## Purpose
Execute the implementation plan, write code, and commit changes to git.

## Steps

1. **Review the plan**
   - Confirm plan is approved
   - Check for any blockers or unknowns

2. **Implement each step**
   - Follow the planned order
   - Write clean, documented code
   - Use project conventions (see CLAUDE.md)

3. **Code style**
   - Run `black` formatter: `black bot.py fxp_monitor.py`
   - Run `flake8` linter: `flake8 bot.py fxp_monitor.py`
   - Fix `isort` imports: `isort bot.py fxp_monitor.py`

4. **Testing during development**
   - Manual testing in `/tmp` if needed
   - Check for regressions in existing features
   - Verify edge cases from specification

5. **Commit changes**
   - Create focused commits with clear messages
   - One commit per logical change
   - Reference issue/spec in commit message

## Output
- Implemented code following the plan
- All tests passing
- Code style validated (black, flake8, isort)
- Commits ready for review

## Code Style Guidelines

### Python
- **Formatter:** Black (88-char line width)
- **Linter:** Flake8 (E501 ignored for Black compatibility)
- **Import sorting:** isort
- **Type hints:** Optional but recommended for public functions
- **Comments:** Only for non-obvious logic (the "why", not the "what")

### File organization
```python
"""Module docstring describing purpose."""

import stdlib
import third_party
from local import imports

CONSTANTS = "values"

def public_function():
    """Short description of public function."""
    pass

def _private_function():
    """Private functions prefixed with underscore."""
    pass

if __name__ == "__main__":
    main()
```

### Naming conventions
- `CamelCase` for classes
- `snake_case` for functions and variables
- `UPPER_CASE` for constants
- Avoid single-letter names except in comprehensions

## Example Output
```
✓ Implemented thread registry with timestamp tracking
✓ Added daily report generation (startup + midnight)
✓ Code formatted with black and flake8
✓ Tests passing: 5/5
✓ Commits: 2 new commits

commit a1b2c3d
  Add thread registry with timestamp persistence
  - New file: thread_registry.json
  - Functions: load_registry(), save_registry()

commit e4f5g6h
  Add daily report generation
  - Midnight report at 00:00
  - Startup report on bot start
```
