"""Undo system for GridShift game using state snapshots."""

from typing import Optional
from gridshift.models import GameState


class UndoManager:
    """Manages undo history via a stack of GameState snapshots."""
    
    def __init__(self):
        """Initialize empty undo stack."""
        self._stack: list[GameState] = []
    
    def push(self, state: GameState) -> None:
        """
        Save a state snapshot to the undo stack.
        
        Args:
            state: GameState to save (will be cloned for independence)
        """
        self._stack.append(state.clone())
    
    def pop(self) -> Optional[GameState]:
        """
        Restore and return the previous state from the stack.
        
        Returns:
            Previous GameState if stack is not empty, None otherwise
        """
        if not self._stack:
            return None
        return self._stack.pop()
    
    def clear(self) -> None:
        """Reset the undo history, removing all saved states."""
        self._stack.clear()
    
    @property
    def depth(self) -> int:
        """Return the number of states in the undo stack."""
        return len(self._stack)
