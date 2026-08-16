# /specify — Specification Writing

## Purpose
Document requirements, acceptance criteria, and technical specifications before implementation.

## Steps

1. **Define the requirement**
   - What problem does this solve?
   - Who is the user/stakeholder?
   - What is the success metric?

2. **Write acceptance criteria**
   - Given → When → Then format (BDD style)
   - Clear, testable conditions
   - Edge cases included

3. **Technical specification**
   - Input/output contracts
   - Data structures
   - Error handling scenarios
   - Performance requirements (if any)

4. **Dependencies and risks**
   - External services or APIs
   - Breaking changes
   - Backwards compatibility

5. **Update SPEC.md**
   - Add to appropriate section
   - Link to related features
   - Document constraints

## Output
A detailed specification document with requirements, acceptance criteria, technical details, and constraints.

## Example
```markdown
## Feature: Daily Thread Reports

### Requirement
The bot should send automated reports showing thread counts by forum at startup and every midnight.

### Acceptance Criteria
- **Startup:** Bot sends today's thread count by forum
- **Midnight:** Bot sends yesterday's thread count by forum
- **Format:** Report shows forum name + thread count + total
- **Timezone:** Uses local system time for date boundaries

### Technical Spec
- New file: `thread_registry.json` stores thread metadata with ISO timestamps
- New functions: `get_daily_report()`, `load_registry()`, `save_registry()`
- Midnight check: Compare `datetime.now().hour == 0` in main loop
- Registry trimmed to 5,000 entries to avoid unbounded growth

### Edge Cases
- Timezone transitions (DST)
- No threads on a given day
- Bot restarts near midnight
```
