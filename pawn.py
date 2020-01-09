from typing import Iterator

from color import Color
from move import Move
from piece import Piece

        
class Pawn(Piece):
    value = 1
    _symbol = "\u2659"
    
    def __init__(self, color: Color) -> None:
        super().__init__(color)
        self.forward: str = "n" if self.color == Color.WHITE else "s"
    
    def _all_moves(self) -> Iterator[Move]:        
        fwd = self.forward
        
        # Standard move
        if self.square[fwd] and not self.square[fwd].piece:
            yield Move(self.square[fwd])
       
            # Can only do double move if able to do standard move.
            if not self.moved and not self.square[fwd][fwd].piece:
                yield Move(self.square[fwd][fwd], pawn_double_move=True)
            
        # Capturing
        for direction in ("e", "w"):
            sq = self.square[fwd + direction]
            if sq and sq.piece:
                # Capture normally
                yield Move(sq)
            elif sq and sq.ghost and sq.ghost != self.color:
                # Capture en passant
                yield Move(sq, enpassant=True)
