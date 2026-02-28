"""Tests for the movement and collision engine."""

import unittest
from gridshift.models import GameState, Direction, Position, Tile
from gridshift.engine import move


class TestEngineMovement(unittest.TestCase):
    """Test basic player movement into empty cells."""
    
    def test_move_up_into_empty(self):
        """Player should move up into empty cell."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.EMPTY, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.WALL],
                [Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(2, 1),
            box_positions=set(),
            goal_positions=set(),
            width=3,
            height=4
        )
        
        new_state, moved = move(state, Direction.UP)
        
        self.assertTrue(moved)
        self.assertEqual(new_state.player_pos, Position(1, 1))
        self.assertEqual(new_state.grid[1][1], Tile.PLAYER)
        self.assertEqual(new_state.grid[2][1], Tile.EMPTY)
        # Original state unchanged
        self.assertEqual(state.player_pos, Position(2, 1))
    
    def test_move_down_into_empty(self):
        """Player should move down into empty cell."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.WALL],
                [Tile.WALL, Tile.EMPTY, Tile.WALL],
                [Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(1, 1),
            box_positions=set(),
            goal_positions=set(),
            width=3,
            height=4
        )
        
        new_state, moved = move(state, Direction.DOWN)
        
        self.assertTrue(moved)
        self.assertEqual(new_state.player_pos, Position(2, 1))
        self.assertEqual(new_state.grid[2][1], Tile.PLAYER)
        self.assertEqual(new_state.grid[1][1], Tile.EMPTY)
    
    def test_move_left_into_empty(self):
        """Player should move left into empty cell."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.EMPTY, Tile.PLAYER, Tile.WALL],
                [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(1, 2),
            box_positions=set(),
            goal_positions=set(),
            width=4,
            height=3
        )
        
        new_state, moved = move(state, Direction.LEFT)
        
        self.assertTrue(moved)
        self.assertEqual(new_state.player_pos, Position(1, 1))
        self.assertEqual(new_state.grid[1][1], Tile.PLAYER)
        self.assertEqual(new_state.grid[1][2], Tile.EMPTY)
    
    def test_move_right_into_empty(self):
        """Player should move right into empty cell."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.EMPTY, Tile.WALL],
                [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(1, 1),
            box_positions=set(),
            goal_positions=set(),
            width=4,
            height=3
        )
        
        new_state, moved = move(state, Direction.RIGHT)
        
        self.assertTrue(moved)
        self.assertEqual(new_state.player_pos, Position(1, 2))
        self.assertEqual(new_state.grid[1][2], Tile.PLAYER)
        self.assertEqual(new_state.grid[1][1], Tile.EMPTY)


class TestEngineWallCollision(unittest.TestCase):
    """Test wall collision in all directions."""
    
    def test_move_up_into_wall(self):
        """Player should be blocked by wall above."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.WALL],
                [Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(1, 1),
            box_positions=set(),
            goal_positions=set(),
            width=3,
            height=3
        )
        
        new_state, moved = move(state, Direction.UP)
        
        self.assertFalse(moved)
        self.assertEqual(new_state.player_pos, Position(1, 1))
        self.assertIs(new_state, state)  # Should return original state
    
    def test_move_down_into_wall(self):
        """Player should be blocked by wall below."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.WALL],
                [Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(1, 1),
            box_positions=set(),
            goal_positions=set(),
            width=3,
            height=3
        )
        
        new_state, moved = move(state, Direction.DOWN)
        
        self.assertFalse(moved)
        self.assertEqual(new_state.player_pos, Position(1, 1))
        self.assertIs(new_state, state)
    
    def test_move_left_into_wall(self):
        """Player should be blocked by wall to the left."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.WALL],
                [Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(1, 1),
            box_positions=set(),
            goal_positions=set(),
            width=3,
            height=3
        )
        
        new_state, moved = move(state, Direction.LEFT)
        
        self.assertFalse(moved)
        self.assertEqual(new_state.player_pos, Position(1, 1))
        self.assertIs(new_state, state)
    
    def test_move_right_into_wall(self):
        """Player should be blocked by wall to the right."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.WALL],
                [Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(1, 1),
            box_positions=set(),
            goal_positions=set(),
            width=3,
            height=3
        )
        
        new_state, moved = move(state, Direction.RIGHT)
        
        self.assertFalse(moved)
        self.assertEqual(new_state.player_pos, Position(1, 1))
        self.assertIs(new_state, state)


