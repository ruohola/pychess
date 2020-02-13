import itertools
from typing import Dict, Optional

from bishop import Bishop
from color import Color
from king import King
from knight import Knight
from pawn import Pawn
from queen import Queen
from rook import Rook
from square import Square
from utils import idx_to_coord


class Board:
    """Models a chess board. The board is a dictionary of Squares, which act as graph nodes."""
    
    _FILES: str = "abcdefgh"
    _RANKS: str = "87654321"
    
    def __init__(self) -> None:
        """Setup the board with all the pieces on the starting positions."""
        self._squares: Dict[str, Square] = {coord: Square(coord) for coord in map("".join, itertools.product(self._FILES, self._RANKS))}
        
        self["a8"].piece = Rook(Color.BLACK)
        self["b8"].piece = Knight(Color.BLACK)
        self["c8"].piece = Bishop(Color.BLACK)
        self["d8"].piece = Queen(Color.BLACK)
        self["e8"].piece = King(Color.BLACK)
        self["f8"].piece = Bishop(Color.BLACK)
        self["g8"].piece = Knight(Color.BLACK)
        self["h8"].piece = Rook(Color.BLACK)
        self["a1"].piece = Rook(Color.WHITE)
        self["b1"].piece = Knight(Color.WHITE)
        self["c1"].piece = Bishop(Color.WHITE)
        self["d1"].piece = Queen(Color.WHITE)
        self["e1"].piece = King(Color.WHITE)
        self["f1"].piece = Bishop(Color.WHITE)
        self["g1"].piece = Knight(Color.WHITE)
        self["h1"].piece = Rook(Color.WHITE)
        
        for file in self._FILES:            
            self[f"{file}7"].piece = Pawn(Color.BLACK)
            self[f"{file}2"].piece = Pawn(Color.WHITE)
        
        # Set the adjacent Square nodes for each Square.
        for i in range(8):
            for j in range(8):
                sq = self._get(i, j)
                sq["n"] = self._get(i, j + 1)
                sq["e"] = self._get(i + 1, j)
                sq["s"] = self._get(i, j - 1)
                sq["w"] = self._get(i - 1, j)
                sq["ne"] = self._get(i + 1, j + 1)
                sq["se"] = self._get(i + 1, j - 1)
                sq["sw"] = self._get(i - 1, j - 1)
                sq["nw"] = self._get(i - 1, j + 1)
    
    def __iter__(self) -> 'Board':
        self.__iter = iter(self._squares.values())
        return self
        
    def __next__(self) -> Square:
        self.__val = next(self.__iter)
        return self.__val
    
    def __getitem__(self, coord: str) -> Square:
        return self._squares[coord]
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
 
    def __str__(self) -> str:
        file_labels = f"  {' '.join(list(self._FILES))} \n"
        
        rv = file_labels
        for rank in self._RANKS:
            rv += rank
            for file in self._FILES:
                rv += f" {self[file + rank]}"
            rv += f" {rank}\n"
        rv += file_labels
        return rv

    def _get(self, x: int, y: int) -> Optional[Square]:
        coord = idx_to_coord(x, y)
        return self._squares.get(coord)
