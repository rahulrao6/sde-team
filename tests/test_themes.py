"""Tests for visual themes."""

import pytest
from gridshift.themes import (
    Theme, NeonTheme, RetroTheme, EmojiTheme,
    ThemeType, get_theme
)


class TestTheme:
    """Test the base Theme class."""
    
    def test_default_characters(self):
        """Default theme uses standard ASCII characters."""
        theme = Theme()
        assert theme.wall == '#'
        assert theme.player == '@'
        assert theme.box == '$'
        assert theme.goal == '.'
        assert theme.empty == ' '
        assert theme.box_on_goal == '*'
        assert theme.player_on_goal == '+'
    
    def test_default_borders(self):
        """Default theme uses box-drawing borders."""
        theme = Theme()
        assert theme.border_top_left == '┌'
        assert theme.border_top_right == '┐'
        assert theme.border_bottom_left == '└'
        assert theme.border_bottom_right == '┘'
        assert theme.border_horizontal == '─'
        assert theme.border_vertical == '│'
    
    def test_cell_width(self):
        """Default theme uses single-width cells."""
        theme = Theme()
        assert theme.cell_width == 1
    
    def test_get_char(self):
        """Test get_char method."""
        theme = Theme()
        assert theme.get_char('wall') == '#'
        assert theme.get_char('player') == '@'
        assert theme.get_char('box') == '$'
        assert theme.get_char('goal') == '.'
        assert theme.get_char('invalid') == ' '  # Default to empty


class TestNeonTheme:
    """Test the Neon theme."""
    
    def test_neon_characters(self):
        """Neon theme uses special characters."""
        theme = NeonTheme()
        assert theme.wall == '█'
        assert theme.player == '@'
        assert theme.goal == '◆'  # Diamond
    
    def test_neon_borders(self):
        """Neon theme uses double-line borders."""
        theme = NeonTheme()
        assert theme.border_top_left == '╔'
        assert theme.border_top_right == '╗'
        assert theme.border_bottom_left == '╚'
        assert theme.border_bottom_right == '╝'
        assert theme.border_horizontal == '═'
        assert theme.border_vertical == '║'
    
    def test_neon_box_with_brackets(self):
        """Neon boxes are displayed with brackets."""
        theme = NeonTheme()
        assert '[' in theme.get_char('box')
        assert '█' in theme.get_char('box')
        assert ']' in theme.get_char('box')


class TestRetroTheme:
    """Test the Retro theme."""
    
    def test_retro_characters(self):
        """Retro theme uses ASCII-art style characters."""
        theme = RetroTheme()
        assert theme.wall == '▓'  # Dense hatch
        assert theme.player == '@'
        assert theme.box == '□'
        assert theme.box_on_goal == '■'
        assert theme.goal == '·'
    
    def test_retro_borders(self):
        """Retro theme uses simple ASCII borders."""
        theme = RetroTheme()
        assert theme.border_top_left == '+'
        assert theme.border_top_right == '+'
        assert theme.border_bottom_left == '+'
        assert theme.border_bottom_right == '+'
        assert theme.border_horizontal == '-'
        assert theme.border_vertical == '|'


class TestEmojiTheme:
    """Test the Emoji theme."""
    
    def test_emoji_characters(self):
        """Emoji theme uses emoji characters."""
        theme = EmojiTheme()
        assert theme.wall == '🧱'
        assert theme.player == '🏃'
        assert theme.box == '📦'
        assert theme.goal == '⭐'
        assert theme.box_on_goal == '✅'
        assert theme.player_on_goal == '🎯'
    
    def test_emoji_cell_width(self):
        """Emoji theme uses double-width cells."""
        theme = EmojiTheme()
        assert theme.cell_width == 2
    
    def test_emoji_empty_is_double_space(self):
        """Emoji theme uses two spaces for empty cells."""
        theme = EmojiTheme()
        assert theme.empty == '  '
    
    def test_emoji_special_tiles(self):
        """Emoji theme includes special tiles for future use."""
        theme = EmojiTheme()
        assert theme.ice == '🧊'
        assert theme.teleporter == '🌀'


class TestThemeRegistry:
    """Test the theme registry and factory."""
    
    def test_get_default_theme(self):
        """Get default theme by type."""
        theme = get_theme(ThemeType.DEFAULT)
        assert isinstance(theme, Theme)
        assert not isinstance(theme, (NeonTheme, RetroTheme, EmojiTheme))
    
    def test_get_neon_theme(self):
        """Get neon theme by type."""
        theme = get_theme(ThemeType.NEON)
        assert isinstance(theme, NeonTheme)
    
    def test_get_retro_theme(self):
        """Get retro theme by type."""
        theme = get_theme(ThemeType.RETRO)
        assert isinstance(theme, RetroTheme)
    
    def test_get_emoji_theme(self):
        """Get emoji theme by type."""
        theme = get_theme(ThemeType.EMOJI)
        assert isinstance(theme, EmojiTheme)
    
    def test_theme_independence(self):
        """Each call to get_theme returns a new instance."""
        theme1 = get_theme(ThemeType.DEFAULT)
        theme2 = get_theme(ThemeType.DEFAULT)
        assert theme1 is not theme2
