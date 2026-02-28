"""Unit tests for core data models."""

import pytest
from gridshift.models import Tile, Direction, Position, GameState


class TestTile:
    """Tests for Tile enum."""
    
    def test_tile_values(self):
        """Test that Tile enum has correct character values."""
        assert Tile.WALL.value == '#'
        assert Tile.PLAYER.value == '@'
        assert Tile.BOX.value == '$'
        assert Tile.GOAL.value == '.'
        assert Tile.EMPTY.value == ' '
    
    def test_from_char_valid(self):
        """Test parsing valid characters into Tiles."""
        assert Tile.from_char('#') == Tile.WALL
        assert Tile.from_char('@') == Tile.PLAYER
        assert Tile.from_char('$') == Tile.BOX
        assert Tile.from_char('.') == Tile.GOAL
        assert Tile.from_char(' ') == Tile.EMPTY
    
    def test_from_char_invalid(self):
        """Test that invalid characters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid tile character"):
            Tile.from_char('X')
        with pytest.raises(ValueError, match="Invalid tile character"):
            Tile.from_char('!')


class TestDirection:
    """Tests for Direction enum."""
    
    def test_direction_values(self):
        """Test that Direction enum has correct delta values."""
        assert Direction.UP.value == (-1, 0)
        assert Direction.DOWN.value == (1, 0)
        assert Direction.LEFT.value == (0, -1)
        assert Direction.RIGHT.value == (0, 1)


class TestPosition:
    """Tests for Position dataclass."""
    
    def test_position_creation(self):
        """Test creating a Position."""
        pos = Position(5, 10)
        assert pos.row == 5
        assert pos.col == 10
    
    def test_position_equality(self):
        """Test that Positions with same coordinates are equal."""
        pos1 = Position(3, 4)
        pos2 = Position(3, 4)
        pos3 = Position(3, 5)
        assert pos1 == pos2
        assert pos1 != pos3
    
    def test_position_hashable(self):
        """Test that Position can be used in sets."""
        pos1 = Position(1, 2)
        pos2 = Position(1, 2)
        pos3 = Position(2, 3)
        pos_set = {pos1, pos2, pos3}
        assert len(pos_set) == 2  # pos1 and pos2 are the same
    
    def test_position_move(self):
        """Test moving a position in various directions."""
        pos = Position(5, 5)
        assert pos.move(Direction.UP) == Position(4, 5)
        assert pos.move(Direction.DOWN) == Position(6, 5)
        assert pos.move(Direction.LEFT) == Position(5, 4)
        assert pos.move(Direction.RIGHT) == Position(5, 6)
    
    def test_position_immutable(self):
        """Test that Position is frozen/immutable."""
        pos = Position(5, 5)
        with pytest.raises(AttributeError):
            pos.row = 10


class TestGameState:
    """Tests for GameState dataclass."""
    
    def test_gamestate_creation(self):
        """Test creating a GameState."""
        grid = [[Tile.WALL, Tile.EMPTY], [Tile.EMPTY, Tile.WALL]]
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
        
        assert state.width == 2
        assert state.height == 2
        assert state.player_pos == player_pos
        assert state.box_positions == box_positions
        assert state.goal_positions == goal_positions
    
    def test_gamestate_clone_independence(self):
        """Test that cloning creates an independent copy."""
        grid = [[Tile.EMPTY, Tile.BOX], [Tile.PLAYER, Tile.GOAL]]
        player_pos = Position(1, 0)
        box_positions = {Position(0, 1)}
        goal_positions = {Position(1, 1)}
        
        original = GameState(
            grid=grid,
            player_pos=player_pos,
            box_positions=box_positions,
            goal_positions=goal_positions,
            width=2,
            height=2
        )
        
        cloned = original.clone()
        
        # Modify the clone
        cloned.grid[0][0] = Tile.WALL
        cloned.player_pos = Position(0, 0)
        cloned.box_positions.add(Position(1, 1))
        cloned.goal_positions.add(Position(0, 0))
        
        # Original should remain unchanged
        assert original.grid[0][0] == Tile.EMPTY
        assert original.player_pos == Position(1, 0)
        assert original.box_positions == {Position(0, 1)}
        assert original.goal_positions == {Position(1, 1)}
        
        # Clone should have the modifications
        assert cloned.grid[0][0] == Tile.WALL
        assert cloned.player_pos == Position(0, 0)
        assert Position(1, 1) in cloned.box_positions
        assert Position(0, 0) in cloned.goal_positions
    
    def test_gamestate_clone_equality(self):
        """Test that a clone initially equals the original."""
        grid = [[Tile.WALL, Tile.EMPTY]]
        state = GameState(
            grid=grid,
            player_pos=Position(0, 1),
            box_positions=set(),
            goal_positions=set(),
            width=2,
            height=1
        )
        
        cloned = state.clone()
        
        assert cloned.player_pos == state.player_pos
        assert cloned.box_positions == state.box_positions
        assert cloned.goal_positions == state.goal_positions
        assert cloned.width == state.width
        assert cloned.height == state.height
        assert cloned.grid == state.grid
