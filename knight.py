from typing import Iterator, List

from move import Move
from piece import Piece

        
class Knight(Piece):
    value = 3
    _symbol = "\u2658"
    
    def _traverse(self, *paths: List[str]) -> Iterator[Move]:        
        for path in paths:
            sq = self.square
            for direction in path:
                try:
                    sq = sq[direction]
                except TypeError:
                    break
            else:
                yield Move(sq)      
                
    def _all_moves(self) -> Iterator[Move]:
        yield from self._traverse(
            ["n", "n", "e"],
            ["n", "n", "w"],
            ["e", "e", "n"],
            ["e", "e", "s"],
            ["s", "s", "e"],
            ["s", "s", "w"],
            ["w", "w", "n"],
            ["w", "w", "s"],
        )
