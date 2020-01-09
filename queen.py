from typing import Iterator

from bishop import Bishop
from move import Move
from rook import Rook

        
class Queen(Bishop, Rook):
    value = 9
    _symbol = "\u2655"
    
    def _all_moves(self) -> Iterator[Move]:
        yield from Bishop._all_moves(self)
        yield from Rook._all_moves(self)
