"""Terminal rendering using curses for GridShift game."""

import curses
from gridshift.models import GameState, Tile, Position


class Renderer:
    """Handles curses-based terminal rendering of the game."""
    
    def __init__(self, stdscr):
        """
        Initialize the renderer with a curses window.
        
        Args:
            stdscr: The curses standard screen object
        """
        self.stdscr = stdscr
        curses.curs_set(0)  # Hide cursor
        self.stdscr.clear()
    
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
        
        # Draw HUD at top
        hud_row = 0
        self.stdscr.addstr(hud_row, 0, f"Level: {level_name}")
        self.stdscr.addstr(hud_row, 30, f"Moves: {move_count}")
        self.stdscr.addstr(hud_row, 50, f"Undo: {undo_depth}")
        
        # Draw status message
        if message:
            self.stdscr.addstr(hud_row + 1, 0, message)
        
        # Draw game grid
        grid_start_row = hud_row + 3
        for row_idx, row in enumerate(state.grid):
            for col_idx, tile in enumerate(row):
                pos = Position(row_idx, col_idx)
                char = self._get_display_char(state, pos, tile)
                try:
                    self.stdscr.addstr(grid_start_row + row_idx, col_idx, char)
                except curses.error:
                    # Ignore errors from writing to bottom-right corner
                    pass
        
        # Draw controls help at bottom
        controls_row = grid_start_row + state.height + 2
        controls = "Controls: WASD/Arrows=Move | R=Reset | Z=Undo | Q=Quit"
        try:
            self.stdscr.addstr(controls_row, 0, controls)
        except curses.error:
            pass
        
        self.stdscr.refresh()
    
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
