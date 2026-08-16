# /plan — Implementation Planning

## Purpose
Design the implementation strategy for a new feature or fix before coding.

## Steps

1. **Understand the requirement**
   - Read the issue or user request carefully
   - Identify success criteria from SPEC.md
   - Check for related existing code

2. **Analyze affected components**
   - List files that need changes
   - Identify dependencies and impact zones
   - Note any backwards-compatibility concerns

3. **Design the solution**
   - Propose the overall approach
   - Consider edge cases and error handling
   - Estimate effort and complexity

4. **Present the plan**
   - Step-by-step implementation plan
   - Critical decision points
   - Potential risks and mitigations

## Output
A numbered step-by-step plan with file paths, decision points, and estimated effort.

## Example
```
## Plan: Add Daily Midnight Reports

1. **Create thread registry file** (`thread_registry.json`)
   - Stores thread metadata with timestamps
   - File: `projects/fxp_bot/bot.py` → new `load_registry()` function

2. **Update main loop** 
   - Add midnight check (hour == 0)
   - Generate yesterday's report
   - File: `projects/fxp_bot/bot.py` → main `run()` loop

3. **Create report generator**
   - Group threads by forum
   - Format human-readable output
   - File: `projects/fxp_bot/bot.py` → new `get_daily_report()` function
```
