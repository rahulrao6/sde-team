# 🎮 PLAY GRIDSHIFT NOW!

## Quick Start

```bash
# From the project directory, run:
python play.py
```

Or:

```bash
python -m gridshift.main
```

## Controls

- **Move**: `W` `A` `S` `D` or Arrow Keys ↑ ← ↓ →
- **Undo**: `Z`
- **Reset Level**: `R`
- **Quit**: `Q`

## Goal

Push all boxes (`$`) onto goal positions (`.`) to win!

## Game Symbols

- `@` = You (the player)
- `$` = Box
- `.` = Goal (empty)
- `*` = Box on goal ✓
- `+` = You standing on goal
- `#` = Wall
- ` ` = Empty space

## Tips

1. Plan your moves - boxes can get stuck in corners!
2. Use `Z` to undo mistakes
3. Use `R` to restart if you get stuck
4. All 5 levels are solvable

## Play Specific Level

```bash
python -m gridshift.main --level levels/level01.txt
python -m gridshift.main --level levels/level02.txt
python -m gridshift.main --level levels/level03.txt
python -m gridshift.main --level levels/level04.txt
python -m gridshift.main --level levels/level05.txt
```

## Debug Mode (for developers)

```bash
python -m gridshift.main --debug
```

---

**Have fun! 🎉**
