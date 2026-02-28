"""Tests for the replay system."""

import tempfile
from pathlib import Path
from gridshift.replay import ReplayRecorder, replay
from gridshift.models import Direction, GameState, Tile, Position
from gridshift.engine import move


def create_simple_state():
    """Create a minimal game state for testing."""
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.EMPTY, Tile.WALL],
        [Tile.WALL, Tile.WALL, Tile.WALL],
    ]
    player_pos = Position(1, 1)
    box_positions = {Position(1, 2)}
    goal_positions = {Position(1, 3)}
    return GameState(
        grid=grid,
        player_pos=player_pos,
        box_positions=box_positions,
        goal_positions=goal_positions,
        width=3,
        height=3
    )


def test_record_and_get_log():
    """Test recording moves and retrieving the log."""
    recorder = ReplayRecorder()
    
    assert recorder.get_log() == []
    
    recorder.record(Direction.UP)
    recorder.record(Direction.RIGHT)
    recorder.record(Direction.DOWN)
    
    log = recorder.get_log()
    assert log == [Direction.UP, Direction.RIGHT, Direction.DOWN]
    
    # Verify it returns a copy
    log.append(Direction.LEFT)
    assert recorder.get_log() == [Direction.UP, Direction.RIGHT, Direction.DOWN]


def test_clear():
    """Test clearing the replay log."""
    recorder = ReplayRecorder()
    
    recorder.record(Direction.UP)
    recorder.record(Direction.DOWN)
    assert len(recorder.get_log()) == 2
    
    recorder.clear()
    assert recorder.get_log() == []


def test_save_and_load():
    """Test saving and loading replay logs to/from files."""
    recorder = ReplayRecorder()
    recorder.record(Direction.UP)
    recorder.record(Direction.RIGHT)
    recorder.record(Direction.DOWN)
    recorder.record(Direction.LEFT)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        filepath = f.name
    
    try:
        recorder.save(filepath)
        
        loaded = recorder.load(filepath)
        assert loaded == [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
    finally:
        Path(filepath).unlink()


def test_load_invalid_direction_raises_error():
    """Test that loading a file with invalid direction names raises ValueError."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("UP\n")
        f.write("INVALID\n")
        f.write("DOWN\n")
        filepath = f.name
    
    try:
        recorder = ReplayRecorder()
        try:
            recorder.load(filepath)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "INVALID" in str(e)
    finally:
        Path(filepath).unlink()


def test_load_nonexistent_file_raises_error():
    """Test that loading a nonexistent file raises FileNotFoundError."""
    recorder = ReplayRecorder()
    try:
        recorder.load("/nonexistent/path/to/file.txt")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass


def test_replay_empty_moves():
    """Test replaying with no moves returns only the initial state."""
    state = create_simple_state()
    moves = []
    
    states = replay(state, moves)
    
    assert len(states) == 1
    assert states[0] == state


def test_replay_valid_moves():
    """Test replaying a sequence of valid moves."""
    # Create a simple level with room to move (no boxes in the way)
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.EMPTY, Tile.EMPTY, Tile.EMPTY, Tile.WALL],
        [Tile.WALL, Tile.EMPTY, Tile.EMPTY, Tile.EMPTY, Tile.WALL],
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
    ]
    initial_state = GameState(
        grid=grid,
        player_pos=Position(1, 1),
        box_positions={Position(2, 3)},  # Box out of the way
        goal_positions={Position(1, 3)},
        width=5,
        height=4
    )
    
    moves = [Direction.RIGHT, Direction.DOWN, Direction.LEFT]
    states = replay(initial_state, moves)
    
    # Should have initial state + 3 move states
    assert len(states) == 4
    
    # Verify player positions at each step
    assert states[0].player_pos == Position(1, 1)
    assert states[1].player_pos == Position(1, 2)
    assert states[2].player_pos == Position(2, 2)
    assert states[3].player_pos == Position(2, 1)


def test_replay_with_blocked_moves():
    """Test that replay handles blocked moves correctly (state unchanged)."""
    # Create a level where player is surrounded
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.EMPTY, Tile.WALL],
        [Tile.WALL, Tile.WALL, Tile.WALL],
    ]
    initial_state = GameState(
        grid=grid,
        player_pos=Position(1, 1),
        box_positions=set(),
        goal_positions={Position(2, 2)},
        width=3,
        height=3
    )
    
    # Try to move into walls
    moves = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
    states = replay(initial_state, moves)
    
    # Should have 5 states (initial + 4 blocked attempts)
    assert len(states) == 5
    
    # Player should never move
    for state in states:
        assert state.player_pos == Position(1, 1)


def test_replay_determinism():
    """Test that replaying the same moves always produces identical results."""
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.EMPTY, Tile.EMPTY, Tile.WALL],
        [Tile.WALL, Tile.EMPTY, Tile.EMPTY, Tile.WALL],
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
    ]
    initial_state = GameState(
        grid=grid,
        player_pos=Position(1, 1),
        box_positions={Position(2, 2)},
        goal_positions={Position(1, 2)},
        width=4,
        height=4
    )
    
    moves = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
    
    # Run replay twice
    states1 = replay(initial_state, moves)
    states2 = replay(initial_state, moves)
    
    # Should produce identical results
    assert len(states1) == len(states2)
    for s1, s2 in zip(states1, states2):
        assert s1.player_pos == s2.player_pos
        assert s1.box_positions == s2.box_positions
        assert s1.width == s2.width
        assert s1.height == s2.height


def test_replay_matches_manual_play():
    """Test that replay produces the same final state as manually applying moves."""
    grid = [
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
        [Tile.WALL, Tile.EMPTY, Tile.EMPTY, Tile.WALL],
        [Tile.WALL, Tile.EMPTY, Tile.EMPTY, Tile.WALL],
        [Tile.WALL, Tile.WALL, Tile.WALL, Tile.WALL],
    ]
    initial_state = GameState(
        grid=grid,
        player_pos=Position(1, 1),
        box_positions={Position(2, 1)},
        goal_positions={Position(2, 2)},
        width=4,
        height=4
    )
    
    moves = [Direction.DOWN, Direction.RIGHT]
    
    # Apply moves manually
    manual_state = initial_state
    for direction in moves:
        manual_state, _ = move(manual_state, direction)
    
    # Apply moves via replay
    replay_states = replay(initial_state, moves)
    replay_final = replay_states[-1]
    
    # Final states should match
    assert manual_state.player_pos == replay_final.player_pos
    assert manual_state.box_positions == replay_final.box_positions
