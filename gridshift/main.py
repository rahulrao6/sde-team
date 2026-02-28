"""Main game loop and entry point for GridShift."""

import curses
import sys
import time
import argparse
from pathlib import Path
from typing import Optional

from .models import Direction
from .level_loader import load_level
from .engine import move, check_win
from .undo import UndoManager
from .renderer import Renderer
from .debug import DebugLogger


class Game:
    """Main game controller."""
    
    def __init__(self, level_path: str, debug: bool = False):
        """Initialize the game.
        
        Args:
            level_path: Path to level file
            debug: Enable debug logging
        """
        self.level_path = level_path
        self.level_name = Path(level_path).stem
        self.debug_logger = DebugLogger(enabled=debug)
        
        # Load initial state
        self.initial_state = load_level(level_path)
        self.current_state = self.initial_state.clone()
        
        # Game components
        self.undo_manager = UndoManager()
        self.move_count = 0
        self.message = ""
        self.won = False
        
        self.debug_logger.log(f"Loaded level: {level_path}")
        self.debug_logger.dump_state(self.initial_state)
    
    def reset(self) -> None:
        """Reset the game to initial state."""
        self.current_state = self.initial_state.clone()
        self.undo_manager.clear()
        self.move_count = 0
        self.message = "Level reset"
        self.won = False
        self.debug_logger.log("Game reset")
    
    def handle_move(self, direction: Direction) -> None:
        """Handle a movement input.
        
        Args:
            direction: Direction to move
        """
        if self.won:
            return
        
        # Save state before move for undo
        self.undo_manager.push(self.current_state.clone())
        
        # Attempt move
        new_state, moved = move(self.current_state, direction)
        
        if moved:
            self.current_state = new_state
            self.move_count += 1
            self.message = ""
            
            self.debug_logger.log(f"Move {self.move_count}: {direction.name}")
            
            # Check win condition
            if check_win(self.current_state):
                self.won = True
                self.message = f"*** YOU WIN! *** Completed in {self.move_count} moves!"
                self.debug_logger.log("WIN!")
        else:
            # Move was blocked, don't count it and remove from undo
            self.undo_manager.pop()
            self.debug_logger.log(f"Move blocked: {direction.name}")
    
    def handle_undo(self) -> None:
        """Undo the last move."""
        if self.won:
            return
        
        previous_state = self.undo_manager.pop()
        if previous_state is not None:
            self.current_state = previous_state
            self.move_count = max(0, self.move_count - 1)
            self.message = "Undo"
            self.debug_logger.log("Undo")
        else:
            self.message = "Nothing to undo"
    
    def run(self, stdscr) -> None:
        """Main game loop.
        
        Args:
            stdscr: Curses standard screen
        """
        renderer = Renderer(stdscr)
        
        # Set non-blocking input with timeout
        stdscr.nodelay(True)
        stdscr.timeout(16)  # ~60 fps (16ms per frame)
        
        running = True
        last_frame_time = time.time()
        
        while running:
            # Frame timing (60fps cap)
            current_time = time.time()
            delta_time = current_time - last_frame_time
            
            if delta_time < 1/60:
                # Wait a bit to maintain 60fps
                time.sleep(1/60 - delta_time)
            
            last_frame_time = current_time
            
            # Render
            renderer.render(
                self.current_state,
                self.move_count,
                self.message,
                self.undo_manager.depth,
                self.level_name
            )
            
            # Input handling
            try:
                key = stdscr.getch()
                
                if key == -1:
                    # No input
                    continue
                
                # Convert key to character
                if key == curses.KEY_UP or key == ord('w') or key == ord('W'):
                    self.handle_move(Direction.UP)
                elif key == curses.KEY_DOWN or key == ord('s') or key == ord('S'):
                    self.handle_move(Direction.DOWN)
                elif key == curses.KEY_LEFT or key == ord('a') or key == ord('A'):
                    self.handle_move(Direction.LEFT)
                elif key == curses.KEY_RIGHT or key == ord('d') or key == ord('D'):
                    self.handle_move(Direction.RIGHT)
                elif key == ord('r') or key == ord('R'):
                    self.reset()
                elif key == ord('z') or key == ord('Z'):
                    self.handle_undo()
                elif key == ord('q') or key == ord('Q'):
                    running = False
                    
            except KeyboardInterrupt:
                running = False
        
        self.debug_logger.log("Game ended")


def select_level(levels_dir: Path) -> Optional[Path]:
    """Show level selection menu and return chosen level path.
    
    Args:
        levels_dir: Directory containing level files
        
    Returns:
        Path to selected level, or None if cancelled
    """
    level_files = sorted(levels_dir.glob("level*.txt"))
    
    if not level_files:
        print("No level files found in levels/ directory", file=sys.stderr)
        return None
    
    if len(level_files) == 1:
        return level_files[0]
    
    print("Select a level:")
    for i, level_file in enumerate(level_files, 1):
        print(f"  {i}. {level_file.name}")
    
    while True:
        try:
            choice = input("Enter level number (or q to quit): ").strip()
            if choice.lower() == 'q':
                return None
            
            level_num = int(choice)
            if 1 <= level_num <= len(level_files):
                return level_files[level_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(level_files)}")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except (EOFError, KeyboardInterrupt):
            return None


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="GridShift - A Sokoban-style puzzle game")
    parser.add_argument(
        "--level",
        type=str,
        help="Path to level file"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging to stderr"
    )
    
    args = parser.parse_args()
    
    # Determine level to load
    if args.level:
        level_path = Path(args.level)
        if not level_path.exists():
            print(f"Error: Level file not found: {level_path}", file=sys.stderr)
            sys.exit(1)
    else:
        # Look for levels in levels/ directory
        levels_dir = Path(__file__).parent.parent / "levels"
        if not levels_dir.exists():
            print("Error: levels/ directory not found", file=sys.stderr)
            sys.exit(1)
        
        level_path = select_level(levels_dir)
        if level_path is None:
            sys.exit(0)
    
    try:
        # Create game instance
        game = Game(str(level_path), debug=args.debug)
        
        # Run game with curses
        curses.wrapper(game.run)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
