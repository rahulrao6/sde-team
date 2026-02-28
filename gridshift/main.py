"""Main game loop and entry point for GridShift."""

import curses
import sys
import time
import argparse
from pathlib import Path
from typing import Optional

from gridshift.models import Direction, GameState
from gridshift.level_loader import load_level
from gridshift.engine import move, check_win
from gridshift.undo import UndoManager
from gridshift.replay import ReplayRecorder, replay
from gridshift.renderer import Renderer
from gridshift.debug import DebugLogger


class Game:
    """Main game controller."""
    
    def __init__(self, stdscr, level_path: str, debug: bool = False, all_levels: Optional[list[Path]] = None):
        """
        Initialize the game.
        
        Args:
            stdscr: Curses standard screen
            level_path: Path to the level file
            debug: Enable debug logging
            all_levels: Optional list of all available levels for progression
        """
        self.stdscr = stdscr
        self.level_path = level_path
        self.level_name = Path(level_path).stem
        
        # Level progression tracking
        self.all_levels = all_levels or []
        self.current_level_index = self._find_current_level_index()
        
        # Initialize game state
        self.initial_state = load_level(level_path)
        self.state = self.initial_state.clone()
        
        # Initialize subsystems
        self.undo_manager = UndoManager()
        self.replay_recorder = ReplayRecorder()
        self.renderer = Renderer(stdscr)
        self.debug_logger = DebugLogger(enabled=debug)
        
        # Game state tracking
        self.move_count = 0
        self.message = ""
        self.running = True
        self.won = False
        self.load_next_level = False
        
        # Frame timing for 60fps cap
        self.frame_time = 1.0 / 60.0
        
        # Configure curses
        self.stdscr.nodelay(True)  # Non-blocking input
        self.stdscr.timeout(16)  # ~60fps timeout
    
    def _find_current_level_index(self) -> int:
        """Find the index of the current level in all_levels."""
        if not self.all_levels:
            return -1
        current_path = Path(self.level_path)
        for i, level in enumerate(self.all_levels):
            if level.resolve() == current_path.resolve():
                return i
        return -1
    
    def handle_input(self) -> None:
        """Process keyboard input."""
        try:
            key = self.stdscr.getch()
        except:
            return
        
        if key == -1:  # No input
            return
        
        # Handle terminal resize
        if key == curses.KEY_RESIZE:
            self.handle_resize()
            return
        
        # Handle quit
        if key in (ord('q'), ord('Q')):
            self.running = False
            return
        
        # Handle reset
        if key in (ord('r'), ord('R')):
            self.reset_level()
            return
        
        # Handle undo
        if key in (ord('z'), ord('Z')):
            self.undo()
            return
        
        # Handle replay
        if key in (ord('p'), ord('P')):
            self.start_replay()
            return
        
        # Handle next level (when won)
        if key in (ord('n'), ord('N')) and self.won:
            self.next_level()
            return
        
        # Handle movement
        direction = None
        if key in (ord('w'), ord('W'), curses.KEY_UP):
            direction = Direction.UP
        elif key in (ord('s'), ord('S'), curses.KEY_DOWN):
            direction = Direction.DOWN
        elif key in (ord('a'), ord('A'), curses.KEY_LEFT):
            direction = Direction.LEFT
        elif key in (ord('d'), ord('D'), curses.KEY_RIGHT):
            direction = Direction.RIGHT
        
        if direction:
            self.make_move(direction)
    
    def make_move(self, direction: Direction) -> None:
        """
        Attempt to move in the given direction.
        
        Args:
            direction: Direction to move
        """
        if self.won:
            return
        
        # Save state before move for undo
        self.undo_manager.push(self.state)
        
        # Attempt the move
        new_state, moved = move(self.state, direction)
        
        if moved:
            self.state = new_state
            self.move_count += 1
            self.replay_recorder.record(direction)
            self.message = ""
            
            self.debug_logger.log(f"Move {self.move_count}: {direction.name}")
            
            # Check for win
            if check_win(self.state):
                self.won = True
                next_level_msg = " Press N for next level," if self.has_next_level() else ""
                self.message = f"🎉 Level Complete! Solved in {self.move_count} moves!{next_level_msg} R to restart, or Q to quit."
                self.debug_logger.log("LEVEL WON!")
        else:
            # Move was blocked, pop the saved state
            self.undo_manager.pop()
            self.message = "Blocked!"
    
    def undo(self) -> None:
        """Undo the last move."""
        previous_state = self.undo_manager.pop()
        if previous_state:
            self.state = previous_state
            self.move_count -= 1
            if self.move_count < 0:
                self.move_count = 0
            self.message = "Undo"
            self.won = False  # Allow continuing after undo from win state
            self.debug_logger.log(f"Undo to move {self.move_count}")
        else:
            self.message = "Nothing to undo"
    
    def reset_level(self) -> None:
        """Reset the level to initial state."""
        self.state = self.initial_state.clone()
        self.move_count = 0
        self.message = "Level reset"
        self.won = False
        self.undo_manager.clear()
        self.replay_recorder.clear()
        self.debug_logger.log("Level reset")
    
    def has_next_level(self) -> bool:
        """Check if there is a next level available."""
        return (self.all_levels and 
                self.current_level_index >= 0 and 
                self.current_level_index < len(self.all_levels) - 1)
    
    def next_level(self) -> None:
        """Load the next level in the sequence."""
        if not self.has_next_level():
            self.message = "No more levels!"
            return
        
        next_index = self.current_level_index + 1
        next_level_path = str(self.all_levels[next_index])
        
        self.debug_logger.log(f"Loading next level: {next_level_path}")
        
        # Load the new level
        self.level_path = next_level_path
        self.level_name = Path(next_level_path).stem
        self.current_level_index = next_index
        self.initial_state = load_level(next_level_path)
        self.state = self.initial_state.clone()
        
        # Reset game state
        self.move_count = 0
        self.message = f"Level {self.current_level_index + 1}/{len(self.all_levels)}"
        self.won = False
        self.undo_manager.clear()
        self.replay_recorder.clear()
        
        self.debug_logger.log(f"Started level {self.current_level_index + 1}")
        self.debug_logger.dump_state(self.initial_state)
    
    def start_replay(self) -> None:
        """Replay all recorded moves from the beginning."""
        moves = self.replay_recorder.get_log()
        
        if not moves:
            self.message = "No moves to replay"
            return
        
        self.debug_logger.log(f"Starting replay of {len(moves)} moves")
        
        # Reset to initial state
        self.state = self.initial_state.clone()
        self.move_count = 0
        self.won = False
        self.undo_manager.clear()
        
        # Get all states from replay
        states = replay(self.initial_state, moves)
        
        # Animate the replay
        for i, state in enumerate(states[1:], 1):  # Skip initial state
            self.state = state
            self.move_count = i
            self.message = f"Replaying... ({i}/{len(moves)})"
            
            # Check for win
            if check_win(self.state):
                self.won = True
                self.message = f"🎉 Replay Complete! Solved in {self.move_count} moves!"
            
            # Render current frame
            self.render()
            self.stdscr.refresh()
            
            # Delay for visualization (10fps for replay)
            time.sleep(0.1)
        
        # Rebuild undo history by pushing each state
        replay_states = replay(self.initial_state, moves)
        for state in replay_states[:-1]:  # All except final state
            self.undo_manager.push(state)
        
        self.debug_logger.log(f"Replay complete: {self.move_count} moves")
        
        if not self.won:
            self.message = f"Replay complete ({self.move_count} moves)"
    
    def handle_resize(self) -> None:
        """Handle terminal resize events."""
        # Update screen dimensions
        curses.update_lines_cols()
        
        # Get new terminal size
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Check if terminal is too small for the game
        min_width = self.state.width + 10  # Grid + borders + padding
        min_height = self.state.height + 15  # Grid + HUD + controls + legend
        
        if max_x < min_width or max_y < min_height:
            self.message = f"Terminal too small! Need at least {min_width}x{min_height}"
        else:
            # Clear previous resize warning if any
            if "too small" in self.message.lower():
                self.message = ""
        
        # Reinitialize renderer with new screen size
        self.renderer = Renderer(self.stdscr)
        
        # Force a full redraw
        self.stdscr.clear()
        self.render()
        self.stdscr.refresh()
        
        self.debug_logger.log(f"Terminal resized to {max_x}x{max_y}")
    
    def render(self) -> None:
        """Render the current game state."""
        self.renderer.render(
            state=self.state,
            move_count=self.move_count,
            message=self.message,
            level_name=self.level_name,
            undo_depth=self.undo_manager.depth
        )
    
    def run(self) -> None:
        """Main game loop."""
        self.debug_logger.log(f"Starting level: {self.level_name}")
        self.debug_logger.dump_state(self.initial_state)
        
        while self.running:
            frame_start = time.time()
            
            self.handle_input()
            self.render()
            
            # Frame rate limiting
            elapsed = time.time() - frame_start
            sleep_time = self.frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)


