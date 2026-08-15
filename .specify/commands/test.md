# /test — Run Tests & Validation

## Usage
```
/test [scope]
```

## Purpose
Runs all tests and validates implementation against SPEC.md.

## Examples
```
/test                    # All tests
/test bot.py            # Test specific file
/test integration       # Only integration tests
/test security          # Security checks (bandit, secrets scan)
```

## What it does
1. Runs pytest (unit + integration)
2. Checks code style (black, flake8)
3. Validates imports (isort)
4. Scans for secrets (hardcoded tokens)
5. Security linting (bandit)
6. Type checking (mypy)
7. Validates SPEC.md compliance

## Output
```
✅ Unit tests: 24/24 passed
✅ Code style: 0 issues
✅ Imports: OK
✅ Security: 0 secrets found
✅ Type check: OK
✅ Spec compliance: OK

Ready to deploy!
```

## Before Merge
Always run `/test` before creating/merging PRs.

---

**Related:** `/implement`, `/deploy`
