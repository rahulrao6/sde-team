"""Replay system for GridShift game - logs and replays move sequences."""

from typing import List
from gridshift.models import Direction, GameState
from gridshift.engine import move


class ReplayRecorder:
    """Records and manages move sequences for deterministic replay."""
    
    def __init__(self):
        """Initialize empty move log."""
        self._log: List[Direction] = []
    
    def record(self, direction: Direction) -> None:
        """
        Append a move to the replay log.
        
        Args:
            direction: The direction that was moved
        """
        self._log.append(direction)
    
    def get_log(self) -> List[Direction]:
        """
        Return the complete move sequence.
        
        Returns:
            List of Direction enums representing all recorded moves
        """
        return self._log.copy()
    
    def clear(self) -> None:
        """Reset the move log, removing all recorded moves."""
        self._log.clear()
    
    def save(self, filepath: str) -> None:
        """
        Write the move log to a file (one direction per line).
        
        Args:
            filepath: Path to the output file
        """
        with open(filepath, 'w') as f:
            for direction in self._log:
                f.write(f"{direction.name}\n")
    
    def load(self, filepath: str) -> List[Direction]:
        """
        Read a move log from a file.
        
        Args:
            filepath: Path to the input file
            
        Returns:
            List of Direction enums loaded from the file
            
        Raises:
            ValueError: If file contains invalid direction names
            FileNotFoundError: If file doesn't exist
        """
        directions = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        directions.append(Direction[line])
                    except KeyError:
                        raise ValueError(f"Invalid direction name in replay file: {line!r}")
        return directions


def replay(initial_state: GameState, moves: List[Direction]) -> List[GameState]:
    """
    Apply a sequence of moves to an initial state and return all intermediate states.
    
    This function is deterministic - given the same initial state and move sequence,
    it will always produce the same sequence of resulting states.
    
    Args:
        initial_state: Starting game state
        moves: Sequence of directions to apply
        
    Returns:
        List of GameState objects representing the state after each move.
        Includes the initial state as the first element.
        Blocked moves still appear in the sequence (state unchanged).
    """
    states = [initial_state]
    current_state = initial_state
    
    for direction in moves:
        new_state, _ = move(current_state, direction)
        current_state = new_state
        states.append(current_state)
    
    return states
