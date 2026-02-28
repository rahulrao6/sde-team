# GridShift — Ticket Breakdown

Tech stack: **Python 3** with `curses` for terminal rendering. All game logic in pure Python, no external dependencies except stdlib.

## Project Structure

```
gridshift/
├── gridshift/
│   ├── __init__.py
│   ├── models.py        # Tile, Direction, Position, GameState
│   ├── level_loader.py  # Parse .txt level files, validate
│   ├── engine.py        # Movement, collision, box pushing
│   ├── undo.py          # Undo stack (state snapshots)
│   ├── replay.py        # Move logging, deterministic replay
│   ├── renderer.py      # curses-based terminal rendering
│   ├── debug.py         # Debug logging, state inspection
│   └── main.py          # Game loop, input handling, controls
├── levels/
│   ├── level01.txt
│   ├── level02.txt
│   ├── level03.txt
│   ├── level04.txt
│   └── level05.txt
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_level_loader.py
│   ├── test_engine.py
│   ├── test_undo.py
│   ├── test_replay.py
│   └── test_win.py
├── requirements.txt
└── README.md
```

---

## Ticket 1: Project Scaffolding & Core Data Models

**Priority:** P0 (blocking all other tickets)

Create the Python project structure and define all core data types.

### Deliverables
- `gridshift/__init__.py`
- `gridshift/models.py` with:
  - `Tile` enum: WALL('#'), PLAYER('@'), BOX('$'), GOAL('.'), EMPTY(' ')
  - `Direction` enum: UP, DOWN, LEFT, RIGHT
  - `Position` dataclass: row, col
  - `GameState` dataclass: grid (2D list of Tiles), player_pos (Position), box_positions (set of Position), goal_positions (set of Position), width, height
  - `GameState.clone()` method for deep copy
- `requirements.txt` (empty or stdlib-only)
- `tests/__init__.py`
- `tests/test_models.py` — unit tests for Tile parsing, Position equality, GameState clone independence

