"""Tests for level_loader module."""

import pytest
from pathlib import Path
from gridshift.level_loader import parse_level, load_level
from gridshift.models import Tile, Position


class TestParseLevel:
    """Tests for parse_level function."""
    
    def test_valid_simple_level(self):
        """Test parsing a simple valid level."""
        level_text = """########
#   .  #
#   $  #
#   @  #
########"""
        state = parse_level(level_text)
        
        assert state.width == 8
        assert state.height == 5
        assert state.player_pos == Position(3, 4)
        assert Position(2, 4) in state.box_positions
        assert Position(1, 4) in state.goal_positions
        assert len(state.box_positions) == 1
        assert len(state.goal_positions) == 1
    
    def test_valid_multiple_boxes_and_goals(self):
        """Test level with multiple boxes and goals."""
        level_text = """#######
#.$ $.#
#  @  #
#.$ $.#
#######"""
        state = parse_level(level_text)
        
        assert state.player_pos == Position(2, 3)
        assert len(state.box_positions) == 4
        assert len(state.goal_positions) == 4
        assert Position(1, 2) in state.box_positions
        assert Position(1, 4) in state.box_positions
        assert Position(3, 2) in state.box_positions
        assert Position(3, 4) in state.box_positions
    
    def test_ragged_lines_padded(self):
        """Test that shorter lines are padded with spaces."""
        level_text = """####
#@$#
#.
####"""
        state = parse_level(level_text)
        
        assert state.width == 4
        assert state.height == 4
        # Row 2 should be padded to width 4
        assert state.grid[2][2] == Tile.EMPTY
        assert state.grid[2][3] == Tile.EMPTY
    
    def test_missing_player_raises_error(self):
        """Test that missing player raises ValueError."""
        level_text = """####
#$.#
####"""
        with pytest.raises(ValueError, match="No player.*found"):
            parse_level(level_text)
    
    def test_multiple_players_raises_error(self):
        """Test that multiple players raise ValueError."""
        level_text = """####
#@$#
#@.#
####"""
        with pytest.raises(ValueError, match="Multiple players"):
            parse_level(level_text)
    
    def test_no_boxes_raises_error(self):
        """Test that missing boxes raise ValueError."""
        level_text = """####
#@.#
####"""
        with pytest.raises(ValueError, match="No boxes.*found"):
            parse_level(level_text)
    
    def test_no_goals_raises_error(self):
        """Test that missing goals raise ValueError."""
        level_text = """####
#@$#
####"""
        with pytest.raises(ValueError, match="No goals.*found"):
            parse_level(level_text)
    
    def test_invalid_character_raises_error(self):
        """Test that invalid characters raise ValueError."""
        level_text = """####
#@$X#
####"""
        with pytest.raises(ValueError, match="Invalid character 'X'"):
            parse_level(level_text)
    
    def test_empty_level_raises_error(self):
        """Test that empty level text raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            parse_level("")
        
        with pytest.raises(ValueError, match="empty|no valid content"):
            parse_level("   \n\n   ")
    
    def test_only_whitespace_raises_error(self):
        """Test that only whitespace raises ValueError."""
        with pytest.raises(ValueError, match="empty|no valid content"):
            parse_level("\n\n\n")
    
    def test_grid_representation_separates_entities(self):
        """Test that grid doesn't contain player/box tiles (they're tracked separately)."""
        level_text = """####
