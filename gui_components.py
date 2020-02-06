"""All the classes that the game GUI uses."""

import math
import time
from typing import List, Tuple, Union

import ui
import scene

from color import Color
from gui_utils import WIDTH, HEIGHT, SQUARE_SIZE, coord_to_pos, get_image
from piece import Piece
from player import Player
from square import Square

LIGHT_SQUARE_COLOR = "#eeeed2"
DARK_SQUARE_COLOR = "#769656"


class SquareShape(scene.ShapeNode):
    """Shape for one chess board square. 64 of these make the full chess board."""

    class IndexLabel(scene.LabelNode):
        def __init__(self, text: Union[str, int]) -> None:
            side = SQUARE_SIZE // 2 - 4
            if isinstance(text, int):
                # The rank index is an int and it will be drawn to top left of the square.
                pos = (-side + 1, side - 3)
            else:
                # The file index is a string and it will be drawn to the bottom right of the square.
                pos = (side, -side)

            super().__init__(
                text=str(text), font=("Helvetica", SQUARE_SIZE//5),
                position=pos,
                color="black",
            )

    def __init__(self, parent: scene.Node, square: Square) -> None:
        self.coord = square.coord

        if square.is_white():
            color = LIGHT_SQUARE_COLOR
        else:
            color = DARK_SQUARE_COLOR
        pos = coord_to_pos(square.coord)
        path = ui.Path.rect(0, 0, SQUARE_SIZE, SQUARE_SIZE)

        super().__init__(
            path=path,
            parent=parent,
            position=pos,
            fill_color=color,
        )
        # Coordinate index labels
        if square.file == "a":
            self.add_child(self.IndexLabel(square.rank))
        if square.rank == 1:
            self.add_child(self.IndexLabel(square.file))
            
        
class PieceSprite(scene.SpriteNode):
    """Sprite, which holds an image of any one chess piece."""

    def __init__(self, parent: scene.Node, piece: Piece) -> None:
        pos = coord_to_pos(piece.square.coord)

        # Black pieces are flipped 180 degrees.
        size = (SQUARE_SIZE * piece.color.value,) * 2
        
        super().__init__(
            texture=get_image(piece),
            parent=parent,
            position=pos,
            z_position=2,
            size=size,
        )


class SelectedShape(scene.ShapeNode):
    """The shape drawn around the currently selected piece."""

    def __init__(self, parent: scene.Node, coord: str) -> None:
        pos = coord_to_pos(coord)
        path = ui.Path.rect(0, 0, SQUARE_SIZE, SQUARE_SIZE)

        super().__init__(
            path=path,
            parent=parent,
            position=pos,
            z_position=1,
            fill_color="orange",
            alpha=0.5,
        )
        

class MoveShape(scene.ShapeNode):
    """A circle drawn on the board squares to represent allowed moves for the selected piece."""

    def __init__(self, parent: scene.Node, coord: str) -> None:
        pos = coord_to_pos(coord)
        width = int(SQUARE_SIZE * 0.4)
        path = ui.Path.oval(0, 0, width, width)

        super().__init__(
            path=path,
            parent=parent,
            position=pos,
            z_position=3,
            fill_color="#616161",
            stroke_color="white",
            alpha=0.9,
        )


class PromoteMenu:
    """The options shown when a Pawn needs to be promoted."""

    def __init__(self, parent: scene.Node, promotion_square: Square, square_shape: SquareShape) -> None:
        self.options: List[scene.SpriteNode] = []
        self.shapes: List[scene.ShapeNode] = []

        direction = promotion_square.piece.color.value

        promotion_options = ("queen", "knight", "rook", "bishop")

        for i, piece_name in enumerate(promotion_options, start=1):
            x, y = square_shape.position
            if HEIGHT - 16*SQUARE_SIZE < 0:
                # Can't fit the vertical piece selection on the screen => running for example on iPad's 4:3 screen.
                pos = ((i-2.5)*SQUARE_SIZE + WIDTH/2, 1.15*SQUARE_SIZE*direction + y)
            else:
                pos = (x, i * SQUARE_SIZE * direction + y)

            # Black menu is flipped 180 degrees.
            size = (SQUARE_SIZE * direction,) * 2
            
            self.shapes.append(
                scene.ShapeNode(
                    path=ui.Path.rect(0, 0, *size),
                    parent=parent,
                    position=pos,
                    fill_color="#eeeeee",
                )
            )
            sn = scene.SpriteNode(
                texture=get_image(promotion_square.piece, piece_name),
                parent=parent,
                position=pos,
                size=size,
            )
            sn.piece_name = piece_name
            self.options.append(sn)

    def __del__(self) -> None:
        for node in self.shapes + self.options:
            node.remove_from_parent()
 
                       
class InfoBox:
    """The box which shows player's captured pieces and his game clock."""
    
    def __init__(self, parent: scene.Node, player: Player) -> None:
        self.parent: scene.Node = parent
        self.player: Player = player
        self.nodes: List[scene.Node] = []
        self.y_offset: int = HEIGHT//2 - 4.5*SQUARE_SIZE
        self.text_font: Tuple[str, int] = ("Menlo", SQUARE_SIZE // 2)
        self.text_color: str = "white"
        
        if self.player.color == Color.WHITE:
            pos_value = (0, self.y_offset)
            pos_clock = (WIDTH, self.y_offset)
        else:
            pos_value = (WIDTH, HEIGHT - self.y_offset)
            pos_clock = (0, HEIGHT - self.y_offset)
        
        self.value_label: scene.LabelNode = scene.LabelNode(
            text="",
            parent=self.parent,
            font=self.text_font,
            position=pos_value,
            anchor_point=(0, 0.5),
            color=self.text_color,
        )
        self.clock_label: scene.LabelNode = scene.LabelNode(
            text="",
            parent=self.parent,
            font=self.text_font,
            position=pos_clock,
            anchor_point=(1, 0.5),
            color=self.text_color,
        )
        
        if self.player.color == Color.BLACK:
            self.value_label.rotation = math.pi
            self.clock_label.rotation = math.pi
        
    def __del__(self) -> None:
        for n in self.nodes:
            n.remove_from_parent()
        self.value_label.remove_from_parent()
        self.clock_label.remove_from_parent()
    
    def update_taken(self) -> None:
        """Called after every move when the taken Pieces of the Player need to be updated.""" 
        for n in self.nodes:
            n.remove_from_parent()
        
        self.value_label.text = f"{self.player.value_diff():+}"
        
        for i, piece in enumerate(self.player.taken_pieces):        
            per_row = 8
            y_offset = self.y_offset - SQUARE_SIZE//2 if i >= per_row else self.y_offset
                
            if self.player.color == Color.WHITE:
                pos = ((i % per_row) * SQUARE_SIZE // 2 + self.text_font[1] * 2.3, y_offset)
            else:
                pos = (WIDTH - (i % per_row) * SQUARE_SIZE // 2 - self.text_font[1] * 2.3, HEIGHT - y_offset)
                
            # Black menu is flipped 180 degrees.
            size = (SQUARE_SIZE/2 * self.player.color.value,) * 2
       
            self.nodes.append(
                scene.SpriteNode(
                    texture=get_image(piece, taken=True),
                    parent=self.parent,
                    position=pos,
                    size=size,
                )
            )
            
    def update_clock(self) -> None:
        """Called every 1/60s when the screen refreshes to update the Player's clock."""
        clock = self.player.read_clock()
        if clock > 3600:
            formatter = "%H:%M:%S"
        else:
            formatter = "%M:%S"
        
        if clock > 10:
            suffix = ""
        else:
            suffix = f"{clock:.2f}"[-3:]
                
        self.clock_label.text = time.strftime(formatter, time.gmtime(clock)) + suffix
