"""Level loader and validator for GridShift."""

from pathlib import Path
from typing import Set
from gridshift.models import GameState, Tile, Position


def parse_level(text: str) -> GameState:
    """
    Parse a level from a text string into a GameState.
    
    Args:
        text: Multi-line string representing the level grid
        
    Returns:
        GameState object representing the parsed level
        
    Raises:
        ValueError: If level is invalid (wrong player count, no boxes/goals, invalid chars)
    """
    if not text.strip():
        raise ValueError("Level text cannot be empty")
    
    lines = text.split('\n')
    # Filter out completely empty lines at start/end but preserve internal structure
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    
    if not lines:
        raise ValueError("Level contains no valid content")
    
    # Determine grid dimensions (handle ragged lines)
    height = len(lines)
    width = max(len(line) for line in lines) if lines else 0
    
    if width == 0 or height == 0:
        raise ValueError("Level must have non-zero dimensions")
    
    # Parse grid and track special positions
    grid = []
    player_pos = None
    box_positions: Set[Position] = set()
    goal_positions: Set[Position] = set()
    
    for row_idx, line in enumerate(lines):
        # Pad line to width if needed (handle ragged lines)
        padded_line = line.ljust(width)
        grid_row = []
        
        for col_idx, char in enumerate(padded_line):
            pos = Position(row_idx, col_idx)
            
            try:
                tile = Tile.from_char(char)
            except ValueError:
                raise ValueError(
                    f"Invalid character '{char}' at row {row_idx}, col {col_idx}. "
                    f"Only '#', '@', '$', '.', and ' ' are allowed."
                )
            
            # Track special positions
            if tile == Tile.PLAYER:
                if player_pos is not None:
                    raise ValueError(
                        f"Multiple players found: at {player_pos} and {pos}. "
                        f"Exactly one player is required."
                    )
                player_pos = pos
                # Player occupies an empty cell in the grid representation
                grid_row.append(Tile.EMPTY)
            elif tile == Tile.BOX:
                box_positions.add(pos)
                # Box occupies an empty cell in the grid representation
                grid_row.append(Tile.EMPTY)
            elif tile == Tile.GOAL:
                goal_positions.add(pos)
                # Goal remains in grid
                grid_row.append(Tile.GOAL)
            else:
                # WALL or EMPTY
                grid_row.append(tile)
        
        grid.append(grid_row)
    
    # Validation
    if player_pos is None:
        raise ValueError("No player ('@') found in level. Exactly one player is required.")
    
    if not box_positions:
        raise ValueError("No boxes ('$') found in level. At least one box is required.")
    
    if not goal_positions:
        raise ValueError("No goals ('.') found in level. At least one goal is required.")
    
    return GameState(
        grid=grid,
        player_pos=player_pos,
        box_positions=box_positions,
        goal_positions=goal_positions,
        width=width,
        height=height
    )


def load_level(filepath: str) -> GameState:
    """
    Load a level from a text file.
    
    Args:
        filepath: Path to the level file
        
    Returns:
        GameState object representing the loaded level
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If level content is invalid
    """
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"Level file not found: {filepath}")
    
    text = path.read_text()
    return parse_level(text)
