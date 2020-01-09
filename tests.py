# Can't use unittest or pytest on Pythonista, because they had some import problems.
# Thus have to do the testing as a normal python script.

from contextlib import contextmanager
from functools import wraps

from bishop import Bishop
from board import Board
from color import Color
from exceptions import InvalidMoveError
from game import Game
from king import King
from knight import Knight
from pawn import Pawn
from queen import Queen
from rook import Rook
from utils import coord_to_idx, idx_to_coord


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Running: {func.__name__}", end=" ")
        try:
            rv = func(*args, **kwargs)
        except Exception:
            print("FAIL")
            raise
        else:                        
            print("OK")
        return rv
    return wrapper


@contextmanager
def assert_raises(exception):
    try:
        yield
    except exception:
        pass
    else:
        assert False, f"Did not raise {exception.__name__}"


@log
def test_coord_to_idx():
    assert coord_to_idx("a1") == (0, 0)
    assert coord_to_idx("h8") == (7, 7)
    assert coord_to_idx("e4") == (4, 3)


@log
def test_idx_to_coord():
    assert idx_to_coord(0, 0) == "a1"
    assert idx_to_coord(7, 7) == "h8"
    assert idx_to_coord(4, 3) == "e4"


@log
def test_piece_eq_and_hash():
    king1 = King(Color.WHITE)
    king2 = King(Color.WHITE)
    king3 = King(Color.BLACK)
    queen1 = Queen(Color.WHITE)
    queen2 = Queen(Color.WHITE)
    queen3 = Queen(Color.BLACK)
    assert king1 == king2 and hash(king1) == hash(king2)
    assert queen1 == queen2 and hash(queen1) == hash(queen2)
    assert king1 != king3 and hash(king1) != hash(king3)
    assert queen1 != queen3 and hash(queen1) != hash(queen3)


@log
def test_player_taken_pieces():
    game = Game()
    
    player = game.current_player
    game._board["a7"].piece = None
    game._board["b7"].piece = None
    game._board["c7"].piece = None
    game._board["a8"].piece = None
    game._board["b8"].piece = None
    game._board["h8"].piece = None
    game._board["c8"].piece = None
    
    assert player.taken_pieces == [Rook(Color.BLACK), Rook(Color.BLACK), Bishop(Color.BLACK), Knight(Color.BLACK), Pawn(Color.BLACK), Pawn(Color.BLACK), Pawn(Color.BLACK)]


@log
def test_board_str():
    board = Board()
    assert str(board) ==\
"""  a b c d e f g h 
8 ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜ 8
7 ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟ 7
6 □ ■ □ ■ □ ■ □ ■ 6
5 ■ □ ■ □ ■ □ ■ □ 5
4 □ ■ □ ■ □ ■ □ ■ 4
3 ■ □ ■ □ ■ □ ■ □ 3
2 ♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙ 2
1 ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖ 1
  a b c d e f g h 
"""


@log   
def test_board_adjacent_squares():
    board = Board()
    
    a1 = board["a1"]
    assert a1.n.coord == "a2"
    assert a1.e.coord == "b1"
    assert a1.s is None
    assert a1.w is None
    
    e4 = board["e4"]
    assert e4.n.coord == "e5"
    assert e4.e.coord == "f4"
    assert e4.s.coord == "e3"
    assert e4.w.coord == "d4"


@log
def test_queen_allowed_moves():
    game = Game()
       
    player = game.current_player
    game._board["d4"].piece = game._board["d1"].piece
    assert sorted(move.square.coord for move in player.allowed_moves("d4")) == ['a4', 'a7', 'b4', 'b6', 'c3', 'c4', 'c5', 'd3', 'd5', 'd6', 'd7', 'e3', 'e4', 'e5', 'f4', 'f6', 'g4', 'g7', 'h4']
    

@log
def test_knight_allowed_moves():
    game = Game()
    
    player = game.current_player
    assert sorted(move.square.coord for move in player.allowed_moves("b1")) == ['a3', 'c3']
    player.move("b1", "a3")
    
    player = game.next_player()
    player.move("b7", "b5")
    
    player = game.next_player()
    assert sorted(move.square.coord for move in player.allowed_moves("a3")) == ['b1', 'b5', 'c4']


@log
def test_king_allowed_moves():
    game = Game()
    
    player = game.current_player
    player.move("e2", "e3")
    player.move("f2", "f3")
    player.move("f1", "a6")
    assert sorted(move.square.coord for move in player.allowed_moves("e1")) == ['e2', 'f1', 'f2']


@log
def test_correct_enpassant():
    # Test correct en passant
    game = Game()
    
    player = game.current_player
    player.move("b2", "b4")
    player.move("b4", "b5")
    
    player = game.next_player()
    player.move("c7", "c5")
    
    player = game.next_player()
    player.move("b5", "c6")
    assert game._board["c5"].piece is None
    
    # Test that can en passant to escape a check.
    game = Game()
    
    player = game.current_player
    player.move("e2", "e4")
    player.move("e4", "e5")
    player.move("e1", "e2")
    player.move("e2", "f3")
    player.move("f3", "g4")
            
    player = game.next_player()
    player.move("f7", "f5")
    
    player = game.next_player()
    player.move("e5", "f6")
    
    
