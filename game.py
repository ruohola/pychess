from itertools import cycle
from typing import Iterator, Optional

from board import Board
from color import Color
from utils import InvalidMoveError
from player import Player
from square import Square
from time_control import TimeControl


class Game:
    def __init__(self, time_control: Optional[TimeControl] = None) -> None:
        self._board: Board = Board()
        self.white: Player = Player(Color.WHITE, self._board, time_control)
        self.black: Player = Player(Color.BLACK, self._board, time_control)
        self.white.opponent = self.black
        self.black.opponent = self.white
        
        self._players: Iterator[Player] = cycle((self.white, self.black))
        self.current_player: Player = next(self._players)

        self.started = False
        
    def __str__(self) -> str:
        return str(self._board)
    
    def next_player(self) -> Player:
        self.started = True

        if self.current_player.promotion:
            # Promotion should be handled before the next turn can start.
            raise InvalidMoveError
        
        if self.current_player.time_control:
            self.current_player.stop_clock()
        
        self.current_player = next(self._players)
        
        if self.current_player.time_control:
            self.current_player.start_clock()
        
        # Clear own en passant ghost markings
        rank = "3" if self.current_player.color == Color.WHITE else "6"
        for file in "abcdefgh":
            self._board[file + rank].ghost = None
        
        return self.current_player
            
    # The two methods under this are used exclusively for the iOS GUI.
    
    def color_of_piece(self, coord: str) -> Optional[Color]:
        try:
            return self._board[coord].piece.color
        except (AttributeError, KeyError):
            return None
    
    def iter_squares(self) -> Iterator[Square]:
        yield from self._board
