"""Tests for level loading and validation."""
import pytest
from gridshift.level_loader import parse_level, load_level
from gridshift.models import Tile, Position, GameState


def test_valid_level_parsing():
    """Test parsing a valid level."""
    level_text = """#####
#@$.#
#####"""
    
    state = parse_level(level_text)
    
    assert state.player_pos == Position(1, 1)
    assert Position(1, 2) in state.box_positions
    assert Position(1, 3) in state.goal_positions
    assert state.width == 5
    assert state.height == 3
    assert len(state.box_positions) == 1
    assert len(state.goal_positions) == 1


def test_missing_player():
    """Test that missing player raises ValueError."""
    level_text = """#####
# $.#
#####"""
    
    with pytest.raises(ValueError, match="No player.*found"):
        parse_level(level_text)


def test_multiple_players():
    """Test that multiple players raises ValueError."""
    level_text = """#####
#@$.#
#@  #
#####"""
    
    with pytest.raises(ValueError, match="Multiple players found"):
        parse_level(level_text)


def test_no_boxes():
    """Test that no boxes raises ValueError."""
    level_text = """#####
#@ .#
#####"""
    
    with pytest.raises(ValueError, match="No boxes.*found"):
        parse_level(level_text)


def test_no_goals():
    """Test that no goals raises ValueError."""
    level_text = """#####
#@$ #
#####"""
    
    with pytest.raises(ValueError, match="No goals.*found"):
        parse_level(level_text)


def test_invalid_characters():
    """Test that invalid characters raise ValueError."""
    level_text = """#####
#@$X#
#####"""
    
    with pytest.raises(ValueError, match="Invalid character"):
        parse_level(level_text)


def test_ragged_lines():
    """Test that ragged lines are padded correctly."""
    level_text = """#####
#@$.#
###"""
    
    state = parse_level(level_text)
    
    # All rows should be padded to width 5
    assert state.width == 5
    assert state.height == 3
    assert len(state.grid[0]) == 5
    assert len(state.grid[1]) == 5
    assert len(state.grid[2]) == 5
    
    # Last row should be padded with EMPTY tiles
    assert state.grid[2][3] == Tile.EMPTY
    assert state.grid[2][4] == Tile.EMPTY


def test_multiple_boxes_and_goals():
    """Test level with multiple boxes and goals."""
    level_text = """#######
#@$ $ #
#. . .#
#######"""
    
    state = parse_level(level_text)
    
    assert len(state.box_positions) == 2
    assert len(state.goal_positions) == 3
    assert Position(1, 2) in state.box_positions
    assert Position(1, 4) in state.box_positions
    assert Position(2, 1) in state.goal_positions
    assert Position(2, 3) in state.goal_positions
    assert Position(2, 5) in state.goal_positions


def test_empty_level():
    """Test that an empty level raises ValueError."""
    with pytest.raises(ValueError, match="Level is empty"):
        parse_level("")


def test_player_position_correct():
    """Test that player position is correctly identified."""
    level_text = """#######
#  $  #
# .@. #
#######"""
    
    state = parse_level(level_text)
    
    assert state.player_pos == Position(2, 3)
    assert state.grid[2][3] == Tile.PLAYER


def test_grid_structure():
    """Test that grid structure is correct."""
    level_text = """###
#@$
#.#"""
    
    state = parse_level(level_text)
    
    # Check grid dimensions
    assert len(state.grid) == 3
    assert all(len(row) == 3 for row in state.grid)
    
    # Check specific tiles
    assert state.grid[0][0] == Tile.WALL
    assert state.grid[1][1] == Tile.PLAYER
    assert state.grid[1][2] == Tile.BOX
    assert state.grid[2][1] == Tile.GOAL


def test_load_level_from_file(tmp_path):
    """Test loading a level from a file."""
    # Create a temporary level file
    level_file = tmp_path / "test_level.txt"
    level_content = """#####
#@$.#
#####"""
    level_file.write_text(level_content)
    
    # Load the level
    state = load_level(str(level_file))
    
    assert state.player_pos == Position(1, 1)
    assert len(state.box_positions) == 1
    assert len(state.goal_positions) == 1


def test_load_nonexistent_file():
    """Test that loading a nonexistent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_level("/nonexistent/file.txt")


def test_complex_level():
    """Test a more complex level layout."""
    level_text = """##########
#        #
# $$ $ $ #
# .@. .  #
#        #
##########"""
    
    state = parse_level(level_text)
    
    assert state.player_pos == Position(3, 3)
    assert len(state.box_positions) == 4
    assert len(state.goal_positions) == 3
    assert state.width == 10
    assert state.height == 6


def test_wall_boundaries():
    """Test that walls are correctly identified."""
    level_text = """#####
#@$.#
#####"""
    
    state = parse_level(level_text)
    
    # Check corners are walls
    assert state.grid[0][0] == Tile.WALL
    assert state.grid[0][4] == Tile.WALL
    assert state.grid[2][0] == Tile.WALL
    assert state.grid[2][4] == Tile.WALL


def test_ragged_lines_multiple_lengths():
    """Test ragged lines with varying lengths."""
    level_text = """#
##
###
#@$.#
###
##
#"""
    
    state = parse_level(level_text)
    
    # All rows should be padded to width 5 (longest line)
    assert state.width == 5
    assert all(len(row) == 5 for row in state.grid)
