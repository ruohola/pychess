from typing import Iterator

from move import Move
from piece import Piece
from rook import Rook

        
class King(Piece):
    value = 0
    _symbol = "\u2654"
        
    def _all_moves(self) -> Iterator[Move]:
        yield from self._traverse("n", "e", "s", "w", "ne", "se", "sw", "nw", max_depth=1)
        
        # Castling
        if not self.moved:
            # Checking the eastern rook.
            to_e = list(self._traverse("e"))
            if len(to_e) == 3:
                # Rook is always 3 squares to  east.
                if isinstance(to_e[-1].square.piece, Rook) and not to_e[-1].square.piece.moved:
                    to_e[1].castle = True
                    yield to_e[1]
            
            # Checking the western rook.
            to_w = list(self._traverse("w"))
            if len(to_w) == 4:
                # Rook is always 4 squares to west.
                if isinstance(to_w[-1].square.piece, Rook) and not to_w[-1].square.piece.moved:
                    to_w[1].castle = True
                    yield to_w[1]
