"""Miscellaneous utility functions and constants for the game GUI."""

import os
from typing import Optional, Tuple

import scene

from color import Color
from piece import Piece
from utils import coord_to_idx


SPRITES_DIR = os.path.join(os.path.dirname(__file__), "sprites")
WIDTH, HEIGHT = map(int, scene.get_screen_size())
SQUARE_SIZE = min(WIDTH, HEIGHT) // 8


def get_image(piece: Piece, piece_name: Optional[str] = None, taken: bool = False) -> str:
    """Return the filepath for the given piece's sprite file."""
    if not piece_name:
        piece_name = piece.__class__.__name__
    if taken and piece.color == Color.BLACK:
        taken = "taken_"
    else:
        taken = ""
    return f"{SPRITES_DIR}/{taken}{piece.color.name.lower()}_{piece_name.lower()}.png"


def coord_to_pos(coord: str) -> Tuple[int, int]:
    """Return (x, y) screen position based on the square coordinate.
    
    No huge logic in this formula, but at least works perfectly on iPhone X and iPad Air.
    """

    x, y = coord_to_idx(coord)
    return (
        int((x-3.5)*SQUARE_SIZE + WIDTH/2),
        int((y-3.5)*SQUARE_SIZE + HEIGHT/2),
    )
