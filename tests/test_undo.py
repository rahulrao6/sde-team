"""Tests for the undo system."""

import pytest
from gridshift.models import GameState, Position, Tile
from gridshift.undo import UndoManager


def create_test_state(player_row: int = 1, player_col: int = 1,
                      box_positions: set[Position] | None = None,
                      goal_positions: set[Position] | None = None) -> GameState:
    """Helper to create a minimal test GameState."""
    if box_positions is None:
        box_positions = {Position(2, 2)}
    if goal_positions is None:
        goal_positions = {Position(3, 3)}
    
    # Create a simple 5x5 grid
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.EMPTY, Tile.EMPTY, Tile.EMPTY, Tile.WALL],
        [Tile.WALL, Tile.EMPTY, Tile.EMPTY, Tile.EMPTY, Tile.WALL],
        [Tile.WALL, Tile.EMPTY, Tile.EMPTY, Tile.EMPTY, Tile.WALL],
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
    ]
    
    # Mark player position
    grid[player_row][player_col] = Tile.PLAYER
    
    # Mark box positions
    for pos in box_positions:
        grid[pos.row][pos.col] = Tile.BOX
    
    # Mark goal positions (goals don't override other tiles in the visual grid,
    # but we store them separately in GameState)
    for pos in goal_positions:
        if grid[pos.row][pos.col] == Tile.EMPTY:
            grid[pos.row][pos.col] = Tile.GOAL
    
    return GameState(
        grid=grid,
        player_pos=Position(player_row, player_col),
        box_positions=box_positions,
        goal_positions=goal_positions,
        width=5,
        height=5
    )


def test_undo_push_and_pop_restores_exact_state():
    """Test that push and pop restore the exact state."""
    manager = UndoManager()
    
    # Create initial state
    state1 = create_test_state(player_row=1, player_col=1)
    
    # Push state
    manager.push(state1)
    
    # Pop and verify
    restored = manager.pop()
    assert restored is not None
    assert restored.player_pos == state1.player_pos
    assert restored.box_positions == state1.box_positions
    assert restored.goal_positions == state1.goal_positions
    assert restored.width == state1.width
    assert restored.height == state1.height
    assert restored.grid == state1.grid


def test_multiple_undo_sequence():
    """Test multiple undo steps restore correct sequence."""
    manager = UndoManager()
    
    # Create three different states
    state1 = create_test_state(player_row=1, player_col=1)
    state2 = create_test_state(player_row=1, player_col=2)
    state3 = create_test_state(player_row=1, player_col=3)
    
    # Push all three
    manager.push(state1)
    manager.push(state2)
    manager.push(state3)
    
    # Pop in reverse order
    restored3 = manager.pop()
    assert restored3 is not None
    assert restored3.player_pos == Position(1, 3)
    
    restored2 = manager.pop()
    assert restored2 is not None
    assert restored2.player_pos == Position(1, 2)
    
    restored1 = manager.pop()
    assert restored1 is not None
    assert restored1.player_pos == Position(1, 1)


def test_pop_empty_stack_returns_none():
    """Test that popping an empty stack returns None."""
    manager = UndoManager()
    
    # Pop from empty stack
    result = manager.pop()
    assert result is None
    
    # Multiple pops should still return None
    result = manager.pop()
    assert result is None


def test_clear_resets_depth():
    """Test that clear resets the stack depth to 0."""
    manager = UndoManager()
    
    # Push some states
    state1 = create_test_state(player_row=1, player_col=1)
    state2 = create_test_state(player_row=1, player_col=2)
    manager.push(state1)
    manager.push(state2)
    
    # Verify depth before clear
    assert manager.depth == 2
    
    # Clear and verify
    manager.clear()
    assert manager.depth == 0
    
    # Pop should return None after clear
    assert manager.pop() is None


def test_undo_after_box_push():
    """Test undo after a box push restores box to original position."""
    manager = UndoManager()
    
    # Initial state: box at (2, 2)
    state1 = create_test_state(
        player_row=1,
        player_col=2,
        box_positions={Position(2, 2)},
        goal_positions={Position(3, 3)}
    )
    manager.push(state1)
    
    # After push: box moved to (3, 2)
    state2 = create_test_state(
        player_row=2,
        player_col=2,
        box_positions={Position(3, 2)},
        goal_positions={Position(3, 3)}
    )
    manager.push(state2)
    
    # Undo and verify box is back at original position
    restored = manager.pop()
    assert restored is not None
    assert Position(3, 2) in restored.box_positions
    
    restored = manager.pop()
    assert restored is not None
    assert Position(2, 2) in restored.box_positions
    assert Position(3, 2) not in restored.box_positions


def test_state_independence():
    """Test that modifying returned state doesn't affect the stack."""
    manager = UndoManager()
    
    # Create and push initial state
    state1 = create_test_state(player_row=1, player_col=1)
    manager.push(state1)
    
    # Push another state so we can pop and modify
    state2 = create_test_state(player_row=1, player_col=2)
    manager.push(state2)
    
    # Pop and modify the returned state
    restored = manager.pop()
    assert restored is not None
    
    # Modify the restored state (modify box positions)
    restored.box_positions.add(Position(4, 4))
    
    # Pop again and verify the stack's copy was not affected
    original = manager.pop()
    assert original is not None
    assert Position(4, 4) not in original.box_positions
    assert Position(2, 2) in original.box_positions


def test_depth_property():
    """Test that depth property accurately reports stack size."""
    manager = UndoManager()
    
    # Initial depth
    assert manager.depth == 0
    
    # Add states
    state1 = create_test_state(player_row=1, player_col=1)
    manager.push(state1)
    assert manager.depth == 1
    
    state2 = create_test_state(player_row=1, player_col=2)
    manager.push(state2)
    assert manager.depth == 2
    
    state3 = create_test_state(player_row=1, player_col=3)
    manager.push(state3)
    assert manager.depth == 3
    
    # Pop and check depth decreases
    manager.pop()
    assert manager.depth == 2
    
    manager.pop()
    assert manager.depth == 1
    
    manager.pop()
    assert manager.depth == 0


def test_empty_stack_depth():
    """Test depth on an empty stack."""
    manager = UndoManager()
    assert manager.depth == 0


def test_push_preserves_original_state():
    """Test that push doesn't mutate the original state object."""
    manager = UndoManager()
    
    # Create state
    state1 = create_test_state(player_row=1, player_col=1)
    original_box_pos = state1.box_positions.copy()
    
    # Push state
    manager.push(state1)
    
    # Modify original state
    state1.box_positions.add(Position(4, 4))
    
    # Pop and verify the pushed state wasn't affected
    restored = manager.pop()
    assert restored is not None
    assert restored.box_positions == original_box_pos
    assert Position(4, 4) not in restored.box_positions
