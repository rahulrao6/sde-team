"""Debug logging utilities for GridShift game."""

import sys
from typing import List, TextIO, Optional
from gridshift.models import GameState, Direction, Tile


class DebugLogger:
    """Provides debug logging for game state and move history."""
    
    def __init__(self, enabled: bool = False, output: Optional[TextIO] = None):
        """
        Initialize the debug logger.
        
        Args:
            enabled: Whether debug logging is active
            output: File-like object to write to (defaults to stderr)
        """
        self.enabled = enabled
        self.output = output or sys.stderr
    
    def toggle(self) -> None:
        """Toggle debug logging on/off."""
        self.enabled = not self.enabled
    
    def log(self, message: str) -> None:
        """
        Write a debug message if logging is enabled.
        
        Args:
            message: The message to log
        """
        if self.enabled:
            self.output.write(f"[DEBUG] {message}\n")
            self.output.flush()
    
    def dump_state(self, state: GameState) -> None:
        """
        Print the current game state as a text grid.
        
        Args:
            state: The GameState to dump
        """
        if not self.enabled:
            return
        
        self.output.write("[DEBUG] Game State:\n")
        for row in state.grid:
            line = ''.join(tile.value for tile in row)
            self.output.write(f"  {line}\n")
        
        self.output.write(f"  Player: {state.player_pos}\n")
        self.output.write(f"  Boxes: {sorted(state.box_positions, key=lambda p: (p.row, p.col))}\n")
        self.output.write(f"  Goals: {sorted(state.goal_positions, key=lambda p: (p.row, p.col))}\n")
        self.output.flush()
    
    def dump_history(self, moves: List[Direction]) -> None:
        """
        Print a move sequence.
        
        Args:
            moves: List of Direction enums representing the move history
        """
        if not self.enabled:
            return
        
        self.output.write("[DEBUG] Move History:\n")
        if not moves:
            self.output.write("  (no moves)\n")
        else:
            move_str = ' '.join(d.name for d in moves)
            self.output.write(f"  {move_str}\n")
        self.output.write(f"  Total moves: {len(moves)}\n")
        self.output.flush()
