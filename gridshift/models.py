"""Core data models for GridShift."""
from enum import Enum
from dataclasses import dataclass
from typing import List, Set
import copy


class Tile(Enum):
    """Represents a single tile type in the game grid."""
    WALL = '#'
    PLAYER = '@'
    BOX = '$'
    GOAL = '.'
    EMPTY = ' '


class Direction(Enum):
    """Represents movement directions."""
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'


@dataclass(frozen=True)
class Position:
    """Represents a position in the grid."""
    row: int
    col: int
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col
    
    def __hash__(self):
        return hash((self.row, self.col))


@dataclass
class GameState:
    """Represents the complete state of the game."""
    grid: List[List[Tile]]
    player_pos: Position
    box_positions: Set[Position]
    goal_positions: Set[Position]
    width: int
    height: int
    
    def clone(self):
        """Create a deep copy of this GameState."""
        return GameState(
            grid=copy.deepcopy(self.grid),
            player_pos=Position(self.player_pos.row, self.player_pos.col),
            box_positions=set(Position(p.row, p.col) for p in self.box_positions),
            goal_positions=set(Position(p.row, p.col) for p in self.goal_positions),
            width=self.width,
            height=self.height
        )