def list_levels(levels_dir: Path) -> list[Path]:
    """
    Find all .txt level files in the levels directory.
    
    Args:
        levels_dir: Path to the levels directory
        
    Returns:
        Sorted list of level file paths
    """
    if not levels_dir.exists():
        return []
    return sorted(levels_dir.glob("*.txt"))


def select_level(stdscr, levels: list[Path]) -> Optional[Path]:
    """
    Show a level selection menu.
    
    Args:
        stdscr: Curses standard screen
        levels: List of available level paths
        
    Returns:
        Selected level path, or None if cancelled
    """
    if not levels:
        return None
    
    curses.curs_set(0)
    current = 0
    
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "GridShift - Select Level")
        stdscr.addstr(1, 0, "=" * 40)
        
        for idx, level_path in enumerate(levels):
            prefix = "> " if idx == current else "  "
            stdscr.addstr(3 + idx, 0, f"{prefix}{level_path.name}")
        
        stdscr.addstr(5 + len(levels), 0, "Use arrow keys to select, Enter to play, Q to quit")
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current > 0:
            current -= 1
        elif key == curses.KEY_DOWN and current < len(levels) - 1:
            current += 1
        elif key in (curses.KEY_ENTER, ord('\n'), ord('\r')):
            return levels[current]
        elif key in (ord('q'), ord('Q')):
            return None


def main_curses(stdscr, args):
    """
    Curses wrapper for the main game.
    
    Args:
        stdscr: Curses standard screen
        args: Command-line arguments
    """
    # Look for all available levels for progression
    levels_dir = Path(__file__).parent.parent / "levels"
    all_levels = list_levels(levels_dir)
    
    # Determine level to load
    if args.level:
        level_path = Path(args.level)
        if not level_path.exists():
            print(f"Error: Level file not found: {args.level}", file=sys.stderr)
            sys.exit(1)
    else:
        if not all_levels:
            print("Error: No level files found in levels/", file=sys.stderr)
            sys.exit(1)
        
        if len(all_levels) == 1:
            level_path = all_levels[0]
        else:
            # Show selection menu
            level_path = select_level(stdscr, all_levels)
            if level_path is None:
                return  # User quit
    
    # Run the game with all levels for progression
    game = Game(stdscr, str(level_path), debug=args.debug, all_levels=all_levels)
    game.run()


def main():
    """Entry point for the GridShift game."""
    parser = argparse.ArgumentParser(description="GridShift - A grid-based puzzle game")
    parser.add_argument("--level", "-l", help="Path to level file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    try:
        curses.wrapper(main_curses, args)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
