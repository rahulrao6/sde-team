"""Game engine for GridShift - movement, collision, and win detection."""

from gridshift.models import GameState


def check_win(state: GameState) -> bool:
    """
    Check if the game is won.
    
    Win condition: Every goal position must have a box on it.
    
    Args:
        state: Current game state
        
    Returns:
        True if all goals have boxes on them, False otherwise
    """
    # Win condition: all goals must have boxes on them
    # This means goal_positions must be a subset of (or equal to) box_positions
    return state.goal_positions.issubset(state.box_positions)
