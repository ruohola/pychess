from typing import Iterator

from move import Move
from piece import Piece

        
class Bishop(Piece):
    value = 3
    _symbol = "\u2657"
    
    def _all_moves(self) -> Iterator[Move]:
        yield from self._traverse("ne", "se", "sw", "nw")
