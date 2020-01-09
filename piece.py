from abc import ABC, abstractmethod
from functools import total_ordering
from typing import Any, Iterator, Optional

from color import Color
from move import Move
from square import Square


@total_ordering
class Piece(ABC):
    """Abstract base class for every chess piece."""
    
    def __init__(self, color: Color) -> None:
        self.color: Color = color
        self.square: Optional[Square] = None
        self.moved: bool = False  # Used for King, Rook, and Pawn.
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Piece):
            return NotImplemented
        return self.__class__ == other.__class__ and self.color == other.color
    
    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Piece) or self.color != other.color:
            # Can't order different color pieces.
            return NotImplemented
        if self.value == other.value:
            # Knight should come before Bishop.
            return self.__class__.__name__ > other.__class__.__name__
        return self.value < other.value
    
    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.color))
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.color})"    
    
    def __str__(self) -> str:
        # White and black unicode chess piece symbols are 6 code points from each other.
        if self.color == Color.WHITE:
            return self._symbol
        else:
            return chr(ord(self._symbol) + 6)

    def allowed_moves(self) -> Iterator[Move]:
        return (move for move in self._all_moves() if move.square and (not move.square.piece or move.square.piece.color != self.color))
        
    def _traverse(self, *directions: str, max_depth: int = 7) -> Iterator[Move]:
        for direction in directions:
            sq = self.square[direction]
            depth = max_depth
            while sq and depth:
                yield Move(sq)
                if sq.piece:
                    break
                sq = sq[direction]
                depth -= 1
    
    @abstractmethod
    def _all_moves(self) -> Iterator[Move]:
        pass

    @property
    @abstractmethod
    def value(self) -> str:
        """The relative value of the piece, e.g. 9 for Queen."""
        pass
            
    @property
    @abstractmethod
    def _symbol(self) -> str:
        """The unicode symbol of the white piece, black symbol is inferred based on this."""
        pass
