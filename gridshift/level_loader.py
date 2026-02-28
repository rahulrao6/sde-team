"""Level loading and validation for GridShift."""
from typing import Set
from gridshift.models import Tile, Position, GameState


def load_level(filepath: str) -> GameState:
    """
    Load a level from a .txt file.
    
    Args:
        filepath: Path to the level file
        
    Returns:
        GameState object representing the loaded level
        
    Raises:
        ValueError: If the level is invalid
        FileNotFoundError: If the file doesn't exist
    """
    with open(filepath, 'r') as f:
        text = f.read()
    return parse_level(text)


def parse_level(text: str) -> GameState:
    """
    Parse a level from a string.
    
    Args:
        text: Level text with # (walls), @ (player), $ (boxes), . (goals), and spaces
        
    Returns:
        GameState object representing the parsed level
        
    Raises:
        ValueError: If the level is invalid (missing player, no boxes, no goals, 
                   multiple players, or invalid characters)
    """
    lines = text.splitlines()
    
    if not lines:
        raise ValueError("Level is empty")
    
    # Find maximum line length to handle ragged lines
    max_width = max(len(line) for line in lines) if lines else 0
    
    # Pad all lines to the same width
    padded_lines = [line.ljust(max_width) for line in lines]
    
    # Track positions
    player_pos = None
    box_positions: Set[Position] = set()
    goal_positions: Set[Position] = set()
    grid = []
    
    # Valid characters
    valid_chars = {'#', '@', '$', '.', ' '}
    
    # Parse the grid
    for row_idx, line in enumerate(padded_lines):
        grid_row = []
        for col_idx, char in enumerate(line):
            # Validate character
            if char not in valid_chars:
                raise ValueError(f"Invalid character '{char}' at row {row_idx}, col {col_idx}")
            
            pos = Position(row_idx, col_idx)
            
            # Track special positions
            if char == '@':
                if player_pos is not None:
                    raise ValueError(f"Multiple players found: at {player_pos} and {pos}")
                player_pos = pos
                grid_row.append(Tile.PLAYER)
            elif char == '$':
                box_positions.add(pos)
                grid_row.append(Tile.BOX)
            elif char == '.':
                goal_positions.add(pos)
                grid_row.append(Tile.GOAL)
            elif char == '#':
                grid_row.append(Tile.WALL)
            else:  # space
                grid_row.append(Tile.EMPTY)
        
        grid.append(grid_row)
    
    # Validate required elements
    if player_pos is None:
        raise ValueError("No player (@) found in level")
    
    if not box_positions:
        raise ValueError("No boxes ($) found in level")
    
    if not goal_positions:
        raise ValueError("No goals (.) found in level")
    
    height = len(grid)
    width = max_width
    
    return GameState(
        grid=grid,
        player_pos=player_pos,
        box_positions=box_positions,
        goal_positions=goal_positions,
        width=width,
        height=height
    )
