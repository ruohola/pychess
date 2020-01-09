"""Pause menu for the game GUI.
Modified from Pythonista's Examples/Games/game_menu.py
"""

from typing import List

import scene
import ui


class _ButtonNode(scene.SpriteNode):
    def __init__(self, title: str, *args, **kwargs) -> None:
        super().__init__("pzl:Button1", *args, **kwargs)
        button_font = ("Menlo", 25)
        self.title_label = scene.LabelNode(title, font=button_font, color="black", position=(0, 1), parent=self)
        self.title = title      

        
class _Menu(scene.Scene):

    def __init__(self, nodes: List[scene.Node]) -> None:
        self.nodes = nodes
        super().__init__()
        self.bg = scene.SpriteNode(color="black", parent=self)
        bg_shape = ui.Path.rounded_rect(0, 0, 240, len(nodes) * 64 + 70, 8)
        bg_shape.line_width = 4
        shadow = ((0, 0, 0, 0.35), 0, 0, 24)
        self.menu_bg = scene.ShapeNode(bg_shape, (1, 1, 1, 0.9), "black", shadow=shadow, parent=self)
        
        for i, node in enumerate(nodes):
            node.position = (0, i*64 - (len(nodes)-1)*32)
            if isinstance(node, scene.Node):
                self.menu_bg.add_child(node)
            else:
                self.menu_bg.view.add_subview(node)
            
        self.did_change_size()
        self.menu_bg.scale = 0
        self.bg.alpha = 0
        self.bg.run_action(scene.Action.fade_to(0.4))
        self.menu_bg.run_action(scene.Action.scale_to(1, 0.3, scene.TIMING_EASE_OUT_2))
        self.background_color = "white"
    
    def did_change_size(self) -> None:
        self.bg.size = self.size + (2, 2)
        self.bg.position = self.size/2
        self.menu_bg.position = self.size/2

    def touch_began(self, touch: scene.Touch) -> None:
        touch_loc = self.menu_bg.point_from_scene(touch.location)
        for node in self.nodes:
            if touch_loc in node.frame:
                node.texture = scene.Texture("pzl:Button2")

    def touch_ended(self, touch: scene.Touch) -> None:
        touch_loc = self.menu_bg.point_from_scene(touch.location)
        for node in self.nodes:
            node.texture = scene.Texture("pzl:Button1")

            if touch_loc in node.frame:
                if self.presenting_scene:
                    self.presenting_scene.menu_button_selected(node.title)
        

class _PauseMenu(_Menu):
    def __init__(self, button_titles: List[str]) -> None:
        buttons = []
        for i, title in enumerate(reversed(button_titles)):
            buttons.append(_ButtonNode(title))
        
        super().__init__(buttons)


class ResumeMenu(_PauseMenu):
    def __init__(self) -> None:
        super().__init__(["Resume Game", "New Game"])


class ContinueMenu(_PauseMenu):
    def __init__(self) -> None:
        super().__init__(["Continue", "New Game"])


if __name__ == "__main__":
    scene.run(ContinueMenu())
