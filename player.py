import collections
import time
from functools import wraps
from typing import Counter, Iterator, List, Optional

from bishop import Bishop
from board import Board
from color import Color
from exceptions import InvalidMoveError
from king import King
from knight import Knight
from move import Move
from pawn import Pawn
from piece import Piece
from queen import Queen
from square import Square
from rook import Rook
from time_control import TimeControl


def _validate_move(func):
    """Check that there is an own colored piece in the coordinate we are moving from. Check also the the possible square we are trying to move to even exists."""
    @wraps(func)
    def wrapper(self, fr, *to):
        try:
            if self._board[fr].piece.color != self.color:
                raise InvalidMoveError
        except (AttributeError, KeyError):
            raise InvalidMoveError from None
            
        try:
            if to:
                self._board[to[0]]
        except KeyError:
            raise InvalidMoveError from None
            
        return func(self, fr, *to)   
    return wrapper


class Player:
    def __init__(self, color: Color, board: Board, time_control: Optional[TimeControl] = None):
        self.color: Color = color
        self._board: Board = board
        
        self.starting_pieces: Counter[Piece] = collections.Counter(self.pieces)

        self.opponent: Optional[Player] = None
        self.__king: Optional[King] = None
        self.promotion: Optional[Square] = None

        self.time_control: Optional[TimeControl] = time_control
        if self.time_control:
            self._time_left: Optional[float] = self.time_control.time
        self._running: bool = False
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.color}, {self._board!r})"
    
    def __str__(self) -> str:
        return self.color.name.capitalize()
    
    @_validate_move
    def allowed_moves(self, fr: str) -> Iterator[Move]:
        for move in self._board[fr].piece.allowed_moves():
            to = move.square.coord
            if move.enpassant:
                if not self._opens_check(fr, to, captured=to[0]+fr[1]):
                    yield move
            elif move.castle:
                if self.is_checked():
                    continue
                if to > fr:
                    # Castled to the east
                    if not self.is_checked(self._king.square.e) and not self.is_checked(self._king.square.e.e):
                        yield move
                else:
                    # Castled to the west
                    if not self.is_checked(self._king.square.w) and not self.is_checked(self._king.square.w.w):
                        yield move
            else:
                if not self._opens_check(fr, to):
                    yield move
                
    @_validate_move
    def move(self, fr: str, to: str) -> None:
        if self.promotion:
            raise InvalidMoveError
            
        if self.time_control and self.read_clock() == 0:
            # Can't move after time has run out.
            raise InvalidMoveError
        
        for move in self.allowed_moves(fr):
            if move.square.coord == to:
                break
        else:
            raise InvalidMoveError
             
        self._board[to].piece = self._board[fr].piece
        self._board[fr].piece = None
        self._board[to].piece.moved = True       
        
        if move.enpassant:
            # to[0] + fr[1] is the square where the double moved pawn sits when we capture it en passant via `to` square.
            # E.g. we move from d5 to e6, the pawn we capture en passant is in c5.
            self._board[to[0] + fr[1]].piece = None
        
        if move.pawn_double_move:
            # Save a double moved Pawn as a ghost to handle possible en passant next move.
            self._board[f"{fr[0]}{(int(fr[1]) + int(to[1])) // 2}"].ghost = self.color

        if isinstance(self._board[to].piece, Pawn) and to[1] in {"1", "8"}:
            # Pawn moved to the last file, so make a mark that the next thing to do is to promote the Pawn.
            self.promotion = self._board[to]
                
        if move.castle:
            rank = to[1]             
            if to > fr:
                # Castled to the east
                self._board["f" + rank].piece = self._board["h" + rank].piece
                self._board["h" + rank].piece = None
            else:
                # Castled to the west
                self._board["d" + rank].piece = self._board["a" + rank].piece
                self._board["a" + rank].piece = None
      
    def promote(self, piece: str) -> None:
        if not self.promotion:
            raise InvalidMoveError

        try:
            piece = piece.lower()
        except AttributeError:
            raise InvalidMoveError from None
            
        promotion_options = {"queen": Queen, "knight": Knight, "rook": Rook, "bishop": Bishop}      
        try:
            self.promotion.piece = promotion_options[piece](self.color)
        except KeyError:
            raise InvalidMoveError from None
        
        self.promotion = None
    
    def is_checked(self, square_to_check: Optional[Square] = None) -> bool:
        if square_to_check is None:
            square_to_check = self._king.square

        for piece in self.opponent.pieces:
            for move in piece.allowed_moves():
                if move.square == square_to_check:
                    return True
        return False
    
    def _opens_check(self, fr: str, to: str, captured: Optional[str] = None) -> bool:
        if captured is not None:
            captured_backup = self._board[captured].piece
            self._board[captured].piece = None
        
        to_backup = self._board[to].piece
        self._board[to].piece = self._board[fr].piece
        self._board[fr].piece = None

        if self.is_checked():
            rv = True
        else:
            rv = False
            
        # Rollback the move
        self._board[fr].piece = self._board[to].piece
        self._board[to].piece = to_backup
        if captured is not None:
            self._board[captured].piece = captured_backup
        
        return rv
    
    def start_clock(self) -> None:
        self.__timer = time.time()
        self._running = True
    
    def stop_clock(self) -> None:
        if self._running:
            diff = time.time() - self.__timer
            if diff > self.time_control.delay:
                self._time_left -= (diff - self.time_control.delay)
            self._time_left += self.time_control.increment
            del self.__timer
            self._running = False
    
    def read_clock(self) -> float:
        if self._running:
            diff = time.time() - self.__timer
        else:
            diff = 0
            
        if diff > self.time_control.delay:
            res = self._time_left - (diff - self.time_control.delay)
        else:
            res = self._time_left
            
        return res if res > 0 else 0
    
    def value_diff(self) -> int:
        value_own = sum(piece.value for piece in self.pieces)
        value_opp = sum(piece.value for piece in self.opponent.pieces)
        return value_own - value_opp
        
    @property
    def pieces(self) -> Iterator[Piece]:
        for square in self._board:
            if square.piece and square.piece.color == self.color:
                yield square.piece
    
    @property
    def taken_pieces(self) -> List[Piece]:
        diff = self.opponent.starting_pieces - collections.Counter(self.opponent.pieces)
        return sorted(diff.elements(), reverse=True)
    
    @property
    def _king(self) -> King:
        # Could be Python 3.8 @cached_property
        if not self.__king:
            for piece in self.pieces:
                if isinstance(piece, King):
                    self.__king = piece
        return self.__king
