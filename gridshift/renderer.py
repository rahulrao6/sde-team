"""Terminal rendering using curses for GridShift game."""

import curses
from typing import Optional
from .models import GameState, Tile, Position


class Renderer:
    """Curses-based terminal renderer for GridShift."""
    
    def __init__(self, stdscr):
        """Initialize the renderer with a curses window.
        
        Args:
            stdscr: Curses standard screen object
        """
        self.stdscr = stdscr
        curses.curs_set(0)  # Hide cursor
        self.stdscr.clear()
        
    def render(self, state: GameState, move_count: int, message: str = "", 
               undo_depth: int = 0, level_name: str = "Level") -> None:
        """Render the game state to the terminal.
        
        Args:
            state: Current game state
            move_count: Number of moves made
            message: Status message to display
            undo_depth: Number of states in undo stack
            level_name: Name of current level
        """
        self.stdscr.clear()
        
        # Render HUD (header)
        self._render_hud(level_name, move_count, undo_depth, message)
        
        # Render game grid (starting at row 2 to leave space for HUD)
        self._render_grid(state, start_row=2)
        
        # Render controls help bar at bottom
        self._render_controls(state.height + 3)
        
        self.stdscr.refresh()
    
    def _render_hud(self, level_name: str, move_count: int, 
                    undo_depth: int, message: str) -> None:
        """Render the HUD (header) information."""
        hud_line = f"{level_name} | Moves: {move_count} | Undo: {undo_depth}"
        self.stdscr.addstr(0, 0, hud_line)
        
        if message:
            self.stdscr.addstr(1, 0, message)
    
    def _render_grid(self, state: GameState, start_row: int) -> None:
        """Render the game grid.
        
        Display rules:
        - walls: #
        - player: @
        - boxes: $
        - goals: .
        - box-on-goal: *
        - player-on-goal: +
        - empty: space
        """
        for row in range(state.height):
            for col in range(state.width):
                pos = Position(row, col)
                char = self._get_display_char(state, pos)
                
                try:
                    self.stdscr.addch(start_row + row, col, char)
                except curses.error:
                    # Ignore errors from writing to bottom-right corner
                    pass
    
    def _get_display_char(self, state: GameState, pos: Position) -> str:
        """Get the display character for a position.
        
        Priority order:
        1. Player (@ or + if on goal)
        2. Box ($ or * if on goal)
        3. Goal (.)
        4. Wall (#)
        5. Empty (space)
        """
        # Check if player is at this position
        if pos == state.player_pos:
            if pos in state.goal_positions:
                return '+'  # Player on goal
            return '@'  # Player
        
        # Check if box is at this position
        if pos in state.box_positions:
            if pos in state.goal_positions:
                return '*'  # Box on goal
            return '$'  # Box
        
        # Check grid tile
        tile = state.grid[pos.row][pos.col]
        return tile.value
    
    def _render_controls(self, row: int) -> None:
        """Render the controls help bar."""
        controls = "Controls: WASD/Arrows=Move | R=Reset | Z=Undo | Q=Quit"
        try:
            self.stdscr.addstr(row, 0, controls)
        except curses.error:
            # Ignore errors if terminal is too small
            pass
