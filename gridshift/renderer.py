"""Terminal rendering using curses for GridShift game."""

import curses
from gridshift.models import GameState, Tile, Position
from gridshift.themes import Theme, ThemeType, get_theme


class Renderer:
    """Handles curses-based terminal rendering of the game."""
    
    # Color pair constants (kept for backward compatibility)
    COLOR_WALL = 1
    COLOR_PLAYER = 2
    COLOR_BOX = 3
    COLOR_GOAL = 4
    COLOR_BOX_ON_GOAL = 5
    COLOR_PLAYER_ON_GOAL = 6
    COLOR_HUD = 7
    COLOR_MESSAGE = 8
    COLOR_WIN = 9
    COLOR_BORDER = 10
    
    def __init__(self, stdscr, theme_type: ThemeType = ThemeType.DEFAULT):
        """
        Initialize the renderer with a curses window and theme.
        
        Args:
            stdscr: The curses standard screen object
            theme_type: Visual theme to use
        """
        self.stdscr = stdscr
        curses.curs_set(0)  # Hide cursor
        self.stdscr.clear()
        
        # Load theme
        self.theme = get_theme(theme_type)
        
        # Initialize colors if supported
        self.colors_available = self.theme.init_colors()
    
    def render(self, state: GameState, move_count: int, message: str = "", 
               level_name: str = "", undo_depth: int = 0) -> None:
        """
        Draw the complete game screen: grid, HUD, and controls.
        
        Args:
            state: Current game state to render
            move_count: Number of moves made
            message: Status message to display
            level_name: Name of the current level
            undo_depth: Number of states in undo stack
        """
        self.stdscr.clear()
        
        # Calculate centering offset
        max_y, max_x = self.stdscr.getmaxyx()
        # Account for cell width (1 for ASCII, 2 for emoji)
        grid_width = (state.width * self.theme.cell_width) + 4  # Grid + border
        grid_height = state.height + 4  # Grid + border + spacing
        
        # Center horizontally, keep some padding at top
        offset_x = max(0, (max_x - grid_width) // 2)
        offset_y = 2
        
        # Draw title banner
        title = "═══ GRIDSHIFT ═══"
        title_x = max(0, (max_x - len(title)) // 2)
        self._safe_addstr(0, title_x, title, 
                         self.theme.get_color_attr('hud', self.colors_available) | curses.A_BOLD)
        
        # Draw HUD below title
        hud_row = offset_y
        hud_items = [
            f"Level: {level_name}",
            f"Moves: {move_count}",
            f"Undo: {undo_depth}"
        ]
        hud_line = "  |  ".join(hud_items)
        hud_x = max(0, (max_x - len(hud_line)) // 2)
        self._safe_addstr(hud_row, hud_x, hud_line,
                         self.theme.get_color_attr('hud', self.colors_available))
        
        # Draw status message with appropriate color
        if message:
            msg_row = hud_row + 1
            msg_x = max(0, (max_x - len(message)) // 2)
            is_win = "Complete" in message or "🎉" in message
            color_attr = self.theme.get_color_attr('win' if is_win else 'message', self.colors_available)
            self._safe_addstr(msg_row, msg_x, message, color_attr)
        
        # Draw game grid with border
        grid_start_row = hud_row + 3
        
        # Draw top border using theme characters
        top_border = self.theme.border_top_left + (self.theme.border_horizontal * (state.width * self.theme.cell_width)) + self.theme.border_top_right
        self._safe_addstr(grid_start_row, offset_x, top_border,
                         self.theme.get_color_attr('border', self.colors_available))
        
        # Draw grid rows with side borders
        for row_idx, row in enumerate(state.grid):
            # Left border
            self._safe_addstr(grid_start_row + row_idx + 1, offset_x, self.theme.border_vertical,
                             self.theme.get_color_attr('border', self.colors_available))
            
            # Grid content
            x_pos = offset_x + 1
            for col_idx, tile in enumerate(row):
                pos = Position(row_idx, col_idx)
                char = self._get_display_char(state, pos, tile)
                color_attr = self._get_color_for_char(char, state, pos)
                self._safe_addstr(grid_start_row + row_idx + 1, x_pos, char, color_attr)
                x_pos += self.theme.cell_width
            
            # Right border
            self._safe_addstr(grid_start_row + row_idx + 1, offset_x + (state.width * self.theme.cell_width) + 1, self.theme.border_vertical,
                             self.theme.get_color_attr('border', self.colors_available))
        
        # Draw bottom border using theme characters
        bottom_border = self.theme.border_bottom_left + (self.theme.border_horizontal * (state.width * self.theme.cell_width)) + self.theme.border_bottom_right
        self._safe_addstr(grid_start_row + state.height + 1, offset_x, bottom_border,
                         self.theme.get_color_attr('border', self.colors_available))
        
        # Draw controls help at bottom
        controls_row = grid_start_row + state.height + 3
        controls = "Controls: WASD/Arrows=Move | R=Reset | Z=Undo | Q=Quit"
        controls_x = max(0, (max_x - len(controls)) // 2)
        self._safe_addstr(controls_row, controls_x, controls, curses.A_DIM)
        
        # Draw legend using theme characters
        legend_row = controls_row + 1
        legend_items = [
            (self.theme.get_char('player'), "Player", 'player'),
            (self.theme.get_char('box'), "Box", 'box'),
            (self.theme.get_char('goal'), "Goal", 'goal'),
            (self.theme.get_char('box_on_goal'), "Box on Goal", 'box_on_goal')
        ]
        
        # Build legend string
        legend_parts = []
        for char, desc, _ in legend_items:
            legend_parts.append(f"{char}={desc}")
        legend_line = "  ".join(legend_parts)
        
        # Calculate position (account for potentially wide characters)
        legend_display_width = sum(len(char) + 1 + len(desc) for char, desc, _ in legend_items) + (len(legend_items) - 1) * 2
        legend_x = max(0, (max_x - legend_display_width) // 2)
        
        # Draw legend with colors if available
        if self.colors_available:
            current_x = legend_x
            for i, (char, desc, element) in enumerate(legend_items):
                self._safe_addstr(legend_row, current_x, char, self.theme.get_color_attr(element, True))
                current_x += len(char)
                self._safe_addstr(legend_row, current_x, f"={desc}", curses.A_DIM)
                current_x += 1 + len(desc)
                if i < len(legend_items) - 1:
                    self._safe_addstr(legend_row, current_x, "  ", 0)
                    current_x += 2
        else:
            self._safe_addstr(legend_row, legend_x, legend_line, curses.A_DIM)
        
        self.stdscr.refresh()
    
    def _safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        """
        Safely add string to screen, handling errors from writing to edges.
        
        Args:
            y: Row position
            x: Column position
            text: Text to write
            attr: Curses attributes/color pair
        """
        try:
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            # Ignore errors from writing to bottom-right corner or out of bounds
            pass
    
    def _get_color_for_char(self, char: str, state: GameState, pos: Position) -> int:
        """
        Get the appropriate color attribute for a character.
        
        Args:
            char: Character being rendered (from theme)
            state: Current game state
            pos: Position of the character
            
        Returns:
            Curses color pair attribute
        """
        # Determine element type by checking position and state
        if pos == state.player_pos and pos in state.goal_positions:
            return self.theme.get_color_attr('player_on_goal', self.colors_available)
        elif pos in state.box_positions and pos in state.goal_positions:
            return self.theme.get_color_attr('box_on_goal', self.colors_available)
        elif pos == state.player_pos:
            return self.theme.get_color_attr('player', self.colors_available)
        elif pos in state.box_positions:
            return self.theme.get_color_attr('box', self.colors_available)
        elif pos in state.goal_positions:
            return self.theme.get_color_attr('goal', self.colors_available)
        elif state.grid[pos.row][pos.col] == Tile.WALL:
            return self.theme.get_color_attr('wall', self.colors_available)
        else:
            return self.theme.get_color_attr('empty', self.colors_available)
    
    def _get_display_char(self, state: GameState, pos: Position, tile: Tile) -> str:
        """
        Determine the character to display for a given position using theme.
        
        Handles overlays: player-on-goal, box-on-goal.
        
        Args:
            state: Current game state
            pos: Position to check
            tile: Base tile at this position
            
        Returns:
            Character(s) to render (may be multi-char for emoji theme)
        """
        # Check if player is on a goal
        if pos == state.player_pos and pos in state.goal_positions:
            return self.theme.get_char('player_on_goal')
        
        # Check if a box is on a goal
        if pos in state.box_positions and pos in state.goal_positions:
            return self.theme.get_char('box_on_goal')
        
        # Check if player is here (not on goal)
        if pos == state.player_pos:
            return self.theme.get_char('player')
        
        # Check if a box is here (not on goal)
        if pos in state.box_positions:
            return self.theme.get_char('box')
        
        # Check base tile type
        if tile == Tile.WALL:
            return self.theme.get_char('wall')
        elif tile == Tile.GOAL:
            return self.theme.get_char('goal')
        else:
            return self.theme.get_char('empty')
