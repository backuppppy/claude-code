# /implement — Implement Spec Requirements

## Usage
```
/implement <section from SPEC.md>
```

## Purpose
Converts requirements from SPEC.md into working code.

## Example
```
/implement "Phase 3: Deployment & CI/CD"
```

## What it does
1. Reads SPEC.md to find the section
2. Generates implementation plan (like `/plan`)
3. Writes code, tests, docs
4. Updates CLAUDE.md context
5. Creates PR with automated commit

## Output
- ✅ Code changes
- ✅ Updated tests
- ✅ Updated documentation
- ✅ PR ready for review

## Workflow
1. Update SPEC.md with requirement
2. Run `/implement "Your requirement"`
3. Review the generated code
4. `/test` to validate
5. Merge PR

---

**Note:** Always write tests alongside implementation.

**Related:** `/plan`, `/test`, `/deploy`
