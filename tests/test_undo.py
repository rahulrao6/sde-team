"""Unit tests for undo system."""

import pytest
from gridshift.models import Tile, Position, GameState
from gridshift.undo import UndoManager


class TestUndoManager:
    """Tests for UndoManager class."""
    
    def test_initial_depth_is_zero(self):
        """Test that a new UndoManager has depth 0."""
        manager = UndoManager()
        assert manager.depth == 0
    
    def test_pop_on_empty_stack_returns_none(self):
        """Test that popping an empty stack returns None."""
        manager = UndoManager()
        assert manager.pop() is None
    
    def test_push_increases_depth(self):
        """Test that pushing a state increases depth."""
        manager = UndoManager()
        state = self._create_simple_state()
        
        manager.push(state)
        assert manager.depth == 1
        
        manager.push(state)
        assert manager.depth == 2
    
    def test_pop_decreases_depth(self):
        """Test that popping a state decreases depth."""
        manager = UndoManager()
        state = self._create_simple_state()
        
        manager.push(state)
        manager.push(state)
        assert manager.depth == 2
        
        manager.pop()
        assert manager.depth == 1
        
        manager.pop()
        assert manager.depth == 0
    
    def test_push_and_pop_restores_exact_state(self):
        """Test that push and pop restore the exact state."""
        manager = UndoManager()
        
        # Create a state with specific values
        grid = [[Tile.WALL, Tile.EMPTY], [Tile.PLAYER, Tile.BOX]]
        player_pos = Position(1, 0)
        box_positions = {Position(1, 1)}
        goal_positions = {Position(0, 1)}
        
        state = GameState(
            grid=grid,
            player_pos=player_pos,
            box_positions=box_positions,
            goal_positions=goal_positions,
            width=2,
            height=2
        )
        
        manager.push(state)
        restored = manager.pop()
        
        assert restored is not None
        assert restored.player_pos == player_pos
        assert restored.box_positions == box_positions
        assert restored.goal_positions == goal_positions
        assert restored.grid == grid
        assert restored.width == 2
        assert restored.height == 2
    
    def test_multiple_undo_steps_restore_correct_sequence(self):
        """Test that multiple undo steps restore the correct sequence."""
        manager = UndoManager()
        
        # Create three different states
        state1 = GameState(
            grid=[[Tile.EMPTY]],
            player_pos=Position(0, 0),
            box_positions=set(),
            goal_positions=set(),
            width=1,
            height=1
        )
        
        state2 = GameState(
            grid=[[Tile.PLAYER]],
            player_pos=Position(0, 0),
            box_positions=set(),
            goal_positions=set(),
            width=1,
            height=1
        )
        
        state3 = GameState(
            grid=[[Tile.BOX]],
            player_pos=Position(0, 0),
            box_positions={Position(0, 0)},
            goal_positions=set(),
            width=1,
            height=1
        )
        
        # Push in order: state1, state2, state3
        manager.push(state1)
        manager.push(state2)
        manager.push(state3)
        
        # Pop should return in reverse order: state3, state2, state1
        restored3 = manager.pop()
        assert restored3 is not None
        assert restored3.grid == state3.grid
        
        restored2 = manager.pop()
        assert restored2 is not None
        assert restored2.grid == state2.grid
        
        restored1 = manager.pop()
        assert restored1 is not None
        assert restored1.grid == state1.grid
        
        # Stack should now be empty
        assert manager.pop() is None
    
    def test_clear_resets_depth_to_zero(self):
        """Test that clear resets depth to 0."""
        manager = UndoManager()
        state = self._create_simple_state()
        
        manager.push(state)
        manager.push(state)
        manager.push(state)
        assert manager.depth == 3
        
        manager.clear()
        assert manager.depth == 0
        assert manager.pop() is None
    
    def test_undo_after_box_push_restores_box_to_original_position(self):
        """Test that undo restores box to its original position."""
        manager = UndoManager()
        
        # Original state: box at (1, 1)
        original_box_pos = Position(1, 1)
        original_state = GameState(
            grid=[[Tile.EMPTY, Tile.EMPTY], [Tile.PLAYER, Tile.BOX]],
            player_pos=Position(1, 0),
            box_positions={original_box_pos},
            goal_positions=set(),
            width=2,
            height=2
        )
        
        manager.push(original_state)
        
        # After pushing box to (1, 2) - simulate by creating new state
        new_box_pos = Position(1, 2)
        new_state = GameState(
            grid=[[Tile.EMPTY, Tile.EMPTY], [Tile.EMPTY, Tile.PLAYER]],
            player_pos=Position(1, 1),
            box_positions={new_box_pos},  # Box moved
            goal_positions=set(),
            width=2,
            height=2
        )
        
        # Now undo
        restored = manager.pop()
        assert restored is not None
        assert original_box_pos in restored.box_positions
        assert new_box_pos not in restored.box_positions
    
    def test_state_independence_after_pop(self):
        """Test that modifying a popped state doesn't affect the stack."""
        manager = UndoManager()
        
        # Create and push a state
        state1 = GameState(
            grid=[[Tile.EMPTY]],
            player_pos=Position(0, 0),
            box_positions={Position(1, 1)},
            goal_positions=set(),
            width=1,
            height=1
        )
        
        state2 = GameState(
            grid=[[Tile.PLAYER]],
            player_pos=Position(2, 2),
            box_positions={Position(3, 3)},
            goal_positions=set(),
            width=1,
            height=1
        )
        
        manager.push(state1)
        manager.push(state2)
        
        # Pop and modify
        popped = manager.pop()
        assert popped is not None
        original_pos = popped.player_pos
        popped.player_pos = Position(9, 9)  # Modify the popped state
        popped.box_positions.add(Position(9, 9))  # Modify the box positions
        
        # Pop again - state1 should be unchanged
        popped_state1 = manager.pop()
        assert popped_state1 is not None
        assert popped_state1.player_pos == Position(0, 0)
        assert popped_state1.box_positions == {Position(1, 1)}
    
    def test_push_clones_state(self):
        """Test that push clones the state so original can be modified."""
        manager = UndoManager()
        
        # Create a state
        state = GameState(
            grid=[[Tile.EMPTY]],
            player_pos=Position(0, 0),
            box_positions={Position(1, 1)},
            goal_positions=set(),
            width=1,
            height=1
        )
        
        manager.push(state)
        
        # Modify the original state
        state.player_pos = Position(5, 5)
        state.box_positions.add(Position(6, 6))
        state.grid[0][0] = Tile.WALL
        
        # Pop should return the cloned state, unaffected by modifications
        popped = manager.pop()
        assert popped is not None
        assert popped.player_pos == Position(0, 0)
        assert popped.box_positions == {Position(1, 1)}
        assert popped.grid[0][0] == Tile.EMPTY
    
    # Helper methods
    
    def _create_simple_state(self) -> GameState:
        """Create a simple GameState for testing."""
        return GameState(
            grid=[[Tile.EMPTY]],
            player_pos=Position(0, 0),
            box_positions=set(),
            goal_positions=set(),
            width=1,
            height=1
        )
