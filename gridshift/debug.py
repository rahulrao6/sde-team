"""Debug logging and state inspection utilities."""

import sys
from typing import TextIO
from .models import GameState, Direction, Tile


class DebugLogger:
    """Logger for debugging game state and move history."""
    
    def __init__(self, enabled: bool = False, output: TextIO = sys.stderr):
        """Initialize the debug logger.
        
        Args:
            enabled: Whether debug logging is enabled
            output: Output stream (default: stderr)
        """
        self.enabled = enabled
        self.output = output
    
    def log(self, message: str) -> None:
        """Log a debug message if enabled."""
        if self.enabled:
            self.output.write(f"[DEBUG] {message}\n")
            self.output.flush()
    
    def dump_state(self, state: GameState) -> None:
        """Print the game state as text."""
        if not self.enabled:
            return
        
        self.output.write("\n=== Game State ===\n")
        self.output.write(f"Size: {state.width}x{state.height}\n")
        self.output.write(f"Player: {state.player_pos}\n")
        self.output.write(f"Boxes: {state.box_positions}\n")
        self.output.write(f"Goals: {state.goal_positions}\n")
        self.output.write("\nGrid:\n")
        
        # Render grid with all entities
        for row in range(state.height):
            line = []
            for col in range(state.width):
                from .models import Position
                pos = Position(row, col)
                
                # Player
                if pos == state.player_pos:
                    if pos in state.goal_positions:
                        line.append('+')
                    else:
                        line.append('@')
                # Box
                elif pos in state.box_positions:
                    if pos in state.goal_positions:
                        line.append('*')
                    else:
                        line.append('$')
                # Tile
                else:
                    line.append(state.grid[row][col].value)
            
            self.output.write(''.join(line) + '\n')
        
        self.output.write("==================\n\n")
        self.output.flush()
    
    def dump_history(self, moves: list[Direction]) -> None:
        """Print move sequence."""
        if not self.enabled:
            return
        
        self.output.write("\n=== Move History ===\n")
        self.output.write(f"Total moves: {len(moves)}\n")
        
        if moves:
            move_names = [self._direction_name(d) for d in moves]
            self.output.write("Moves: " + " ".join(move_names) + "\n")
        
        self.output.write("====================\n\n")
        self.output.flush()
    
    def _direction_name(self, direction: Direction) -> str:
        """Get a short name for a direction."""
        return direction.name[0]  # U, D, L, R
