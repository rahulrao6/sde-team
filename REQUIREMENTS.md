# Requirements Document

**Project:** GridShift — Deterministic Grid Puzzle Game

---

# 1. Objective

Build a **fully playable, deterministic, grid-based puzzle game** that runs locally.

The game must support:

* Player movement
* Box pushing
* Collision rules
* Multiple levels
* Undo
* Replay
* Win detection

---

# 2. Functional Requirements

---

## 2.1 Game World

* The world is a **2D rectangular grid**.
* Grid dimensions are defined per level.
* Each grid cell contains **at most one entity**.

### Tile Types

| Symbol | Meaning |
| ------ | ------- |
| `#`    | Wall    |
| `@`    | Player  |
| `$`    | Box     |
| `.`    | Goal    |
| ` `    | Empty   |

---

## 2.2 Level Input Format

Levels are loaded from **plain text files**.

Example:

```
########
#   .  #
#   $  #
#   @  #
########
```

### Constraints

* Exactly **1 player** per level.
* At least **1 box**.
* At least **1 goal**.
* All characters outside the allowed set must be rejected.

---

## 2.3 Movement Rules

Player can move:

* Up
* Down
* Left
* Right

Movement behavior:

* If target cell is empty → player moves.
* If target cell contains a wall → movement blocked.
* If target cell contains a box:

  * If the cell beyond the box is empty → push box and move.
  * If the cell beyond is blocked → movement blocked.

No diagonal movement.

---

## 2.4 Game State Rules

* Player and boxes occupy **distinct grid cells**.
* Walls are static.
* Goals do not block movement.
* Boxes can sit on goals.

---

## 2.5 Win Condition

The level is complete when **all boxes are positioned on goal tiles**.

---

## 2.6 Controls

| Key   | Action         |
| ----- | -------------- |
| W / ↑ | Move Up        |
| S / ↓ | Move Down      |
| A / ← | Move Left      |
| D / → | Move Right     |
| R     | Reset level    |
| Z     | Undo last move |
| P     | Replay run     |

---

## 2.7 Undo System

* Each player action must be recorded.
* Undo restores the **exact previous game state**.
* Unlimited undo depth is required.

---

## 2.8 Replay System

* Every move must be logged.
* A full run can be replayed deterministically from:

  * Level file
  * Input sequence
* Replay must exactly reproduce:

  * Player movement
  * Box movement
  * Final outcome

---

## 2.9 Determinism

Given:

* Level file
* Input sequence

The resulting gameplay **must be identical on every run**.

This includes:

* Final board state
* Move count
* Win / lose outcome

---

# 3. Non-Functional Requirements

---

## 3.1 Performance

* Must maintain **≥60 FPS rendering**.
* All moves must complete within **1ms simulation time**.

---

## 3.2 Reliability

* Invalid levels must fail gracefully.
* Game must not crash due to malformed input.
* All invalid player actions must be safely rejected.

---

## 3.3 Debuggability

* Must expose:

  * Current grid state
  * Move history
  * Replay log
* Debug logging toggle required.

---

# 4. Deliverables

The system must output:

1. Fully working executable game
2. Level loader
3. Replay log system
4. Undo system
5. At least **5 test levels**
6. Automated tests for:

   * Movement
   * Collision
   * Undo correctness
   * Replay determinism
   * Win detection

---

# 5. Acceptance Criteria

The project is considered complete when:

* All test levels are playable.
* Undo restores exact previous states.
* Replay produces identical outcomes.
* No invalid movement is allowed.
* Win condition is correctly detected.

---

# 6. Explicit Non-Goals

The following are *not required*:

* Sound
* Animation
* Multiplayer
* Online features
* Fancy graphics

---

# 7. Complexity Justification

This task is intentionally small but tests:

* Planning
* State modeling
* Edge case handling
* Deterministic simulation
* Multi-module integration
* Debugging
* Testing
