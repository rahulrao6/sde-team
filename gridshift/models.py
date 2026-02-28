"""Core data models for GridShift game."""

from dataclasses import dataclass
from enum import Enum
from typing import Set


class Tile(Enum):
    """Represents a single tile type in the game grid."""
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

    @property
    def delta_row(self) -> int:
        """Row offset for this direction."""
        return self.value[0]

    @property
    def delta_col(self) -> int:
        """Column offset for this direction."""
        return self.value[1]


@dataclass(frozen=True)
class Position:
    """Represents a position on the game grid."""
    row: int
    col: int

    def move(self, direction: Direction) -> 'Position':
        """Return a new Position moved in the given direction."""
        return Position(
            self.row + direction.delta_row,
            self.col + direction.delta_col
        )


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
        """Create a deep copy of this GameState."""
        # Deep copy the grid
        grid_copy = [row[:] for row in self.grid]
        
        # Position is frozen (immutable), but we copy the sets
        box_positions_copy = self.box_positions.copy()
        goal_positions_copy = self.goal_positions.copy()
        
        return GameState(
            grid=grid_copy,
            player_pos=self.player_pos,  # Position is immutable
            box_positions=box_positions_copy,
            goal_positions=goal_positions_copy,
            width=self.width,
            height=self.height
        )
