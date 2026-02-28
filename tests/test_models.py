"""Tests for core data models."""
import pytest
from gridshift.models import Tile, Direction, Position, GameState


def test_tile_enum_values():
    """Test that Tile enum has correct values."""
    assert Tile.WALL.value == '#'
    assert Tile.PLAYER.value == '@'
    assert Tile.BOX.value == '$'
    assert Tile.GOAL.value == '.'
    assert Tile.EMPTY.value == ' '


def test_direction_enum():
    """Test Direction enum."""
    assert Direction.UP.value == 'UP'
    assert Direction.DOWN.value == 'DOWN'
    assert Direction.LEFT.value == 'LEFT'
    assert Direction.RIGHT.value == 'RIGHT'


def test_position_equality():
    """Test Position equality."""
    pos1 = Position(1, 2)
    pos2 = Position(1, 2)
    pos3 = Position(2, 1)
    
    assert pos1 == pos2
    assert pos1 != pos3
    assert pos2 != pos3


def test_position_hashable():
    """Test that Position can be used in sets and as dict keys."""
    pos1 = Position(1, 2)
    pos2 = Position(1, 2)
    pos3 = Position(2, 1)
    
    position_set = {pos1, pos2, pos3}
    assert len(position_set) == 2  # pos1 and pos2 are the same
    
    position_dict = {pos1: "a", pos3: "b"}
    assert position_dict[pos2] == "a"  # pos2 is same as pos1


def test_gamestate_clone_independence():
    """Test that GameState.clone() produces an independent copy."""
    # Create original state
    grid = [[Tile.WALL, Tile.PLAYER], [Tile.BOX, Tile.GOAL]]
    player_pos = Position(0, 1)
    box_positions = {Position(1, 0)}
    goal_positions = {Position(1, 1)}
    
    original = GameState(
        grid=grid,
        player_pos=player_pos,
        box_positions=box_positions,
        goal_positions=goal_positions,
        width=2,
        height=2
    )
    
    # Clone it
    cloned = original.clone()
    
    # Verify initial equality
    assert cloned.player_pos == original.player_pos
    assert cloned.box_positions == original.box_positions
    assert cloned.goal_positions == original.goal_positions
    assert cloned.width == original.width
    assert cloned.height == original.height
    
    # Modify the clone
    cloned.grid[0][0] = Tile.EMPTY
    cloned.player_pos = Position(1, 1)
    cloned.box_positions.add(Position(0, 0))
    cloned.goal_positions.add(Position(0, 1))
    cloned.width = 3
    
    # Verify original is unchanged
    assert original.grid[0][0] == Tile.WALL
    assert original.player_pos == Position(0, 1)
    assert Position(0, 0) not in original.box_positions
    assert Position(0, 1) not in original.goal_positions
    assert original.width == 2


def test_gamestate_clone_grid_independence():
    """Test that modifying cloned grid doesn't affect original."""
    grid = [[Tile.WALL, Tile.PLAYER], [Tile.BOX, Tile.GOAL]]
    original = GameState(
        grid=grid,
        player_pos=Position(0, 1),
        box_positions={Position(1, 0)},
        goal_positions={Position(1, 1)},
        width=2,
        height=2
    )
    
    cloned = original.clone()
    
    # Modify cloned grid
    cloned.grid[1][0] = Tile.EMPTY
    
    # Original should be unchanged
    assert original.grid[1][0] == Tile.BOX


def test_gamestate_clone_positions_independence():
    """Test that modifying cloned position sets doesn't affect original."""
    original = GameState(
        grid=[[Tile.WALL]],
        player_pos=Position(0, 0),
        box_positions={Position(1, 1), Position(2, 2)},
        goal_positions={Position(3, 3)},
        width=1,
        height=1
    )
    
    cloned = original.clone()
    
    # Modify cloned position sets
    cloned.box_positions.add(Position(4, 4))
    cloned.goal_positions.clear()
    
    # Original should be unchanged
    assert len(original.box_positions) == 2
    assert Position(4, 4) not in original.box_positions
    assert len(original.goal_positions) == 1
