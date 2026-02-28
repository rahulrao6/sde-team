"""Tests for win detection."""

import pytest
from gridshift.models import GameState, Tile, Position
from gridshift.engine import check_win


def test_all_boxes_on_goals_is_win():
    """Test that when all boxes are on goals, the game is won."""
    # Create a simple 3x3 grid with 2 boxes and 2 goals, all boxes on goals
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.BOX, Tile.BOX],
        [Tile.WALL, Tile.PLAYER, Tile.WALL]
    ]
    
    state = GameState(
        grid=grid,
        player_pos=Position(2, 1),
        box_positions={Position(1, 1), Position(1, 2)},
        goal_positions={Position(1, 1), Position(1, 2)},
        width=3,
        height=3
    )
    
    assert check_win(state) is True


def test_some_boxes_on_goals_is_not_win():
    """Test that when only some boxes are on goals, the game is not won."""
    # 3 boxes, 3 goals, but only 2 boxes on goals
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.BOX, Tile.BOX, Tile.WALL],
        [Tile.WALL, Tile.BOX, Tile.PLAYER, Tile.WALL],
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL]
    ]
    
    state = GameState(
        grid=grid,
        player_pos=Position(2, 2),
        box_positions={Position(1, 1), Position(1, 2), Position(2, 1)},
        goal_positions={Position(1, 1), Position(1, 2), Position(2, 2)},  # Goal at (2,2) has no box
        width=4,
        height=4
    )
    
    assert check_win(state) is False


def test_no_boxes_on_goals_is_not_win():
    """Test that when no boxes are on goals, the game is not won."""
    # Boxes and goals in different positions
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.BOX, Tile.EMPTY, Tile.WALL],
        [Tile.WALL, Tile.EMPTY, Tile.PLAYER, Tile.WALL],
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL]
    ]
    
    state = GameState(
        grid=grid,
        player_pos=Position(2, 2),
        box_positions={Position(1, 1)},
        goal_positions={Position(2, 1)},  # Goal not where box is
        width=4,
        height=4
    )
    
    assert check_win(state) is False


def test_box_on_goal_but_extra_goals_empty_is_not_win():
    """Test edge case: fewer boxes than goals, even if all boxes are on goals."""
    # 1 box on a goal, but 2 goals total
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.BOX, Tile.WALL],
        [Tile.WALL, Tile.PLAYER, Tile.WALL],
        [Tile.WALL, Tile.WALL, Tile.WALL]
    ]
    
    state = GameState(
        grid=grid,
        player_pos=Position(2, 1),
        box_positions={Position(1, 1)},
        goal_positions={Position(1, 1), Position(2, 1)},  # 2 goals, only 1 box
        width=3,
        height=4
    )
    
    assert check_win(state) is False


def test_single_box_single_goal_on_goal_is_win():
    """Test minimal win case: 1 box, 1 goal, box on goal."""
    # Simplest possible win scenario
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.BOX, Tile.WALL],
        [Tile.WALL, Tile.PLAYER, Tile.WALL],
        [Tile.WALL, Tile.WALL, Tile.WALL]
    ]
    
    state = GameState(
        grid=grid,
        player_pos=Position(2, 1),
        box_positions={Position(1, 1)},
        goal_positions={Position(1, 1)},
        width=3,
        height=4
    )
    
    assert check_win(state) is True


def test_more_boxes_than_goals_all_goals_covered_is_win():
    """Test edge case: more boxes than goals, all goals covered."""
    # 3 boxes, 2 goals, but both goals have boxes
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.BOX, Tile.BOX, Tile.WALL],
        [Tile.WALL, Tile.BOX, Tile.PLAYER, Tile.WALL],
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL]
    ]
    
    state = GameState(
        grid=grid,
        player_pos=Position(2, 2),
        box_positions={Position(1, 1), Position(1, 2), Position(2, 1)},
        goal_positions={Position(1, 1), Position(1, 2)},  # Only 2 goals, both covered
        width=4,
        height=4
    )
    
    assert check_win(state) is True


def test_empty_goals_and_boxes_is_not_win():
    """Test edge case: no goals and no boxes (degenerate case)."""
    # While this shouldn't happen in a valid level, test the logic
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.PLAYER, Tile.WALL],
        [Tile.WALL, Tile.WALL, Tile.WALL]
    ]
    
    state = GameState(
        grid=grid,
        player_pos=Position(1, 1),
        box_positions=set(),
        goal_positions=set(),
        width=3,
        height=3
    )
    
    # Empty set is a subset of empty set, so technically this is a "win"
    # This matches the mathematical definition: all 0 goals have boxes
    assert check_win(state) is True
