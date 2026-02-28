"""Unit tests for core data models."""

import unittest
from gridshift.models import Tile, Direction, Position, GameState


class TestTile(unittest.TestCase):
    """Tests for Tile enum."""

    def test_tile_values(self):
        """Test that Tile enum has correct character values."""
        self.assertEqual(Tile.WALL.value, '#')
        self.assertEqual(Tile.PLAYER.value, '@')
        self.assertEqual(Tile.BOX.value, '$')
        self.assertEqual(Tile.GOAL.value, '.')
        self.assertEqual(Tile.EMPTY.value, ' ')

    def test_from_char_valid(self):
        """Test parsing valid tile characters."""
        self.assertEqual(Tile.from_char('#'), Tile.WALL)
        self.assertEqual(Tile.from_char('@'), Tile.PLAYER)
        self.assertEqual(Tile.from_char('$'), Tile.BOX)
        self.assertEqual(Tile.from_char('.'), Tile.GOAL)
        self.assertEqual(Tile.from_char(' '), Tile.EMPTY)

    def test_from_char_invalid(self):
        """Test parsing invalid tile characters raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Tile.from_char('X')
        self.assertIn('Invalid tile character', str(context.exception))
        self.assertIn("'X'", str(context.exception))

    def test_from_char_multiple_invalid(self):
        """Test various invalid characters."""
        invalid_chars = ['a', '1', '!', '\n', '\t']
        for char in invalid_chars:
            with self.assertRaises(ValueError):
                Tile.from_char(char)


class TestDirection(unittest.TestCase):
    """Tests for Direction enum."""

    def test_direction_values(self):
        """Test that Direction enum has correct delta values."""
        self.assertEqual(Direction.UP.value, (-1, 0))
        self.assertEqual(Direction.DOWN.value, (1, 0))
        self.assertEqual(Direction.LEFT.value, (0, -1))
        self.assertEqual(Direction.RIGHT.value, (0, 1))

    def test_delta_properties(self):
        """Test delta_row and delta_col properties."""
        self.assertEqual(Direction.UP.delta_row, -1)
        self.assertEqual(Direction.UP.delta_col, 0)
        
        self.assertEqual(Direction.DOWN.delta_row, 1)
        self.assertEqual(Direction.DOWN.delta_col, 0)
        
        self.assertEqual(Direction.LEFT.delta_row, 0)
        self.assertEqual(Direction.LEFT.delta_col, -1)
        
        self.assertEqual(Direction.RIGHT.delta_row, 0)
        self.assertEqual(Direction.RIGHT.delta_col, 1)


class TestPosition(unittest.TestCase):
    """Tests for Position dataclass."""

    def test_position_creation(self):
        """Test creating Position instances."""
        pos = Position(5, 10)
        self.assertEqual(pos.row, 5)
        self.assertEqual(pos.col, 10)

    def test_position_equality(self):
        """Test Position equality comparison."""
        pos1 = Position(3, 4)
        pos2 = Position(3, 4)
        pos3 = Position(3, 5)
        pos4 = Position(4, 4)
        
        self.assertEqual(pos1, pos2)
        self.assertNotEqual(pos1, pos3)
        self.assertNotEqual(pos1, pos4)

    def test_position_hashable(self):
        """Test that Position can be used in sets and as dict keys."""
        pos1 = Position(1, 2)
        pos2 = Position(1, 2)
        pos3 = Position(2, 3)
        
        # Should be usable in a set
        pos_set = {pos1, pos2, pos3}
        self.assertEqual(len(pos_set), 2)  # pos1 and pos2 are same
        
        # Should be usable as dict key
        pos_dict = {pos1: 'a', pos3: 'b'}
        self.assertEqual(pos_dict[pos2], 'a')  # pos2 same as pos1

    def test_position_immutable(self):
        """Test that Position is immutable (frozen)."""
        pos = Position(5, 6)
        with self.assertRaises(AttributeError):
            pos.row = 10
        with self.assertRaises(AttributeError):
            pos.col = 20

    def test_position_move(self):
        """Test moving a Position in different directions."""
        pos = Position(5, 5)
        
        up_pos = pos.move(Direction.UP)
        self.assertEqual(up_pos, Position(4, 5))
        
        down_pos = pos.move(Direction.DOWN)
        self.assertEqual(down_pos, Position(6, 5))
        
        left_pos = pos.move(Direction.LEFT)
        self.assertEqual(left_pos, Position(5, 4))
        
        right_pos = pos.move(Direction.RIGHT)
        self.assertEqual(right_pos, Position(5, 6))
        
        # Original position should be unchanged
        self.assertEqual(pos, Position(5, 5))


class TestGameState(unittest.TestCase):
    """Tests for GameState dataclass."""

    def setUp(self):
        """Set up test fixtures."""
        self.grid = [
            [Tile.WALL, Tile.WALL, Tile.WALL],
            [Tile.WALL, Tile.EMPTY, Tile.WALL],
            [Tile.WALL, Tile.WALL, Tile.WALL]
        ]
        self.player_pos = Position(1, 1)
        self.box_positions = {Position(1, 2)}
        self.goal_positions = {Position(2, 2)}

    def test_gamestate_creation(self):
        """Test creating a GameState instance."""
        state = GameState(
            grid=self.grid,
            player_pos=self.player_pos,
            box_positions=self.box_positions,
            goal_positions=self.goal_positions,
            width=3,
            height=3
        )
        
        self.assertEqual(state.width, 3)
        self.assertEqual(state.height, 3)
        self.assertEqual(state.player_pos, Position(1, 1))
        self.assertEqual(len(state.box_positions), 1)
        self.assertEqual(len(state.goal_positions), 1)

    def test_gamestate_clone_independence(self):
        """Test that clone creates an independent copy."""
        state = GameState(
            grid=self.grid,
            player_pos=self.player_pos,
            box_positions=self.box_positions,
            goal_positions=self.goal_positions,
            width=3,
            height=3
        )
        
        cloned = state.clone()
        
        # Check that values are equal
        self.assertEqual(state.player_pos, cloned.player_pos)
        self.assertEqual(state.box_positions, cloned.box_positions)
        self.assertEqual(state.goal_positions, cloned.goal_positions)
        self.assertEqual(state.width, cloned.width)
        self.assertEqual(state.height, cloned.height)
        
        # Modify the clone's grid
        cloned.grid[1][1] = Tile.BOX
        self.assertEqual(state.grid[1][1], Tile.EMPTY)  # Original unchanged
        
        # Modify the clone's box_positions
        cloned.box_positions.add(Position(2, 1))
        self.assertEqual(len(state.box_positions), 1)  # Original unchanged
        self.assertEqual(len(cloned.box_positions), 2)
        
        # Modify the clone's goal_positions
        cloned.goal_positions.add(Position(1, 3))
        self.assertEqual(len(state.goal_positions), 1)  # Original unchanged
        self.assertEqual(len(cloned.goal_positions), 2)

    def test_gamestate_clone_grid_deep_copy(self):
        """Test that grid is deeply copied, not just shallow."""
        state = GameState(
            grid=self.grid,
            player_pos=self.player_pos,
            box_positions=self.box_positions,
            goal_positions=self.goal_positions,
            width=3,
            height=3
        )
        
        cloned = state.clone()
        
        # Modify a nested row in the clone
        cloned.grid[0][0] = Tile.EMPTY
        
        # Original should be unchanged
        self.assertEqual(state.grid[0][0], Tile.WALL)

    def test_gamestate_clone_position_immutability(self):
        """Test that Position immutability works correctly with clone."""
        state = GameState(
            grid=self.grid,
            player_pos=self.player_pos,
            box_positions=self.box_positions,
            goal_positions=self.goal_positions,
            width=3,
            height=3
        )
        
        cloned = state.clone()
        
        # Since Position is immutable, changing player_pos in clone
        # should not affect original
        cloned.player_pos = Position(2, 2)
        
        self.assertEqual(state.player_pos, Position(1, 1))
        self.assertEqual(cloned.player_pos, Position(2, 2))


if __name__ == '__main__':
    unittest.main()