class TestEngineBoxPushing(unittest.TestCase):
    """Test box pushing mechanics."""
    
    def test_push_box_into_empty(self):
        """Player should push box into empty cell."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.BOX, Tile.EMPTY],
                [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(1, 1),
            box_positions={Position(1, 2)},
            goal_positions=set(),
            width=4,
            height=3
        )
        
        new_state, moved = move(state, Direction.RIGHT)
        
        self.assertTrue(moved)
        self.assertEqual(new_state.player_pos, Position(1, 2))
        self.assertIn(Position(1, 3), new_state.box_positions)
        self.assertNotIn(Position(1, 2), new_state.box_positions)
        self.assertEqual(new_state.grid[1][2], Tile.PLAYER)
        self.assertEqual(new_state.grid[1][3], Tile.BOX)
        self.assertEqual(new_state.grid[1][1], Tile.EMPTY)
    
    def test_push_box_into_wall(self):
        """Player should be blocked when trying to push box into wall."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.BOX, Tile.WALL],
            ],
            player_pos=Position(1, 1),
            box_positions={Position(1, 2)},
            goal_positions=set(),
            width=4,
            height=2
        )
        
        new_state, moved = move(state, Direction.RIGHT)
        
        self.assertFalse(moved)
        self.assertEqual(new_state.player_pos, Position(1, 1))
        self.assertIn(Position(1, 2), new_state.box_positions)
        self.assertIs(new_state, state)
    
    def test_push_box_into_box(self):
        """Player should be blocked when trying to push box into another box."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.BOX, Tile.BOX, Tile.WALL],
                [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(1, 1),
            box_positions={Position(1, 2), Position(1, 3)},
            goal_positions=set(),
            width=5,
            height=3
        )
        
        new_state, moved = move(state, Direction.RIGHT)
        
        self.assertFalse(moved)
        self.assertEqual(new_state.player_pos, Position(1, 1))
        self.assertIn(Position(1, 2), new_state.box_positions)
        self.assertIn(Position(1, 3), new_state.box_positions)
        self.assertIs(new_state, state)
    
    def test_push_box_onto_goal(self):
        """Player should be able to push box onto goal."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.BOX, Tile.GOAL],
                [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(1, 1),
            box_positions={Position(1, 2)},
            goal_positions={Position(1, 3)},
            width=4,
            height=3
        )
        
        new_state, moved = move(state, Direction.RIGHT)
        
        self.assertTrue(moved)
        self.assertEqual(new_state.player_pos, Position(1, 2))
        self.assertIn(Position(1, 3), new_state.box_positions)
        self.assertNotIn(Position(1, 2), new_state.box_positions)
        self.assertEqual(new_state.grid[1][3], Tile.BOX)


class TestEngineGoalInteraction(unittest.TestCase):
    """Test player and box interaction with goals."""
    
    def test_player_walk_onto_goal(self):
        """Player should be able to walk onto goal."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.GOAL],
                [Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(1, 1),
            box_positions=set(),
            goal_positions={Position(1, 2)},
            width=3,
            height=3
        )
        
        new_state, moved = move(state, Direction.RIGHT)
        
        self.assertTrue(moved)
        self.assertEqual(new_state.player_pos, Position(1, 2))
        self.assertEqual(new_state.grid[1][2], Tile.PLAYER)
        self.assertEqual(new_state.grid[1][1], Tile.EMPTY)
    
    def test_player_walk_off_goal(self):
        """Player should be able to walk off goal, restoring goal tile."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.EMPTY],
                [Tile.WALL, Tile.WALL, Tile.WALL],
            ],
            player_pos=Position(1, 1),
            box_positions=set(),
            goal_positions={Position(1, 1)},  # Player is on goal
            width=3,
            height=3
        )
        
        new_state, moved = move(state, Direction.RIGHT)
        
        self.assertTrue(moved)
        self.assertEqual(new_state.player_pos, Position(1, 2))
        self.assertEqual(new_state.grid[1][2], Tile.PLAYER)
        self.assertEqual(new_state.grid[1][1], Tile.GOAL)  # Goal restored


