"""Movement and collision engine for GridShift."""

from gridshift.models import GameState, Direction, Position, Tile


def _get_next_position(pos: Position, direction: Direction) -> Position:
    """Calculate the next position given a direction."""
    if direction == Direction.UP:
        return Position(pos.row - 1, pos.col)
    elif direction == Direction.DOWN:
        return Position(pos.row + 1, pos.col)
    elif direction == Direction.LEFT:
        return Position(pos.row, pos.col - 1)
    elif direction == Direction.RIGHT:
        return Position(pos.row, pos.col + 1)
    else:
        raise ValueError(f"Invalid direction: {direction}")


def _is_out_of_bounds(pos: Position, state: GameState) -> bool:
    """Check if position is outside grid boundaries."""
    return (pos.row < 0 or pos.row >= state.height or
            pos.col < 0 or pos.col >= state.width)


def _get_tile(pos: Position, state: GameState) -> Tile:
    """Get the tile at a position. Returns WALL if out of bounds."""
    if _is_out_of_bounds(pos, state):
        return Tile.WALL
    return state.grid[pos.row][pos.col]


def move(state: GameState, direction: Direction) -> tuple[GameState, bool]:
    """
    Attempt to move the player in the given direction.
    
    Returns:
        tuple[GameState, bool]: (new_state, moved) where moved=True if movement succeeded
    
    Rules:
        - Empty cell → player moves
        - Wall → blocked (return original state, False)
        - Box with empty beyond → push box, move player (return new state, True)
        - Box with wall/box beyond → blocked (return original state, False)
        - Edge of grid treated as wall
        - Player can walk on/off goals freely
        - Boxes can be pushed onto goals
    """
    # Calculate target position
    target_pos = _get_next_position(state.player_pos, direction)
    
    # Check if target is out of bounds (treat as wall)
    if _is_out_of_bounds(target_pos, state):
        return (state, False)
    
    # Check what's at the target position
    target_tile = _get_tile(target_pos, state)
    
    # Wall collision - blocked
    if target_tile == Tile.WALL:
        return (state, False)
    
    # Check if there's a box at target position
    is_box_at_target = target_pos in state.box_positions
    
    if is_box_at_target:
        # Calculate position beyond the box
        beyond_pos = _get_next_position(target_pos, direction)
        
        # Check if beyond position is valid
        if _is_out_of_bounds(beyond_pos, state):
            return (state, False)
        
        beyond_tile = _get_tile(beyond_pos, state)
        
        # Can't push box into wall
        if beyond_tile == Tile.WALL:
            return (state, False)
        
        # Can't push box into another box
        if beyond_pos in state.box_positions:
            return (state, False)
        
        # Valid push - create new state with box moved
        new_state = state.clone()
        
        # Remove box from old position, add to new position
        new_state.box_positions.remove(target_pos)
        new_state.box_positions.add(beyond_pos)
        
        # Update grid - remove box from target
        if target_pos in state.goal_positions:
            new_state.grid[target_pos.row][target_pos.col] = Tile.GOAL
        else:
            new_state.grid[target_pos.row][target_pos.col] = Tile.EMPTY
        
        # Add box to beyond position
        new_state.grid[beyond_pos.row][beyond_pos.col] = Tile.BOX
        
        # Move player to target position
        # Clear old player position
        if state.player_pos in state.goal_positions:
            new_state.grid[state.player_pos.row][state.player_pos.col] = Tile.GOAL
        else:
            new_state.grid[state.player_pos.row][state.player_pos.col] = Tile.EMPTY
        
        # Place player at target
        new_state.grid[target_pos.row][target_pos.col] = Tile.PLAYER
        new_state.player_pos = target_pos
        
        return (new_state, True)
    
    else:
        # No box at target - simple move
        # Target can be EMPTY or GOAL (player can walk on goals)
        new_state = state.clone()
        
        # Clear old player position
        if state.player_pos in state.goal_positions:
            new_state.grid[state.player_pos.row][state.player_pos.col] = Tile.GOAL
        else:
            new_state.grid[state.player_pos.row][state.player_pos.col] = Tile.EMPTY
        
        # Place player at target
        new_state.grid[target_pos.row][target_pos.col] = Tile.PLAYER
        new_state.player_pos = target_pos
        
        return (new_state, True)
