from typing import Tuple


class InvalidMoveError(Exception):
    pass


def coord_to_idx(coord: str) -> Tuple[int, int]:
    file, rank = coord
    x = ord(file) - 97
    y = int(rank) - 1
    return x, y
    
    
def idx_to_coord(x: int, y: int) -> str:
    file = chr(x + 97)
    rank = str(y + 1)
    return file + rank
