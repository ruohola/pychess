import re
from typing import Any, Dict, Optional, Pattern, TYPE_CHECKING

from color import Color

if TYPE_CHECKING:
    from piece import Piece


class Square:
    """Models one chess board square. A Square is also essentially a graph node."""
        
    _EMPTY_BLACK: str = "\u25A0"
    _EMPTY_WHITE: str = "\u25A1"
    _PATTERN: Pattern = re.compile(r"^[a-h][1-8]$")
        
    def __init__(self, coord: str) -> None:
        if not re.match(self._PATTERN, coord):
            raise ValueError(f"Invalid coordinate: '{coord}'")
            
        self.coord: str = coord
        self._adjacent: Dict[str, Optional['Square']] = {}
        self._piece: Optional['Piece'] = None
        self.ghost: Optional[Color] = None  # True if there's an virtual Pawn in the Square that can be captured en passant.
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.coord == other.coord
        
    def __getitem__(self, direction: str) -> Optional['Square']:
        return self._adjacent[direction]
    
    def __setitem__(self, direction: str, val: Optional['Square']) -> None:
        self._adjacent[direction] = val
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.coord!r})"
        
    def __str__(self) -> str:
        if self.piece:
            return str(self.piece)
        if self.is_white():
            return self._EMPTY_WHITE 
        return self._EMPTY_BLACK
        
    @property
    def piece(self) -> Optional['Piece']:
        return self._piece
    
    @piece.setter
    def piece(self, piece: 'Piece') -> None:
        """This allows the Square.piece and the corresponding Piece.square attributes to always be in sync."""
        
        self._piece = piece
        if piece:
            piece.square = self
    
    @property
    def file(self) -> str:
        return self.coord[0]
    
    @property
    def rank(self) -> int:
        return int(self.coord[1])
    
    def is_white(self) -> bool:
        """Return True if the Square is a white square, else False."""
    
        return (ord(self.file) + self.rank) % 2 != 0
    
    # Can't override __getattr__ for these, because it created a recursion problem when pickling.
    @property
    def n(self) -> Optional['Square']:
        return self["n"]

    @property
    def e(self) -> Optional['Square']:
        return self["e"]

    @property
    def s(self) -> Optional['Square']:
        return self["s"]

    @property
    def w(self) -> Optional['Square']:
        return self["w"]

    @property
    def ne(self) -> Optional['Square']:
        return self["ne"]

    @property
    def se(self) -> Optional['Square']:
        return self["se"]

    @property
    def sw(self) -> Optional['Square']:
        return self["sw"]

    @property
    def nw(self) -> Optional['Square']:
        return self["nw"]