@log
def test_invalid_enpassant():
    # Test that can't en passant after a turn has passed.
    game = Game()
    
    player = game.current_player
    player.move("b2", "b4")
    player.move("b4", "b5")
        
    player = game.next_player()
    player.move("c7", "c5")

    player = game.next_player()
    player.move("h2", "h3")
    
    player = game.next_player()
    player.move("h7", "h6")
       
    player = game.next_player()
    with assert_raises(InvalidMoveError):
        player.move("b5", "c6")
    
    # Test that can't en passant when it opens a check.
    game = Game()
    
    player = game.current_player
    player.move("e2", "e4")
    player.move("e4", "e5")
    player.move("e1", "e2")
    player.move("e2", "f3")
    player.move("f3", "g4")
    player.move("g4", "g5")
            
    player = game.next_player()
    player.move("a7", "a5")
    player.move("a5", "a4")
    player.move("a8", "a5")
    player.move("f7", "f5")
    
    player = game.next_player()
    with assert_raises(InvalidMoveError):
        player.move("e5", "f6")
    

@log
def test_pawn_promotion():
    game = Game()
    
    game._board["a8"].piece = None
    game._board["a7"].piece = None
    
    player = game.current_player
    player.move("a2", "a4")
    player.move("a4", "a5")
    player.move("a5", "a6")
    player.move("a6", "a7")
    player.move("a7", "a8")
    
    assert player.promotion
    
    with assert_raises(InvalidMoveError):
        player = game.next_player()
    
    with assert_raises(InvalidMoveError):
        player = game.next_player()
    
    player.promote("queen")    
    assert not player.promotion
    assert isinstance(game._board["a8"].piece, Queen)
    

@log
def test_castling():
    # Castle to east
    game = Game()
    
    player = game.current_player
    player.move("g2", "g3")
    player.move("f1", "h3")
    player.move("g1", "f3")
    
    player.move("e1", "g1")
    assert isinstance(game._board["g1"].piece, King)
    assert isinstance(game._board["f1"].piece, Rook)
    
    # Castle to west
    game = Game()
    
    player = game.current_player
    player.move("b2", "b4")
    player.move("c2", "c4")
    player.move("b1", "c3")
    player.move("c1", "a3")
    player.move("d1", "b3")
    
    player.move("e1", "c1")
    assert isinstance(game._board["c1"].piece, King)
    assert isinstance(game._board["d1"].piece, Rook)
    
    # Can't castle over checkline.
    game = Game()
    
    player = game.current_player
    player.move("b2", "b4")
    player.move("c2", "c4")
    player.move("b1", "c3")
    player.move("c1", "a3")
    player.move("d1", "b3")
    player.move("e2", "e3")
    
    player = game.next_player()
    player.move("d7", "d6")
    player.move("c8", "g4")

    player = game.next_player()
    with assert_raises(InvalidMoveError):
        player.move("e1", "c1")

    # Can't castle away from check
    game = Game()
    
    player = game.current_player
    player.move("b2", "b4")
    player.move("c2", "c4")
    player.move("b1", "c3")
    player.move("c1", "a3")
    player.move("d1", "b3")
    player.move("f2", "f3")
    
    player = game.next_player()
    player.move("e7", "e6")
    player.move("d8", "h4")

    player = game.next_player()
    with assert_raises(InvalidMoveError):
        player.move("e1", "c1")


@log
def test_king_check():
    game = Game()
    
    player = game.current_player
    assert isinstance(player._king, King)
    assert player._king.color == Color.WHITE
    player.move("d2", "d4")
    
    player = game.next_player()
    assert isinstance(player._king, King)
    assert player._king.color == Color.BLACK
    player.move("c7", "c5")
    
    player = game.next_player()
    player.move("d4", "c5")
    assert not player.is_checked()

    player = game.next_player()
    player.move("d8", "a5")
    
    player = game.next_player()
    assert player.is_checked()
    assert sorted(move.square.coord for move in player.allowed_moves("b2")) == ["b4"]
    assert sorted(move.square.coord for move in player.allowed_moves("c2")) == ["c3"]
    assert sorted(move.square.coord for move in player.allowed_moves("d1")) == ["d2"]
    assert sorted(move.square.coord for move in player.allowed_moves("b1")) == ["c3", "d2"]
    assert sorted(move.square.coord for move in player.allowed_moves("e1")) == []
    

test_coord_to_idx()
test_idx_to_coord()
test_piece_eq_and_hash()
test_player_taken_pieces()
test_board_str()
test_board_adjacent_squares()
test_queen_allowed_moves()
test_knight_allowed_moves()
test_king_allowed_moves()
test_correct_enpassant()
test_invalid_enpassant()
test_pawn_promotion()
test_castling()
test_king_check()

print("All tests passed.")