class TestEngineEdgeCases(unittest.TestCase):
    """Test edge cases and boundaries."""
    
    def test_move_off_grid_top(self):
        """Moving off top edge should be blocked."""
        state = GameState(
            grid=[
                [Tile.PLAYER],
            ],
            player_pos=Position(0, 0),
            box_positions=set(),
            goal_positions=set(),
            width=1,
            height=1
        )
        
        new_state, moved = move(state, Direction.UP)
        
        self.assertFalse(moved)
        self.assertIs(new_state, state)
    
    def test_move_off_grid_bottom(self):
        """Moving off bottom edge should be blocked."""
        state = GameState(
            grid=[
                [Tile.PLAYER],
            ],
            player_pos=Position(0, 0),
            box_positions=set(),
            goal_positions=set(),
            width=1,
            height=1
        )
        
        new_state, moved = move(state, Direction.DOWN)
        
        self.assertFalse(moved)
        self.assertIs(new_state, state)
    
    def test_move_off_grid_left(self):
        """Moving off left edge should be blocked."""
        state = GameState(
            grid=[
                [Tile.PLAYER],
            ],
            player_pos=Position(0, 0),
            box_positions=set(),
            goal_positions=set(),
            width=1,
            height=1
        )
        
        new_state, moved = move(state, Direction.LEFT)
        
        self.assertFalse(moved)
        self.assertIs(new_state, state)
    
    def test_move_off_grid_right(self):
        """Moving off right edge should be blocked."""
        state = GameState(
            grid=[
                [Tile.PLAYER],
            ],
            player_pos=Position(0, 0),
            box_positions=set(),
            goal_positions=set(),
            width=1,
            height=1
        )
        
        new_state, moved = move(state, Direction.RIGHT)
        
        self.assertFalse(moved)
        self.assertIs(new_state, state)


class TestEngineStateImmutability(unittest.TestCase):
    """Test that original state is never mutated."""
    
    def test_state_immutability_on_valid_move(self):
        """Original state should remain unchanged after valid move."""
        original_grid = [
            [Tile.WALL, Tile.WALL, Tile.WALL],
            [Tile.WALL, Tile.EMPTY, Tile.WALL],
            [Tile.WALL, Tile.PLAYER, Tile.WALL],
        ]
        state = GameState(
            grid=original_grid,
            player_pos=Position(2, 1),
            box_positions=set(),
            goal_positions=set(),
            width=3,
            height=3
        )
        
        original_player_pos = state.player_pos
        
        new_state, moved = move(state, Direction.UP)
        
        self.assertTrue(moved)
        # Original state unchanged
        self.assertEqual(state.player_pos, original_player_pos)
        self.assertEqual(state.grid[2][1], Tile.PLAYER)
        # New state changed
        self.assertEqual(new_state.player_pos, Position(1, 1))
        self.assertEqual(new_state.grid[1][1], Tile.PLAYER)
    
    def test_state_immutability_on_box_push(self):
        """Original state should remain unchanged when pushing box."""
        state = GameState(
            grid=[
                [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
                [Tile.WALL, Tile.PLAYER, Tile.BOX, Tile.EMPTY],
            ],
            player_pos=Position(1, 1),
            box_positions={Position(1, 2)},
            goal_positions=set(),
            width=4,
            height=2
        )
        
        original_box_positions = state.box_positions.copy()
        
        new_state, moved = move(state, Direction.RIGHT)
        
        self.assertTrue(moved)
        # Original state unchanged
        self.assertEqual(state.box_positions, original_box_positions)
        self.assertIn(Position(1, 2), state.box_positions)
        # New state changed
        self.assertIn(Position(1, 3), new_state.box_positions)
        self.assertNotIn(Position(1, 2), new_state.box_positions)


if __name__ == '__main__':
    unittest.main()
