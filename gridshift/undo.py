"""Undo system for GridShift."""

from typing import Optional
from .models import GameState


class UndoManager:
    """Manages undo/redo via state snapshot stack."""
    
    def __init__(self):
        """Initialize an empty undo manager."""
        self._stack: list[GameState] = []
    
    def push(self, state: GameState) -> None:
        """Save a state snapshot before each move.
        
        Args:
            state: The GameState to save
        """
        self._stack.append(state.clone())
    
    def pop(self) -> Optional[GameState]:
        """Restore the previous state.
        
        Returns:
            The previous GameState, or None if the stack is empty
        """
        if not self._stack:
            return None
        return self._stack.pop()
    
    def clear(self) -> None:
        """Reset undo history."""
        self._stack.clear()
    
    @property
    def depth(self) -> int:
        """Return the number of states in the stack."""
        return len(self._stack)
