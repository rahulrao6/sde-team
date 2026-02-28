"""Core data models for GridShift."""

from enum import Enum
from dataclasses import dataclass
from typing import Set
import copy


class Tile(Enum):
    """Represents a tile type on the game grid."""
    WALL = '#'
    PLAYER = '@'
    BOX = '$'
    GOAL = '.'
    EMPTY = ' '
    
    @classmethod
    def from_char(cls, char: str) -> 'Tile':
        """Parse a character into a Tile enum."""
        for tile in cls:
            if tile.value == char:
                return tile
        raise ValueError(f"Invalid tile character: {char!r}")


class Direction(Enum):
    """Represents a movement direction."""
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


@dataclass(frozen=True)
class Position:
    """Represents a position on the grid."""
    row: int
    col: int
    
    def move(self, direction: Direction) -> 'Position':
        """Return a new position moved in the given direction."""
        dr, dc = direction.value
        return Position(self.row + dr, self.col + dc)


@dataclass
class GameState:
    """Represents the complete state of the game."""
    grid: list[list[Tile]]
    player_pos: Position
    box_positions: Set[Position]
    goal_positions: Set[Position]
    width: int
    height: int
    
    def clone(self) -> 'GameState':
        """Create an independent deep copy of this GameState."""
        return GameState(
            grid=copy.deepcopy(self.grid),
            player_pos=self.player_pos,  # Position is frozen/immutable
            box_positions=self.box_positions.copy(),
            goal_positions=self.goal_positions.copy(),
            width=self.width,
            height=self.height
        )
