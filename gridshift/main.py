#!/usr/bin/env python3
"""GridShift - A Sokoban-style puzzle game."""

import curses
import sys
import argparse
from pathlib import Path

from gridshift.models import Direction, GameState
from gridshift.level_loader import load_level
from gridshift.engine import move, check_win
from gridshift.undo import UndoManager


def draw_game(stdscr, state: GameState, move_count: int, undo_depth: int, message: str = ""):
    """Draw the game state to the screen."""
    stdscr.clear()
    
    # Draw title
    stdscr.addstr(0, 0, "=== GRIDSHIFT ===", curses.A_BOLD)
    stdscr.addstr(1, 0, f"Moves: {move_count}  Undo: {undo_depth}  {message}")
    stdscr.addstr(2, 0, "-" * 40)
    
    # Draw grid
    for row_idx, row in enumerate(state.grid):
        row_str = ""
        for col_idx, tile in enumerate(row):
            pos = (row_idx, col_idx)
            # Check if box is on goal
            if pos in state.box_positions and pos in state.goal_positions:
                row_str += "*"  # Box on goal
            # Check if player is on goal
            elif state.player_pos.row == row_idx and state.player_pos.col == col_idx:
                if (row_idx, col_idx) in state.goal_positions:
                    row_str += "+"  # Player on goal
                else:
                    row_str += "@"  # Player
            else:
                row_str += tile.value
        stdscr.addstr(row_idx + 3, 0, row_str)
    
    # Draw controls
    controls_y = state.height + 4
    stdscr.addstr(controls_y, 0, "-" * 40)
    stdscr.addstr(controls_y + 1, 0, "Controls: WASD/Arrows=Move  Z=Undo  R=Reset  Q=Quit")
    
    stdscr.refresh()


def main():
    """Main game loop."""
    parser = argparse.ArgumentParser(description="GridShift - Sokoban puzzle game")
    parser.add_argument("--level", default="levels/level01.txt", help="Level file to load")
    args = parser.parse_args()
    
    # Load level
    try:
        initial_state = load_level(args.level)
    except FileNotFoundError:
        print(f"Error: Level file '{args.level}' not found")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid level file - {e}")
        sys.exit(1)
    
    # Initialize curses
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)  # Hide cursor
    
    try:
        # Game state
        current_state = initial_state
        undo_manager = UndoManager()
        move_count = 0
        message = "Push all boxes ($) onto goals (.) to win!"
        
        while True:
            # Check win condition
            if check_win(current_state):
                draw_game(stdscr, current_state, move_count, undo_manager.depth, "🎉 YOU WIN! Press Q to quit")
                stdscr.getch()
                break
            
            # Draw current state
            draw_game(stdscr, current_state, move_count, undo_manager.depth, message)
            message = ""
            
            # Get input
            key = stdscr.getch()
            
            # Handle quit
            if key in (ord('q'), ord('Q')):
                break
            
            # Handle reset
            if key in (ord('r'), ord('R')):
                current_state = initial_state
                undo_manager.clear()
                move_count = 0
                message = "Game reset!"
                continue
            
            # Handle undo
            if key in (ord('z'), ord('Z')):
                prev_state = undo_manager.pop()
                if prev_state:
                    current_state = prev_state
                    move_count -= 1
                    message = "Undo!"
                else:
                    message = "Nothing to undo"
                continue
            
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
                # Save state for undo
                undo_manager.push(current_state)
                
                # Try move
                new_state, moved = move(current_state, direction)
                
                if moved:
                    current_state = new_state
                    move_count += 1
                else:
                    # Move was blocked, remove from undo
                    undo_manager.pop()
                    message = "Blocked!"
    
    finally:
        # Restore terminal
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()


if __name__ == "__main__":
    main()
