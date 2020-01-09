from typing import Iterator

from piece import Piece
from square import Square

        
class Rook(Piece):
    value = 5
    _symbol = "\u2656"
    
    def _all_moves(self) -> Iterator[Square]:
        yield from self._traverse("n", "e", "s", "w")
