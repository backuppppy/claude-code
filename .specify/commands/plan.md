# /plan — FXP Bot Implementation Plan

## Usage
```
/plan <requirement>
```

## Purpose
Creates a step-by-step implementation plan from a requirement in SPEC.md.

## Example
```
/plan "Add Prometheus metrics support to FXP Bot"
```

## What it does
1. Reads SPEC.md to understand project scope
2. Identifies related requirements
3. Creates a breakdown with:
   - Critical path (must-do first)
   - Dependencies
   - Estimated effort
   - Test strategy
   - Rollback plan

## Output
A markdown document with:
- [x] What to change
- [x] File locations
- [x] Step-by-step implementation
- [x] Testing approach
- [x] Risk assessment

---

**Related:** `/specify`, `/implement`
