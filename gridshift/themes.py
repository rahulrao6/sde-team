"""Visual theme definitions for GridShift game."""

import curses
from enum import Enum
from typing import Dict, Tuple, Optional


class ThemeType(Enum):
    """Available visual themes."""
    DEFAULT = "default"
    NEON = "neon"
    RETRO = "retro"
    EMOJI = "emoji"


class Theme:
    """Base theme class defining visual representation."""
    
    def __init__(self):
        """Initialize theme with default characters and colors."""
        # Character mappings
        self.wall = '#'
        self.player = '@'
        self.player_on_goal = '+'
        self.box = '$'
        self.box_on_goal = '*'
        self.goal = '.'
        self.empty = ' '
        
        # Border characters
        self.border_top_left = '┌'
        self.border_top_right = '┐'
        self.border_bottom_left = '└'
        self.border_bottom_right = '┘'
        self.border_horizontal = '─'
        self.border_vertical = '│'
        
        # Cell width (1 for ASCII, 2 for emoji)
        self.cell_width = 1
        
        # Color pairs (to be initialized)
        self.color_wall = 1
        self.color_player = 2
        self.color_box = 3
        self.color_goal = 4
        self.color_box_on_goal = 5
        self.color_player_on_goal = 6
        self.color_hud = 7
        self.color_message = 8
        self.color_win = 9
        self.color_border = 10
    
    def init_colors(self):
        """
        Initialize curses color pairs for this theme.
        Returns True if colors were successfully initialized.
        """
        if not curses.has_colors():
            return False
        
        try:
            curses.start_color()
            curses.use_default_colors()
            
            # Default theme colors
            curses.init_pair(self.color_wall, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(self.color_player, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(self.color_box, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(self.color_goal, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_box_on_goal, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_player_on_goal, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(self.color_hud, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(self.color_message, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            curses.init_pair(self.color_win, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_border, curses.COLOR_BLUE, curses.COLOR_BLACK)
            
            return True
        except:
            return False
    
    def get_char(self, element: str) -> str:
        """
        Get the character representation for a game element.
        
        Args:
            element: One of 'wall', 'player', 'player_on_goal', 'box', 
                    'box_on_goal', 'goal', 'empty'
        
        Returns:
            Character(s) to display
        """
        return getattr(self, element, ' ')
    
    def get_color_attr(self, element: str, colors_available: bool = True) -> int:
        """
        Get curses color attribute for a game element.
        
        Args:
            element: One of 'wall', 'player', 'player_on_goal', 'box',
                    'box_on_goal', 'goal', 'empty', 'hud', 'message', 
                    'win', 'border'
            colors_available: Whether colors are available
        
        Returns:
            Curses attribute (color pair + formatting)
        """
        if not colors_available:
            return 0
        
        color_map = {
            'wall': curses.color_pair(self.color_wall) | curses.A_BOLD,
            'player': curses.color_pair(self.color_player) | curses.A_BOLD,
            'player_on_goal': curses.color_pair(self.color_player_on_goal) | curses.A_BOLD,
            'box': curses.color_pair(self.color_box) | curses.A_BOLD,
            'box_on_goal': curses.color_pair(self.color_box_on_goal) | curses.A_BOLD,
            'goal': curses.color_pair(self.color_goal),
            'empty': 0,
            'hud': curses.color_pair(self.color_hud),
            'message': curses.color_pair(self.color_message),
            'win': curses.color_pair(self.color_win) | curses.A_BOLD,
            'border': curses.color_pair(self.color_border),
        }
        
        return color_map.get(element, 0)


class NeonTheme(Theme):
    """Neon cyberpunk theme with vibrant colors and double-line borders."""
    
    def __init__(self):
        super().__init__()
        # Character mappings - Neon style
        self.wall = '█'  # Solid block
        self.player = '@'
        self.player_on_goal = '⊕'
        self.box = '['  # Will display as [█]
        self.box_on_goal = '〚'  # Box on goal variant
        self.goal = '◆'  # Diamond
        
        # Double-line borders
        self.border_top_left = '╔'
        self.border_top_right = '╗'
        self.border_bottom_left = '╚'
        self.border_bottom_right = '╝'
        self.border_horizontal = '═'
        self.border_vertical = '║'
    
    def init_colors(self):
        """Initialize neon color scheme."""
        if not curses.has_colors():
            return False
        
        try:
            curses.start_color()
            curses.use_default_colors()
            
            # Neon colors: magenta walls, cyan boxes, yellow goals, green player
            curses.init_pair(self.color_wall, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            curses.init_pair(self.color_player, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_box, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(self.color_goal, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(self.color_box_on_goal, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(self.color_player_on_goal, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_hud, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(self.color_message, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            curses.init_pair(self.color_win, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_border, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            
            return True
        except:
            return False
    
    def get_char(self, element: str) -> str:
        """Override to add brackets around boxes."""
        if element == 'box':
            return '[█]'
        elif element == 'box_on_goal':
            return '〚█〛'
        return super().get_char(element)


class RetroTheme(Theme):
    """Retro green-on-black terminal theme (Matrix style)."""
    
    def __init__(self):
        super().__init__()
        # Character mappings - Retro ASCII style
        self.wall = '▓'  # Dense hatch pattern
        self.player = '@'
        self.player_on_goal = '⊕'
        self.box = '□'
        self.box_on_goal = '■'  # Filled square on goal
        self.goal = '·'  # Small dot
        
        # Simple borders
        self.border_top_left = '+'
        self.border_top_right = '+'
        self.border_bottom_left = '+'
        self.border_bottom_right = '+'
        self.border_horizontal = '-'
        self.border_vertical = '|'
    
    def init_colors(self):
        """Initialize retro green-on-black color scheme."""
        if not curses.has_colors():
            return False
        
        try:
            curses.start_color()
            curses.use_default_colors()
            
            # Everything green on black (Matrix style)
            curses.init_pair(self.color_wall, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_player, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_box, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_goal, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_box_on_goal, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_player_on_goal, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_hud, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_message, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_win, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_border, curses.COLOR_GREEN, curses.COLOR_BLACK)
            
            return True
        except:
            return False
    
    def get_color_attr(self, element: str, colors_available: bool = True) -> int:
        """All elements are bold green."""
        if not colors_available:
            return 0
        
        # Everything gets bold green
        return curses.color_pair(self.color_wall) | curses.A_BOLD


class EmojiTheme(Theme):
    """Fun emoji-based theme with 2-character wide cells."""
    
    def __init__(self):
        super().__init__()
        # Emoji character mappings (2 chars wide in terminals)
        self.wall = '🧱'
        self.player = '🏃'
        self.player_on_goal = '🎯'  # Player on goal
        self.box = '📦'
        self.box_on_goal = '✅'  # Checked box on goal
        self.goal = '⭐'
        self.empty = '  '  # Two spaces for double-width
        
        # Ice and teleporter for future expansion
        self.ice = '🧊'
        self.teleporter = '🌀'
        
        # Borders remain single-width ASCII
        self.border_top_left = '┌'
        self.border_top_right = '┐'
        self.border_bottom_left = '└'
        self.border_bottom_right = '┘'
        self.border_horizontal = '─'
        self.border_vertical = '│'
        
        # Double-width cells
        self.cell_width = 2
    
    def init_colors(self):
        """Initialize emoji theme colors (colorful!)."""
        if not curses.has_colors():
            return False
        
        try:
            curses.start_color()
            curses.use_default_colors()
            
            # Colorful theme
            curses.init_pair(self.color_wall, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(self.color_player, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_box, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(self.color_goal, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(self.color_box_on_goal, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_player_on_goal, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(self.color_hud, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(self.color_message, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            curses.init_pair(self.color_win, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(self.color_border, curses.COLOR_BLUE, curses.COLOR_BLACK)
            
            return True
        except:
            return False


# Theme registry
THEMES: Dict[ThemeType, type] = {
    ThemeType.DEFAULT: Theme,
    ThemeType.NEON: NeonTheme,
    ThemeType.RETRO: RetroTheme,
    ThemeType.EMOJI: EmojiTheme,
}


def get_theme(theme_type: ThemeType) -> Theme:
    """
    Get a theme instance by type.
    
    Args:
        theme_type: The desired theme
    
    Returns:
        Theme instance
    """
    theme_class = THEMES.get(theme_type, Theme)
    return theme_class()
