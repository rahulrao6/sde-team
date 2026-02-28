# QA & Testing Policy — GridShift

## Priority: Testing is the HIGHEST priority

No feature is considered done until it has passing tests. If you find a bug, fix it immediately or report it clearly so a follow-up worker can be spawned.

## Test Requirements

Every module MUST have tests covering:
1. **Happy path** — normal expected usage
2. **Edge cases** — boundary conditions, empty inputs, maximums
3. **Error cases** — invalid inputs, graceful failure
4. **Integration** — modules working together end-to-end

## Running Tests

```bash
cd /path/to/repo
python -m pytest tests/ -v          # Run all tests
python -m pytest tests/ -v --tb=short  # Compact output
python -m pytest tests/test_engine.py -v  # Single module
```

## If Tests Fail

1. Identify the root cause
2. Fix the bug in the relevant module
3. Add a regression test for the specific bug
4. Re-run ALL tests to ensure no regressions
5. If the fix is in another worker's code, coordinate via the supervisor

## Key Edge Cases to Always Test

- Empty grid / minimal grid (1x1)
- Player surrounded by walls (no valid moves)
- Box in corner (deadlock)
- Multiple boxes pushing into each other
- Undo at start of game (nothing to undo)
- Replay with zero moves
- Level with boxes already on goals (instant win)
- Very large grids (performance)
- All directions (UP/DOWN/LEFT/RIGHT) for every movement scenario
