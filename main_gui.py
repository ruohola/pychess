"""The iOS specific GUI for the chess game.
This game uses 2 Pythonista specific Python modules made for iOS: `scene` and `ui`.
"""

import os
import pickle
import sys
from typing import Iterator, List, Optional

import scene

import game
from exceptions import InvalidMoveError
from gui_components import SquareShape, PieceSprite, SelectedShape, MoveShape, InfoBox, PromoteMenu
from gui_pause_menu import ContinueMenu, ResumeMenu
from player import Player
from time_control import TimeControl

CLOCK_TIME = 300
CLOCK_INCREMENT = 0
CLOCK_DELAY = 0

SAVE_FILE = os.path.join(os.path.dirname(__file__), ".save")

# Default is 256 on iOS, higher limit is needed for pickling.
sys.setrecursionlimit(1000)

            
class Main(scene.Scene):
    def __init__(self) -> None:        
        self.squares: List[SquareShape] = []
        self.pieces: List[PieceSprite] = []
        self.moves: List[MoveShape] = []

        self.fr: Optional[str] = None
        self.selected: Optional[SelectedShape] = None
        self.pause_menu: Optional[ResumeMenu] = None
        self.promote_menu: Optional[PromoteMenu] = None
        self.info_white: Optional[InfoBox] = None
        self.info_black: Optional[InfoBox] = None
        self.root: Optional[scene.Node] = None
        self.game: Optional[game.Game] = None
        self.player: Optional[Player] = None

        super().__init__()

    # Override
    def setup(self) -> None:
        # Set scene.Scene attributes
        self.background_color = "black"
        
        self.root = scene.Node(parent=self)
        
        self.new_game()
        if os.path.isfile(SAVE_FILE):
            self.show_resume_menu()       
            
    def new_game(self, loaded: Optional[game.Game] = None) -> None:        
        if loaded is None:            
            self.game = game.Game(TimeControl(CLOCK_TIME, CLOCK_INCREMENT, CLOCK_DELAY))
        else:
            self.game = loaded
            
        self.player = self.game.current_player
        
        self.info_white = InfoBox(self.root, self.game.white)
        self.info_black = InfoBox(self.root, self.game.black)

        for square in self.game.iter_squares():
            self.squares.append(SquareShape(self.root, square))

        self.render_pieces()
    
    def save_game(self) -> None:
        try:
            with open(SAVE_FILE, "wb") as f:
                pickle.dump(self.game, f)
        except AttributeError:
            pass
    
    def load_save(self) -> None:
        with open(SAVE_FILE, "rb") as f:
            loaded = pickle.load(f)
        self.delete_save()
        self.new_game(loaded=loaded)

    @staticmethod
    def delete_save() -> None:
        try:
            os.remove(SAVE_FILE)
        except FileNotFoundError:
            pass
        
    def render_pieces(self) -> None:
        self.clear_allowed_moves()
        for piece in self.pieces:
            piece.remove_from_parent()
        self.pieces.clear()

        for square in self.game.iter_squares():
            if square.piece:
                self.pieces.append(PieceSprite(self.root, square.piece))
        
        self.info_white.update_taken()
        self.info_black.update_taken()

    def clear_allowed_moves(self) -> None:
        for move in self.moves:
            move.remove_from_parent()
        self.moves.clear()
        if self.selected:
            self.selected.remove_from_parent()
        self.selected = None

    def render_allowed_moves(self) -> None:
        self.clear_allowed_moves()
        if not self.fr:
            return

        self.selected = SelectedShape(self.root, self.fr)

        try:
            for move in self.player.allowed_moves(self.fr):
                self.moves.append(MoveShape(self.root, move.square.coord))
        except InvalidMoveError:
            pass

    def select_promotion(self, touch: scene.Touch) -> None:
        option = self.square_from_touch(touch, self.promote_menu.options)
        if not option:
            return
        
        self.player.promote(option.piece_name)
        self.player = self.game.next_player()

        del self.promote_menu
        self.promote_menu = None
        self.render_pieces()

    def square_from_touch(self, touch: scene.Touch,
                          iterator: Iterator[scene.Node]) -> Optional[SquareShape]:

        pos = self.root.point_from_scene(touch.location)
        for square in iterator:
            if square.frame.contains_point(pos):
                return square

    # Override
    def touch_ended(self, touch: scene.Touch) -> None:
        if touch.location.x < 48 and touch.location.y > self.size.h - 48:
            self.show_resume_menu()
            return
            
        if self.player.promotion:
            return self.select_promotion(touch)

        square = self.square_from_touch(touch, self.squares)
        if not square:
            return
        pos = square.coord

        if self.game.color_of_piece(pos) == self.player.color:
            if self.fr == pos:
                # Selecting the same piece again deselects it.
                self.fr = None
            else:
                self.fr = pos
            self.render_allowed_moves()
        else:
            try:
                self.player.move(self.fr, pos)
            except InvalidMoveError:
                pass
            else:
                self.render_pieces()
                if self.player.promotion:
                    self.promote_menu = PromoteMenu(self, self.player.promotion, square)
                else:
                    self.player = self.game.next_player()
    
    def show_resume_menu(self) -> None:
        self.pause_menu = ResumeMenu()
        self.present_modal_scene(self.pause_menu)
                
    def show_continue_menu(self) -> None:
        self.player.stop_clock()
        self.pause_menu = ContinueMenu()
        self.present_modal_scene(self.pause_menu)
        
    def menu_button_selected(self, title: str) -> None:
        self.dismiss_modal_scene()
        if title == "New Game":
            self.new_game()
        elif title == "Resume Game":
            self.load_save()
        elif title == "Continue":
            self.player.start_clock()

    # Override
    def update(self) -> None:
        try:
            self.info_white.update_clock()
            self.info_black.update_clock()
        except AttributeError:
            # The info boxes were not created yet.
            pass
        
    # Override
    def pause(self) -> None:
        self.player.stop_clock()
        self.show_continue_menu()
        self.save_game()
        
    # Override
    def stop(self) -> None:
        self.pause()

    
if __name__ == "__main__":
    scene.run(Main(), scene.PORTRAIT)