"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


from typing import Any, Optional

import time

from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Elt
from lib_nadisplay_transformation import ND_Transformation
from lib_nadisplay_elt_sprite_of_atlas_texture import ND_Elt_Sprite_of_AtlasTexture



# ND_Elt_Sprite class implementation
class ND_Elt_AnimatedSprite(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            animations: dict[str, list[int | ND_Elt_Sprite_of_AtlasTexture]],
            animations_speed: dict[str, float],
            default_animation_speed: float = 0.1,
            default_animation: str = ""
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.animations: dict[str, list[Any]] = animations
        self.animations_speed: dict[str, float] = animations_speed
        #
        self.default_animation_speed: float = default_animation_speed
        #
        self.transformations = ND_Transformation()
        #
        self.current_animation: str = default_animation
        self.current_frame: int = 0
        self.delta_shift_time: float = 0
        self.last_update: float = time.time()
        #

    #
    def add_animation(self, animation_name: str, animation: list[int | ND_Elt_Sprite_of_AtlasTexture], animation_speed: float = -1, if_exists: str = "error") -> None:
        #
        if animation_name in self.animations:
            #
            if if_exists == "ignore":
                #
                return
            #
            elif if_exists == "error":
                #
                raise UserWarning(f"Error: tried to add animation \"{animation_name}\" but it already existed in AnimatedSprite {self.elt_id}")
        #
        self.animations[animation_name] = animation
        #
        if animation_speed > 0:
            self.animations_speed[animation_name] = animation_speed

    #
    def add_frame_to_animation(self, animation_name: str, animation_frame: int | ND_Elt_Sprite_of_AtlasTexture, if_not_exists: str = "create") -> None:
        #
        if animation_name not in self.animations:
            #
            if if_not_exists == "create":
                #
                self.animations[animation_name] = []
            #
            elif if_not_exists == "ignore":
                #
                return
            #
            elif if_not_exists == "error":
                #
                raise UserWarning(f"Error: tried to add a frame to animation \"{animation_name}\" but it doesn't exist in AnimatedSprite {self.elt_id}")
        #
        self.animations[animation_name].append(animation_frame)

    #
    def set_animation_speed(self, animation_name: str, animation_speed: float) -> None:
        #
        self.animations_speed[animation_name] = animation_speed

    #
    def change_animation(self, new_animation_name: str) -> None:
        #
        self.current_animation = new_animation_name
        #
        self.current_frame = 0
        self.last_update = time.time()

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        if self.current_animation not in self.animations:
            return

        #
        an_speed: float = self.default_animation_speed
        if self.current_animation in self.animations_speed:
            an_speed = self.animations_speed[self.current_animation]

        #
        t_now: float = time.time()
        #
        if t_now - self.last_update >= an_speed:
            #
            self.last_update = t_now
            #
            self.current_frame = (self.current_frame + 1) % (len(self.animations[self.current_animation]))

        #
        current_frame: Optional[int | ND_Elt_Sprite_of_AtlasTexture] = self.animations[self.current_animation][self.current_frame]

        # Drawing the background rect color or texture
        if current_frame is not None:
            #
            if isinstance(current_frame, int):
                #
                self.window.render_prepared_texture(current_frame, self.x, self.y, self.w, self.h, self.transformations)
            else:
                #
                old_position: ND_Position = current_frame.position
                old_transformations: ND_Transformation = current_frame.transformations
                #
                current_frame.position = self.position
                current_frame.transformations = self.transformations + current_frame.transformations
                #
                current_frame.render()
                #
                current_frame.position = old_position
                current_frame.transformations = old_transformations