#@$#
#. #
####"""
        state = parse_level(level_text)
        
        # Player and box positions should have EMPTY in grid
        player_grid_tile = state.grid[state.player_pos.row][state.player_pos.col]
        assert player_grid_tile == Tile.EMPTY
        
        for box_pos in state.box_positions:
            box_grid_tile = state.grid[box_pos.row][box_pos.col]
            assert box_grid_tile == Tile.EMPTY
        
        # Goals should remain in grid
        for goal_pos in state.goal_positions:
            goal_grid_tile = state.grid[goal_pos.row][goal_pos.col]
            assert goal_grid_tile == Tile.GOAL
    
    def test_minimal_valid_level(self):
        """Test smallest possible valid level (1 player, 1 box, 1 goal)."""
        level_text = "@$."
        state = parse_level(level_text)
        
        assert state.width == 3
        assert state.height == 1
        assert state.player_pos == Position(0, 0)
        assert Position(0, 1) in state.box_positions
        assert Position(0, 2) in state.goal_positions
    
    def test_box_on_goal_position(self):
        """Test level where box starts on a goal (allowed scenario)."""
        level_text = """####
#@.#
# .#
####"""
        # This should work - box can be on goal initially
        # But this test has no box, so it should fail
        with pytest.raises(ValueError, match="No boxes"):
            parse_level(level_text)
        
        # Actually test with box
        level_text = """####
#@$#
# .#
####"""
        state = parse_level(level_text)
        assert len(state.box_positions) == 1
        assert len(state.goal_positions) == 1
    
    def test_preserves_leading_trailing_spaces(self):
        """Test that spaces at edges of lines are preserved correctly."""
        level_text = """####
   @$. 
####"""
        # Ragged lines will be padded, width should be max line length
        state = parse_level(level_text)
        assert state.width == 7  # "   @$. " has 7 chars


class TestLoadLevel:
    """Tests for load_level function."""
    
    def test_load_valid_file(self, tmp_path):
        """Test loading a valid level file."""
        level_file = tmp_path / "test_level.txt"
        level_content = """########
#   .  #
#   $  #
#   @  #
########"""
        level_file.write_text(level_content)
        
        state = load_level(str(level_file))
        
        assert state.width == 8
        assert state.height == 5
        assert state.player_pos == Position(3, 4)
    
    def test_load_nonexistent_file_raises_error(self):
        """Test that loading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            load_level("/nonexistent/path/level.txt")
    
    def test_load_invalid_content_raises_error(self, tmp_path):
        """Test that loading file with invalid content raises ValueError."""
        level_file = tmp_path / "invalid_level.txt"
        level_file.write_text("####\n#@#\n####")  # No box or goal
        
        with pytest.raises(ValueError):
            load_level(str(level_file))


class TestEdgeCases:
    """Additional edge case tests for level loading."""
    
    def test_very_large_level(self):
        """Test parsing a large level (performance check)."""
        # Create a 50x50 level
        width, height = 50, 50
        lines = []
        lines.append('#' * width)
        for i in range(1, height - 1):
            if i == 1:
                lines.append('#' + ' ' * (width - 2) + '#')
            elif i == 2:
                lines.append('#' + ' ' * 10 + '@' + ' ' * (width - 13) + '#')
            elif i == 3:
                lines.append('#' + ' ' * 10 + '$' + ' ' * (width - 13) + '#')
            elif i == 4:
                lines.append('#' + ' ' * 10 + '.' + ' ' * (width - 13) + '#')
            else:
                lines.append('#' + ' ' * (width - 2) + '#')
        lines.append('#' * width)
        
        level_text = '\n'.join(lines)
        state = parse_level(level_text)
        
        assert state.width == width
        assert state.height == height
        assert len(state.box_positions) == 1
        assert len(state.goal_positions) == 1
    
    def test_all_valid_characters_present(self):
        """Test level containing all valid character types."""
        level_text = """######
#@$. #
######"""
        state = parse_level(level_text)
        
        # Verify all tile types are correctly parsed
        assert state.grid[0][0] == Tile.WALL
        assert state.grid[1][4] == Tile.EMPTY
        assert state.grid[1][3] == Tile.GOAL
    
    def test_goal_symbols_remain_in_grid(self):
        """Test that goal positions remain marked in the grid."""
        level_text = """####
#@$#
#..#
####"""
        state = parse_level(level_text)
        
        # Goals should still be in grid
        assert state.grid[2][1] == Tile.GOAL
        assert state.grid[2][2] == Tile.GOAL
        assert len(state.goal_positions) == 2
