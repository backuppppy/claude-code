# /specify — Create or Update SPEC.md

## Usage
```
/specify <requirement or change>
```

## Purpose
Writes or updates SPEC.md with clear, measurable requirements.

## Example
```
/specify "Add support for filtering by forum category"
```

## What it does
1. Parses the requirement
2. Breaks it into functional & non-functional parts
3. Adds it to SPEC.md under the appropriate section
4. Links to related requirements
5. Proposes test criteria

## Output
Updated SPEC.md with:
- Clear purpose statement
- Success criteria (testable)
- In/out of scope
- Risk assessment
- Effort estimate

---

**Important:** Keep SPEC.md as the source of truth for requirements.

**Related:** `/plan`, `/implement`
