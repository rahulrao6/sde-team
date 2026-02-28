"""Terminal rendering using curses for GridShift game."""

import curses
from gridshift.models import GameState, Tile, Position


class Renderer:
    """Handles curses-based terminal rendering of the game."""
    
    # Color pair constants
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
    
    def __init__(self, stdscr):
        """
        Initialize the renderer with a curses window.
        
        Args:
            stdscr: The curses standard screen object
        """
        self.stdscr = stdscr
        curses.curs_set(0)  # Hide cursor
        self.stdscr.clear()
        
        # Initialize colors if supported
        self.colors_available = False
        if curses.has_colors():
            try:
                curses.start_color()
                curses.use_default_colors()
                
                # Define color pairs
                curses.init_pair(self.COLOR_WALL, curses.COLOR_WHITE, curses.COLOR_BLACK)
                curses.init_pair(self.COLOR_PLAYER, curses.COLOR_YELLOW, curses.COLOR_BLACK)
                curses.init_pair(self.COLOR_BOX, curses.COLOR_CYAN, curses.COLOR_BLACK)
                curses.init_pair(self.COLOR_GOAL, curses.COLOR_GREEN, curses.COLOR_BLACK)
                curses.init_pair(self.COLOR_BOX_ON_GOAL, curses.COLOR_GREEN, curses.COLOR_BLACK)
                curses.init_pair(self.COLOR_PLAYER_ON_GOAL, curses.COLOR_YELLOW, curses.COLOR_BLACK)
                curses.init_pair(self.COLOR_HUD, curses.COLOR_CYAN, curses.COLOR_BLACK)
                curses.init_pair(self.COLOR_MESSAGE, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
                curses.init_pair(self.COLOR_WIN, curses.COLOR_GREEN, curses.COLOR_BLACK)
                curses.init_pair(self.COLOR_BORDER, curses.COLOR_BLUE, curses.COLOR_BLACK)
                
                self.colors_available = True
            except:
                # Color initialization failed, continue without colors
                self.colors_available = False
    
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
        grid_width = state.width + 4  # Grid + border
        grid_height = state.height + 4  # Grid + border + spacing
        
        # Center horizontally, keep some padding at top
        offset_x = max(0, (max_x - grid_width) // 2)
        offset_y = 2
        
        # Draw title banner
        title = "═══ GRIDSHIFT ═══"
        title_x = max(0, (max_x - len(title)) // 2)
        self._safe_addstr(0, title_x, title, 
                         curses.color_pair(self.COLOR_HUD) | curses.A_BOLD if self.colors_available else curses.A_BOLD)
        
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
                         curses.color_pair(self.COLOR_HUD) if self.colors_available else 0)
        
        # Draw status message with appropriate color
        if message:
            msg_row = hud_row + 1
            msg_x = max(0, (max_x - len(message)) // 2)
            is_win = "Complete" in message or "🎉" in message
            color_attr = curses.color_pair(self.COLOR_WIN) | curses.A_BOLD if is_win and self.colors_available else curses.color_pair(self.COLOR_MESSAGE) if self.colors_available else 0
            self._safe_addstr(msg_row, msg_x, message, color_attr)
        
        # Draw game grid with border
        grid_start_row = hud_row + 3
        
        # Draw top border
        top_border = "┌" + "─" * state.width + "┐"
        self._safe_addstr(grid_start_row, offset_x, top_border,
                         curses.color_pair(self.COLOR_BORDER) if self.colors_available else 0)
        
        # Draw grid rows with side borders
        for row_idx, row in enumerate(state.grid):
            # Left border
            self._safe_addstr(grid_start_row + row_idx + 1, offset_x, "│",
                             curses.color_pair(self.COLOR_BORDER) if self.colors_available else 0)
            
            # Grid content
            for col_idx, tile in enumerate(row):
                pos = Position(row_idx, col_idx)
                char = self._get_display_char(state, pos, tile)
                color_attr = self._get_color_for_char(char, state, pos)
                self._safe_addstr(grid_start_row + row_idx + 1, offset_x + col_idx + 1, char, color_attr)
            
            # Right border
            self._safe_addstr(grid_start_row + row_idx + 1, offset_x + state.width + 1, "│",
                             curses.color_pair(self.COLOR_BORDER) if self.colors_available else 0)
        
        # Draw bottom border
        bottom_border = "└" + "─" * state.width + "┘"
        self._safe_addstr(grid_start_row + state.height + 1, offset_x, bottom_border,
                         curses.color_pair(self.COLOR_BORDER) if self.colors_available else 0)
        
        # Draw controls help at bottom
        controls_row = grid_start_row + state.height + 3
        controls = "Controls: WASD/Arrows=Move | R=Reset | Z=Undo | Q=Quit"
        controls_x = max(0, (max_x - len(controls)) // 2)
        self._safe_addstr(controls_row, controls_x, controls, curses.A_DIM)
        
        # Draw legend
        legend_row = controls_row + 1
        legend_items = [
            ("@", "Player", self.COLOR_PLAYER),
            ("$", "Box", self.COLOR_BOX),
            (".", "Goal", self.COLOR_GOAL),
            ("*", "Box on Goal", self.COLOR_BOX_ON_GOAL)
        ]
        legend_parts = []
        for char, desc, _ in legend_items:
            legend_parts.append(f"{char}={desc}")
        legend_line = "  ".join(legend_parts)
        legend_x = max(0, (max_x - len(legend_line)) // 2)
        
        # Draw legend with colors if available
        if self.colors_available:
            current_x = legend_x
            for i, (char, desc, color) in enumerate(legend_items):
                part = f"{char}={desc}"
                self._safe_addstr(legend_row, current_x, char, curses.color_pair(color) | curses.A_BOLD)
                self._safe_addstr(legend_row, current_x + 1, f"={desc}", curses.A_DIM)
                current_x += len(part)
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
            char: Character being rendered
            state: Current game state
            pos: Position of the character
            
        Returns:
            Curses color pair attribute
        """
        if not self.colors_available:
            return 0
        
        if char == '#':
            return curses.color_pair(self.COLOR_WALL) | curses.A_BOLD
        elif char == '@':
            return curses.color_pair(self.COLOR_PLAYER) | curses.A_BOLD
        elif char == '+':  # Player on goal
            return curses.color_pair(self.COLOR_PLAYER_ON_GOAL) | curses.A_BOLD
        elif char == '$':
            return curses.color_pair(self.COLOR_BOX) | curses.A_BOLD
        elif char == '*':  # Box on goal
            return curses.color_pair(self.COLOR_BOX_ON_GOAL) | curses.A_BOLD
        elif char == '.':
            return curses.color_pair(self.COLOR_GOAL)
        else:
            return 0
    
    def _get_display_char(self, state: GameState, pos: Position, tile: Tile) -> str:
        """
        Determine the character to display for a given position.
        
        Handles overlays: player-on-goal, box-on-goal.
        
        Args:
            state: Current game state
            pos: Position to check
            tile: Base tile at this position
            
        Returns:
            Single character to render
        """
        # Check if player is on a goal
        if pos == state.player_pos and pos in state.goal_positions:
            return '+'
        
        # Check if a box is on a goal
        if pos in state.box_positions and pos in state.goal_positions:
            return '*'
        
        # Check if player is here (not on goal)
        if pos == state.player_pos:
            return '@'
        
        # Check if a box is here (not on goal)
        if pos in state.box_positions:
            return '$'
        
        # Return the base tile
        return tile.value