### Acceptance
- All model types importable
- GameState.clone() produces independent copy (mutating clone doesn't affect original)
- Tests pass

---

## Ticket 2: Level Loader & Validator

**Priority:** P0 (blocking engine, rendering)

Parse plain-text level files into GameState objects with full validation.

### Deliverables
- `gridshift/level_loader.py` with:
  - `load_level(filepath: str) -> GameState` — reads .txt file, parses grid
  - `parse_level(text: str) -> GameState` — parses level from string (for testing)
  - Validation: exactly 1 player, ≥1 box, ≥1 goal, only valid characters (#@$. and space)
  - Raises `ValueError` with descriptive message on invalid levels
  - Handles ragged lines (pads shorter rows with spaces)
- `tests/test_level_loader.py` with tests for:
  - Valid level parsing
  - Missing player → error
  - Multiple players → error
  - No boxes → error
  - No goals → error
  - Invalid characters → error
  - Ragged line handling

### Acceptance
- Can load a .txt file and produce a valid GameState
- All validation constraints enforced with clear error messages
- Tests pass

---

## Ticket 3: Movement & Collision Engine

**Priority:** P0 (core gameplay)

Implement all movement rules: player movement, wall collision, box pushing.

### Deliverables
- `gridshift/engine.py` with:
  - `move(state: GameState, direction: Direction) -> tuple[GameState, bool]`
    - Returns (new_state, moved) where moved=True if the move was valid
    - Empty cell → player moves
    - Wall → blocked (return original state, False)
    - Box with empty beyond → push box, move player (return new state, True)
    - Box with wall/box beyond → blocked (return original state, False)
  - Player on goal tile: player can walk on/off goals freely
  - Box on goal tile: box can be pushed onto goals
  - State is NEVER mutated; always return new state
- `tests/test_engine.py` with tests for:
  - Move into empty cell (all 4 directions)
  - Move into wall (all 4 directions)
  - Push box into empty cell
  - Push box into wall (blocked)
  - Push box into another box (blocked)
  - Push box onto goal
  - Player walks on/off goal
  - Edge of grid (treat as wall)

### Acceptance
- All movement rules from requirements §2.3 implemented
- State immutability: original state unchanged after move()
- Tests pass

---

## Ticket 4: Win Detection

**Priority:** P1 (requires engine)

Detect when all boxes are on goal tiles.

### Deliverables
- Add to `gridshift/engine.py`:
  - `check_win(state: GameState) -> bool` — returns True when every goal has a box on it
- `tests/test_win.py` with tests for:
  - All boxes on goals → win
  - Some boxes on goals → not win
  - No boxes on goals → not win
  - Box on goal but extra goals empty → not win (number of boxes < goals edge case)
  - Level with 1 box, 1 goal, box on goal → win

### Acceptance
- Win detected correctly for all configurations
- Tests pass

---

## Ticket 5: Undo System

**Priority:** P1 (requires engine)

Implement unlimited undo via state snapshot stack.

### Deliverables
- `gridshift/undo.py` with:
  - `UndoManager` class:
    - `push(state: GameState)` — save state snapshot before each move
    - `pop() -> GameState | None` — restore previous state, None if empty
    - `clear()` — reset undo history
    - `depth` property — number of states in stack
  - Uses GameState.clone() for independent snapshots
- `tests/test_undo.py` with tests for:
  - Push and pop restores exact state
  - Multiple undo steps restore correct sequence
  - Pop on empty stack returns None
  - Clear resets depth to 0
  - Undo after box push restores box to original position
  - State independence (modifying returned state doesn't affect stack)

### Acceptance
- Unlimited undo depth
- Exact state restoration verified
- Tests pass

---

## Ticket 6: Replay System

**Priority:** P1 (requires engine)

Log all moves and replay them deterministically.

### Deliverables
- `gridshift/replay.py` with:
  - `ReplayRecorder` class:
    - `record(direction: Direction)` — append move to log
    - `get_log() -> list[Direction]` — return move sequence
    - `clear()` — reset log
    - `save(filepath: str)` — write log to file (one direction per line)
    - `load(filepath: str) -> list[Direction]` — read log from file
  - `replay(initial_state: GameState, moves: list[Direction]) -> list[GameState]`
    - Apply each move sequentially, return list of all states
    - Must produce identical results given same inputs (determinism)
- `tests/test_replay.py` with tests for:
  - Record and replay produces same final state as manual play
  - Replay with invalid moves (blocked moves) still produces correct state
  - Save and load round-trip
  - Determinism: two replays of same inputs produce identical state sequences
  - Empty replay returns initial state only

### Acceptance
- Deterministic replay verified
- Save/load works
- Tests pass

---

## Ticket 7: Terminal Rendering & Game Loop

**Priority:** P1 (requires all above)

Build the curses-based terminal UI, game loop, and input handling.

### Deliverables
- `gridshift/renderer.py` with:
  - `Renderer` class (curses-based):
    - `render(state: GameState, move_count: int, message: str)` — draw grid + HUD
    - Display: walls as `#`, player as `@`, boxes as `$`, goals as `.`, box-on-goal as `*`, player-on-goal as `+`, empty as space
    - HUD shows: level name, move count, undo depth, status messages
    - Controls help bar at bottom
- `gridshift/main.py` with:
  - Main game loop:
    - Initialize curses
    - Load level from command line arg or default
    - Handle input: W/↑=up, S/↓=down, A/←=left, D/→=right, R=reset, Z=undo, P=replay, Q=quit
    - Integrate engine, undo manager, replay recorder
    - Show win message when level complete
    - Support --debug flag for debug logging
    - Support --level flag to select level file
    - Level selection menu if multiple levels in levels/ directory
  - 60fps cap via frame timing
  - `if __name__ == "__main__"` entry point
- `gridshift/debug.py` with:
  - `DebugLogger` class:
    - Toggle on/off
    - Log grid state, move history, replay log to stderr or file
    - `dump_state(state: GameState)` — print grid as text
    - `dump_history(moves: list[Direction])` — print move sequence

### Acceptance
- Game playable in terminal
- All controls working
- 60fps rendering
- Win detection displays message
- Debug mode toggleable via --debug flag

---

## Ticket 8: Test Levels

**Priority:** P1 (can be parallelized)

Create 5 test levels of increasing difficulty.

### Deliverables
- `levels/level01.txt` — Tutorial: 1 box, 1 goal, simple push (3-4 moves to solve)
- `levels/level02.txt` — Easy: 1 box, 1 goal, requires navigation around walls
- `levels/level03.txt` — Medium: 2 boxes, 2 goals, basic planning required
- `levels/level04.txt` — Hard: 3 boxes, 3 goals, tight corridors
- `levels/level05.txt` — Expert: 3+ boxes, dead-end traps, requires careful sequencing

### Constraints per level
- Exactly 1 player (@)
- Number of boxes ($) == number of goals (.)
- All levels must be solvable
- All levels enclosed by walls (#)
- Each level must be a valid Sokoban puzzle

### Acceptance
- All 5 levels load without validation errors
- All 5 levels are solvable (provide solution move sequences in comments at top of file)
- Levels increase in difficulty

---

## Dependency Graph

```
Ticket 1 (Models) ──────┬──→ Ticket 2 (Level Loader)
                         ├──→ Ticket 3 (Engine) ──→ Ticket 4 (Win Detection)
                         ├──→ Ticket 5 (Undo)
                         └──→ Ticket 6 (Replay)

Tickets 2-6 ───────────────→ Ticket 7 (Rendering & Game Loop)

Ticket 2 ──────────────────→ Ticket 8 (Test Levels)
```

Tickets 3, 4, 5, 6, and 8 can all be worked on in parallel once Ticket 1 is merged.
Ticket 7 integrates everything at the end.
