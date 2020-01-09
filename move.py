from typing import Optional

from square import Square


class Move:
    # Could be Python 3.7 @dataclass
    
    def __init__(self, square: Square, castle: bool = False,
                 enpassant: bool = False, pawn_double_move: bool = False) -> None:
        self.square: Optional[Square] = square        
        self.castle: bool = castle
        self.enpassant: bool = enpassant
        self.pawn_double_move: bool = pawn_double_move
    
    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}({self.square!r}, "
                f"castle={self.castle}, enpassant={self.enpassant}, "
                f"pawn_double_move={self.pawn_double_move})")
