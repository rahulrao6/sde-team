# GridShift

A deterministic, grid-based puzzle game inspired by Sokoban. Push boxes onto goal positions using strategic planning and spatial reasoning.

## Features

- **Deterministic Gameplay**: Same moves always produce the same result
- **Undo System**: Unlimited undo to try different strategies
- **Replay System**: Record and replay move sequences
- **Multiple Levels**: 5 progressively challenging puzzles
- **Visual Themes**: Choose from 4 distinct visual styles (default, neon, retro, emoji)
- **Polished Terminal UI**: Color-coded elements, bordered game grid, centered layout
- **Visual Feedback**: Color-coded game elements and status messages
- **Debug Mode**: Optional debug logging for development

## Installation

No external dependencies required - uses only Python standard library:

```bash
# No installation needed! Just run:
python -m gridshift.main
```

## How to Play

### Objective
Push all boxes ($) onto goal positions (.) to complete the level.

### Controls

- **Movement**: `WASD` or Arrow keys
- **Reset**: `R` - Restart the current level
- **Undo**: `Z` - Undo the last move
- **Replay**: `P` - Replay all recorded moves from the beginning
- **Quit**: `Q` - Exit the game

### Game Symbols

**Default Theme:**
| Symbol | Meaning |
|--------|---------|
| `@` | Player |
| `#` | Wall |
| `$` | Box |
| `.` | Goal (empty) |
| `*` | Box on goal |
| `+` | Player on goal |
| ` ` | Empty space |

**Theme Variations:**
- **Neon**: Uses `█` for walls, `[█]` for boxes, `◆` for goals, with double-line borders (`╔═╗`)
- **Retro**: Uses `▓` for walls, `□` for boxes, `·` for goals, all in green-on-black
- **Emoji**: Uses 🧱 for walls, 📦 for boxes, ⭐ for goals, 🏃 for player (2-char wide cells)

### Rules

1. Move in 4 directions (up, down, left, right)
2. Push boxes by walking into them
3. Can only push one box at a time
4. Cannot push boxes through walls or other boxes
5. All boxes must reach goals to win

## Running the Game

### Play with Level Selection Menu
```bash
python -m gridshift.main
```

### Play a Specific Level
```bash
python -m gridshift.main --level levels/level01.txt
```

### Enable Debug Mode
```bash
python -m gridshift.main --debug
```

### Choose a Visual Theme
```bash
# Default theme (classic ASCII)
python -m gridshift.main --theme default

# Neon theme (cyberpunk with magenta walls, cyan boxes, yellow goals, green player)
python -m gridshift.main --theme neon

# Retro theme (green-on-black Matrix style)
python -m gridshift.main --theme retro

# Emoji theme (fun emoji characters with 2-char wide cells)
python -m gridshift.main --theme emoji
```

### Help
```bash
python -m gridshift.main --help
```

## Running Tests

All game logic is thoroughly tested:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_engine.py -v

# Run with coverage
python -m pytest tests/ --cov=gridshift
```

Current test coverage: **99 tests**, all passing ✓

## Project Structure

```
gridshift/
├── gridshift/
│   ├── __init__.py
│   ├── models.py        # Core data types (Tile, Direction, Position, GameState)
│   ├── level_loader.py  # Level file parsing and validation
│   ├── engine.py        # Movement logic, collision, box pushing
│   ├── undo.py          # Unlimited undo via state snapshots
│   ├── replay.py        # Move recording and deterministic replay
│   ├── themes.py        # Visual theme definitions (default, neon, retro, emoji)
│   ├── renderer.py      # Curses-based terminal rendering
│   ├── debug.py         # Debug logging utilities
│   └── main.py          # Game loop and entry point
├── levels/              # 5 puzzle levels (level01.txt - level05.txt)
├── tests/               # Comprehensive test suite
└── requirements.txt     # Empty (stdlib only)
```

## Development

### Tech Stack
- **Language**: Python 3.12+
- **UI**: `curses` (terminal rendering)
- **Testing**: `pytest`
- **Dependencies**: None (stdlib only)

### Key Design Principles

1. **Immutability**: Game states are never mutated; all moves return new states
2. **Determinism**: Replay always produces identical results
3. **Separation of Concerns**: Models, engine, rendering, and I/O are decoupled
4. **Testability**: All game logic has comprehensive unit tests

### Adding New Levels

Create a `.txt` file in the `levels/` directory following this format:

```
########
#   .  #
#   $  #
#   @  #
########
```

**Requirements**:
- Exactly 1 player (`@`)
- At least 1 box (`$`)
- At least 1 goal (`.`)
- Enclosed by walls (`#`)
- Only valid characters: `#`, `@`, `$`, `.`, ` ` (space)

## License

MIT

## Credits

Built with Python standard library. Inspired by classic Sokoban puzzles.
