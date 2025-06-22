"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


from typing import Callable, Any, Optional

import time

import math
import random

import numpy as np

import lib_nadisplay_events as nd_event
from lib_nadisplay_colors import ND_Color, cl
from lib_nadisplay_point import ND_Point
from lib_nadisplay_rects import ND_Rect
from lib_nadisplay_position import ND_Position, ND_Position_Constraints, ND_Position_Margins
from lib_nadisplay_point_3d import ND_Point_3D
from lib_nadisplay_utils import clamp, get_percentage_from_str, get_font_size
from lib_nadisplay_core import ND_Window, ND_Elt, ND_Scene
from lib_nadisplay_transformation import ND_Transformation
from lib_nadisplay_val import ND_Val  # type: ignore
from lib_nadisplay_core import ND_MainApp, ND_Display, ND_EventsManager  # type: ignore



# ND_Text class implementation
class ND_Text(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            text: str,
            font_name: Optional[str] = None,
            font_size: int = 24,
            font_color: ND_Color = cl("gray"),
            text_wrap: bool = False,
            text_h_align: str = "center",
            text_v_align: str = "center"
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        self.text: str = text
        self.font_name: Optional[str] = font_name
        self.font_size: int = font_size
        self.font_color: ND_Color = font_color
        #
        self.text_wrap: bool = text_wrap
        #
        self.text_h_align: str = text_h_align
        self.text_v_align: str = text_v_align
        #
        self.base_text_w: int = 0
        self.base_text_h: int = 0
        #
        self.base_text_w, self.base_text_h = get_font_size(self.text, self.font_size, font_ratio=0.5)
        #

    #
    def get_value(self) -> Any:
        #
        return self.text

    #
    def set_value(self, new_value: Any) -> None:
        #
        self.text = str(new_value)

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        x, y = self.x, self.y

        if self.w <= 0 or self.h <= 0:
            #
            # TODO: Taille indéterminée
            #
            pass
        else:
            #
            # TODO: Taille déterminée
            #
            if self.text_wrap:
                #
                # TODO: Calculer ce qui wrap ou pas
                #
                pass
            else:
                #
                if self.text_h_align == "center":
                    #
                    x=x + (self.w - self.base_text_w) // 2
                    #
                elif self.text_h_align == "right":
                    #
                    x=x + (self.w - self.base_text_w)
                    #
                #
                if self.text_v_align == "center":
                    #
                    y=y + (self.h - self.base_text_h) // 2
                    #
                elif self.text_v_align == "right":
                    #
                    y=y + (self.h - self.base_text_h)
                    #

        #
        self.window.draw_text(
                txt=self.text,
                x=x,
                y=y,
                font_name=self.font_name,
                font_size=self.font_size,
                font_color=self.font_color
        )


# ND_Clickable class implementation
class ND_Clickable(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            onclick: Optional[Callable[["ND_Clickable"], None]] = None,
            active: bool = True,
            block_events_below: bool = True
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        self.onclick: Optional[Callable[[ND_Clickable], None]] = onclick
        self.state: str = "normal"  # Can be "normal", "hover", or "clicked"
        self.mouse_bt_down_on_hover: bool = False
        self.block_events_below: bool = block_events_below
        #
        self.active: bool = active

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if not self.visible:
            self.state = "normal"
            return
        #
        if not self.clickable:
            self.state = "normal"
            return
        #
        if not self.active:
            self.state = "normal"
            return
        #
        if isinstance(event, nd_event.ND_EventMouseMotion):
            #
            if self.position.rect.contains_point(ND_Point(event.x, event.y)):
                self.state = "hover"
            else:
                self.state = "normal"
        #
        elif isinstance(event, nd_event.ND_EventMouseButtonDown):
            if event.button_id == 1:
                if self.position.rect.contains_point(ND_Point(event.x, event.y)):
                    #
                    self.state = "clicked"
                    #
                    self.mouse_bt_down_on_hover = True
                else:
                    self.mouse_bt_down_on_hover = False
        #
        elif isinstance(event, nd_event.ND_EventMouseButtonUp):
            if event.button_id == 1:
                #
                self.state = "hover" if self.position.rect.contains_point(ND_Point(event.x, event.y)) else "normal"
                #
                if self.state == "hover" and self.mouse_bt_down_on_hover:
                    #
                    if self.block_events_below:
                        event.blocked = True
                    #
                    if self.onclick:
                        self.onclick(self)
            #
            self.mouse_bt_down_on_hover = False


# ND_Rectangle class implementation
class ND_Rectangle(ND_Clickable):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            border_radius: int = 5,
            border: bool = True,
            onclick: Optional[Callable[["ND_Clickable"], None]] = None,
            mouse_active: bool = True,
            base_bg_color: Optional[ND_Color] = None,
            base_fg_color: Optional[ND_Color] = None,
            base_bg_texture: Optional[int | str] = None,
            hover_bg_color: Optional[ND_Color] = None,
            hover_fg_color: Optional[ND_Color] = None,
            hover_bg_texture: Optional[int | str] = None,
            clicked_bg_color: Optional[ND_Color] = None,
            clicked_fg_color: Optional[ND_Color] = None,
            clicked_bg_texture: Optional[int | str] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, onclick=onclick, active=mouse_active)
        self.base_bg_color: ND_Color = base_bg_color if base_bg_color is not None else cl("gray")
        self.base_fg_color: ND_Color = base_fg_color if base_fg_color is not None else cl("black")
        self.base_bg_texture: Optional[int] = self.window.prepare_image_to_render(base_bg_texture) if isinstance(base_bg_texture, str) else base_bg_texture
        self.hover_bg_color: ND_Color = hover_bg_color if hover_bg_color is not None else cl("dark gray")
        self.hover_fg_color: ND_Color = hover_fg_color if hover_fg_color is not None else cl("black")
        self.hover_bg_texture: Optional[int] = self.window.prepare_image_to_render(hover_bg_texture) if isinstance(hover_bg_texture, str) else hover_bg_texture
        self.clicked_bg_color: ND_Color = clicked_bg_color if clicked_bg_color is not None else cl("very dark gray")
        self.clicked_fg_color: ND_Color = clicked_fg_color if clicked_fg_color is not None else cl("black")
        self.clicked_bg_texture: Optional[int] = self.window.prepare_image_to_render(clicked_bg_texture) if isinstance(clicked_bg_texture, str) else clicked_bg_texture
        #
        self.border: bool = border
        self.border_radius: int = border_radius
        #

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        x, y = self.x, self.y

        #
        bg_color: ND_Color
        fg_color: ND_Color
        bg_texture: Optional[int]

        # Getting the right colors along the state
        if self.state == "normal":
            bg_color, fg_color, bg_texture = self.base_bg_color, self.base_fg_color, self.base_bg_texture
        elif self.state == "hover":
            bg_color, fg_color, bg_texture = self.hover_bg_color, self.hover_fg_color, self.hover_bg_texture
        else:  # clicked
            bg_color, fg_color, bg_texture = self.clicked_bg_color, self.clicked_fg_color, self.clicked_bg_texture

        # Drawing the background rect color or texture
        if bg_texture:
            self.window.render_prepared_texture(bg_texture, x, y, self.w, self.h)
        else:
            if not self.border and self.border_radius <= 0:
                self.window.draw_filled_rect(x, y, self.w, self.h, bg_color)
            elif not self.border:
                self.window.draw_rounded_rect(x, y, self.w, self.h, self.border_radius, bg_color, cl((0, 0, 0, 0)))
            else:
                self.window.draw_rounded_rect(x, y, self.w, self.h, self.border_radius, bg_color, fg_color)


# ND_Sprite class implementation
class ND_Sprite(ND_Clickable):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            onclick: Optional[Callable[["ND_Clickable"], None]] = None,
            mouse_active: bool = True,
            base_texture: Optional[int | str] = None,
            hover_texture: Optional[int | str] = None,
            clicked_texture: Optional[int | str] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, onclick=onclick, active=mouse_active)
        self.base_texture: Optional[int | str] = base_texture
        self.hover_texture: Optional[int | str] = self.window.prepare_image_to_render(hover_texture) if isinstance(hover_texture, str) else hover_texture
        self.clicked_texture: Optional[int | str] = self.window.prepare_image_to_render(clicked_texture) if isinstance(clicked_texture, str) else clicked_texture
        #
        self.transformations = ND_Transformation()

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        texture: Optional[int] = None

        # Getting the right colors along the state
        if self.state == "hover" and self.hover_texture is not None:
            if isinstance(self.hover_texture, str):
                self.hover_texture = self.window.prepare_image_to_render(self.hover_texture)
            #
            texture = self.hover_texture
        elif self.state == "clicked" and self.clicked_texture is not None:
            if isinstance(self.clicked_texture, str):
                self.clicked_texture = self.window.prepare_image_to_render(self.clicked_texture)
            #
            texture = self.clicked_texture
        #
        if texture is None:
            if isinstance(self.base_texture, str):
                self.base_texture = self.window.prepare_image_to_render(self.base_texture)
            #
            texture = self.base_texture

        # Drawing the background rect color or texture
        if texture is not None:
            # print(f"DEBUG | rendering texture id {texture} at x={self.x}, y={self.y}, w={self.w}, h={self.h}")
            self.window.render_prepared_texture(texture, self.x, self.y, self.w, self.h, self.transformations)


#
class ND_AtlasTexture:
    #
    def __init__(self, window: ND_Window, texture_atlas_path: str, tiles_size: ND_Point = ND_Point(32, 32)) -> None:
        #
        self.window: ND_Window = window
        #
        self.texture_atlas_path: str = texture_atlas_path
        #
        self.texture_atlas: Optional[int] = None
        #
        self.tiles_size: ND_Point = tiles_size
        self.texture_dim: ND_Point = ND_Point(-1, -1)

    #
    def render_texture_at_position(self,
                                    at_win_x: int, at_win_y: int, at_win_w: int, at_win_h: int,
                                    tile_x: int, tile_y: int, nb_tiles_w: int = 1, nb_tiles_h: int = 1,
                                    transformations: ND_Transformation = ND_Transformation()
        ) -> None:

        #
        if self.texture_atlas is None:
            #
            self.texture_atlas = self.window.prepare_image_to_render(self.texture_atlas_path)
            self.texture_dim = self.window.get_prepared_texture_size(self.texture_atlas)

        #
        src_x: int = self.tiles_size.x * tile_x
        src_y: int = self.tiles_size.y * tile_y
        src_w: int = self.tiles_size.x * nb_tiles_w
        src_h: int = self.tiles_size.y * nb_tiles_h

        #
        src_x = clamp(src_x, 0, self.texture_dim.x)
        src_y = clamp(src_y, 0, self.texture_dim.y)
        src_w = clamp(src_w, 0, self.texture_dim.x-src_x)
        src_h = clamp(src_h, 0, self.texture_dim.y-src_y)

        #
        self.window.render_part_of_prepared_texture(
                self.texture_atlas,
                at_win_x, at_win_y, at_win_w, at_win_h,
                src_x, src_y, src_w, src_h,
                transformations
        )


#
class ND_Sprite_of_AtlasTexture(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            atlas_texture: ND_AtlasTexture,
            tile_x: int,
            tile_y: int,
            nb_tiles_x: int = 1,
            nb_tiles_y: int = 1
        ) -> None:
        #
        super().__init__(window, elt_id, position)
        #
        self.atlas_texture: ND_AtlasTexture = atlas_texture
        #
        self.tile_x: int = tile_x
        self.tile_y: int = tile_y
        self.nb_tiles_x: int = nb_tiles_x
        self.nb_tiles_y: int = nb_tiles_y
        #
        self.transformations = ND_Transformation()

    #
    def render(self) -> None:
        #
        self.atlas_texture.render_texture_at_position(
                self.x, self.y, self.w, self.h,
                self.tile_x, self.tile_y, self.nb_tiles_x, self.nb_tiles_y,
                self.transformations
        )


# ND_Sprite class implementation
class ND_AnimatedSprite(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            animations: dict[str, list[int | ND_Sprite_of_AtlasTexture]],
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
    def add_animation(self, animation_name: str, animation: list[int | ND_Sprite_of_AtlasTexture], animation_speed: float = -1, if_exists: str = "error") -> None:
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
    def add_frame_to_animation(self, animation_name: str, animation_frame: int | ND_Sprite_of_AtlasTexture, if_not_exists: str = "create") -> None:
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
        current_frame: Optional[int | ND_Sprite_of_AtlasTexture] = self.animations[self.current_animation][self.current_frame]

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


# ND_Button class implementation
class ND_Button(ND_Clickable):

    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            onclick: Optional[Callable[[ND_Clickable], None]],
            text: str,
            mouse_active: bool = True,
            font_name: Optional[str] = None,
            font_size: int = 24,
            border_radius: int = 5,
            border: bool = True,
            base_bg_color: Optional[ND_Color] = None,
            base_fg_color: Optional[ND_Color] = None,
            base_bg_texture: Optional[int | str] = None,
            hover_bg_color: Optional[ND_Color] = None,
            hover_fg_color: Optional[ND_Color] = None,
            hover_bg_texture: Optional[int | str] = None,
            clicked_bg_color: Optional[ND_Color] = None,
            clicked_fg_color: Optional[ND_Color] = None,
            clicked_bg_texture: Optional[int | str] = None,
            texture_transformations: ND_Transformation = ND_Transformation()
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, onclick=onclick, active=mouse_active)
        self.text: str = text
        self.font_name: Optional[str] = font_name
        self.font_size: int = font_size
        self.base_bg_color: ND_Color = base_bg_color if base_bg_color is not None else cl("gray")
        self.base_fg_color: ND_Color = base_fg_color if base_fg_color is not None else cl("black")
        self.base_bg_texture: Optional[int] = self.window.prepare_image_to_render(base_bg_texture) if isinstance(base_bg_texture, str) else base_bg_texture
        self.hover_bg_color: ND_Color = hover_bg_color if hover_bg_color is not None else cl("dark gray")
        self.hover_fg_color: ND_Color = hover_fg_color if hover_fg_color is not None else cl("black")
        self.hover_bg_texture: Optional[int] = self.window.prepare_image_to_render(hover_bg_texture) if isinstance(hover_bg_texture, str) else hover_bg_texture
        self.clicked_bg_color: ND_Color = clicked_bg_color if clicked_bg_color is not None else cl("very dark gray")
        self.clicked_fg_color: ND_Color = clicked_fg_color if clicked_fg_color is not None else cl("black")
        self.clicked_bg_texture: Optional[int] = self.window.prepare_image_to_render(clicked_bg_texture) if isinstance(clicked_bg_texture, str) else clicked_bg_texture
        #
        self.border: bool = border
        self.border_radius: int = border_radius
        #
        self.base_text_w: int = 0
        self.base_text_h: int = 0
        #
        self.base_text_w, self.base_text_h = get_font_size(self.text, self.font_size, font_ratio=0.5)
        #
        self.texture_transformations: ND_Transformation = texture_transformations

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        x, y = self.x, self.y

        #
        bg_color: ND_Color
        fg_color: ND_Color
        bg_texture: Optional[int]

        # Getting the right colors along the state
        if self.state == "normal":
            bg_color, fg_color, bg_texture = self.base_bg_color, self.base_fg_color, self.base_bg_texture
        elif self.state == "hover":
            bg_color, fg_color, bg_texture = self.hover_bg_color, self.hover_fg_color, self.hover_bg_texture if self.hover_bg_texture is not None else self.base_bg_texture
        else:  # clicked
            bg_color, fg_color, bg_texture = self.clicked_bg_color, self.clicked_fg_color, self.clicked_bg_texture if self.clicked_bg_texture is not None else self.base_bg_texture

        # Drawing the background rect color or texture
        if bg_texture:
            self.window.render_prepared_texture(bg_texture, x, y, self.w, self.h, transformations=self.texture_transformations)
        else:
            if not self.border and self.border_radius <= 0:
                self.window.draw_filled_rect(x, y, self.w, self.h, bg_color)
            elif not self.border:
                self.window.draw_rounded_rect(x, y, self.w, self.h, self.border_radius, bg_color, cl((255, 0, 0, 0)))
            else:
                self.window.draw_rounded_rect(x, y, self.w, self.h, self.border_radius, bg_color, fg_color)

        #
        self.window.draw_text(
                txt=self.text,
                x=x + (self.w - self.base_text_w) // 2,
                y=y + (self.h - self.base_text_h) // 2,
                font_name=self.font_name,
                font_size=self.font_size,
                font_color=fg_color
        )


# ND_H_ScrollBar class implementation
class ND_H_ScrollBar(ND_Elt):
    #
    def __init__(
                    self,
                    window: ND_Window,
                    elt_id: str,
                    position: ND_Position,
                    content_width: int,
                    bg_cl: ND_Color = cl((10, 10, 10)),
                    fg_cl: ND_Color = cl("white"),
                    on_value_changed: Optional[Callable[["ND_H_ScrollBar", float], None]] = None
        ) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.on_value_changed: Optional[Callable[[ND_H_ScrollBar, float], None]] = on_value_changed
        #
        self.content_width: int = content_width
        self.scroll_position: float = 0
        self.dragging: bool = False
        self.prep_dragging: bool = False
        #
        self.bg_cl: ND_Color = bg_cl
        self.fg_cl: ND_Color = fg_cl

    #
    def get_scroll_ratio(self) -> float:
        #
        return self.scroll_position / float(self.content_width)

    #
    @property
    def thumb_width(self) -> int:
        return max(20, int(self.w * (self.w / self.content_width)))

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        # Draw background
        self.window.draw_filled_rect(self.x, self.y, self.w, self.h, self.bg_cl)
        #
        self.window.draw_unfilled_rect(self.x, self.y, self.w, self.h, self.fg_cl)

        # Draw thumb
        thumb_x = self.x + int(self.scroll_position * (self.w - self.thumb_width) / (self.content_width - self.w))
        self.window.draw_filled_rect(thumb_x, self.y, self.thumb_width, self.h, self.fg_cl)

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if isinstance(event, nd_event.ND_EventMouse):
            #
            if not self.position.rect.contains_point(ND_Point(event.x, event.y)):
                self.prep_dragging = False
                self.dragging = False
                return
            #
            if isinstance(event, nd_event.ND_EventMouseButtonDown):
                if event.button_id == 1:
                    self.prep_dragging = True
            #
            elif isinstance(event, nd_event.ND_EventMouseButtonUp):
                if event.button_id == 1:
                    if self.dragging:
                        self.dragging = False
                    else:
                        relative_x = event.x - self.x
                        self.scroll_position = max(0, min(self.content_width - self.w,
                                                    int(relative_x * self.content_width / self.w)))
                        #
                        if self.on_value_changed is not None:
                            self.on_value_changed(self, self.scroll_position)

            #
            elif isinstance(event, nd_event.ND_EventMouseMotion):
                if self.dragging or self.prep_dragging:
                    #
                    if self.prep_dragging:
                        self.dragging = True
                        self.prep_dragging = False
                    #
                    relative_x = event.x - self.x
                    self.scroll_position = max(0, min(self.content_width - self.w,
                                                    int(relative_x * self.content_width / self.w)))
                    #
                    if self.on_value_changed is not None:
                        self.on_value_changed(self, self.scroll_position)


# ND_V_ScrollBar class implementation
class ND_V_ScrollBar(ND_Elt):
    #
    def __init__(
                    self,
                    window: ND_Window,
                    elt_id: str,
                    position: ND_Position,
                    content_height: int,
                    fg_color: ND_Color = cl("white"),
                    bg_color: ND_Color = cl("dark gray"),
                    on_value_changed: Optional[Callable[["ND_V_ScrollBar", float], None]] = None
        ) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.on_value_changed: Optional[Callable[[ND_V_ScrollBar, float], None]] = on_value_changed
        #
        self.content_height = content_height
        self.scroll_position = 0
        self.dragging = False
        #
        self.fg_color: ND_Color = fg_color
        self.bg_color: ND_Color = bg_color

    #
    def get_scroll_ratio(self) -> float:
        #
        return self.scroll_position / float(self.content_height)

    @property
    def thumb_height(self) -> int:
        return clamp(int(self.w * (self.w / self.content_height)), 2, 20)

    #
    def render(self) -> None:
        if not self.visible:
            return

        # Draw background
        self.window.draw_filled_rect(self.x, self.y, self.w, self.h, self.bg_color)

        # Draw thumb
        thumb_y = self.y + int(self.scroll_position * (self.h - self.thumb_height) / (self.content_height))
        self.window.draw_filled_rect(self.x, thumb_y, self.w, self.thumb_height, self.fg_color)

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if isinstance(event, nd_event.ND_EventMouseButtonDown):
            if event.button_id == 1:
                if self.position.rect.contains_point(ND_Point(event.x, event.y)):
                    #
                    self.scroll_position = clamp(int(((event.y - self.y) / self.h) * self.content_height), 0, self.content_height)
                    #
                    if self.on_value_changed is not None:
                        self.on_value_changed(self, self.scroll_position)
                    #
                    event.blocked = True
                    #
                    self.dragging = True
                else:
                    self.dragging = False
        #
        elif isinstance(event, nd_event.ND_EventMouseButtonUp):
            if event.button_id == 1:
                self.dragging = False
        #
        elif isinstance(event, nd_event.ND_EventMouseMotion):
            if self.dragging:
                relative_y = event.y - self.y
                self.scroll_position = max(0, min(self.content_height - self.h,
                                                int(relative_y * self.content_height / self.h)))
                #
                if self.on_value_changed is not None:
                    self.on_value_changed(self, self.scroll_position)


#
class ND_LineEdit(ND_Elt):
    def __init__(
        self,
        window: ND_Window,
        elt_id: str,
        position: ND_Position,
        text: str = "",
        place_holder: str = "",
        max_text_length: int = -1,
        mouse_active: bool = True,
        font_name: Optional[str] = None,
        font_size: int = 24,
        border_radius: int = 5,
        border: bool = True,
        base_bg_color: Optional[ND_Color] = None,
        base_fg_color: Optional[ND_Color] = None,
        hover_bg_color: Optional[ND_Color] = None,
        hover_fg_color: Optional[ND_Color] = None,
        clicked_bg_color: Optional[ND_Color] = None,
        clicked_fg_color: Optional[ND_Color] = None,
        characters_restrictions: Optional[set[str]] = None,
        password_mode: bool = False,
        on_line_edit_validated: Optional[Callable[["ND_LineEdit", str], None]] = None,
        on_line_edit_escaped: Optional[Callable[["ND_LineEdit"], None]] = None
    ) -> None:
        super().__init__(window=window, elt_id=elt_id, position=position)
        self.state: str = "normal"
        self.text: str = text
        self.place_holder: str = place_holder
        self.font_name: Optional[str] = font_name
        self.font_size: int = font_size
        self.base_bg_color: ND_Color = base_bg_color if base_bg_color else cl("gray")
        self.base_fg_color: ND_Color = base_fg_color if base_fg_color else cl("black")
        self.hover_bg_color: ND_Color = hover_bg_color if hover_bg_color else cl("dark gray")
        self.hover_fg_color: ND_Color = hover_fg_color if hover_fg_color else cl("black")
        self.clicked_bg_color: ND_Color = clicked_bg_color if clicked_bg_color else cl("very dark gray")
        self.clicked_fg_color: ND_Color = clicked_fg_color if clicked_fg_color else cl("black")
        self.border: bool = border
        self.border_radius: int = border_radius
        self.cursor: int = len(text)
        self.cursor_width: int = 2
        self.cursor_height: int = self.font_size
        self.focused: bool = False
        self.max_text_length: int = max_text_length
        self.characters_restrictions: Optional[set[str]] = characters_restrictions   # Do not accept others character that theses
        self.password_mode: bool = password_mode
        self.on_line_edit_validated: Optional[Callable[[ND_LineEdit, str], None]] = on_line_edit_validated
        self.on_line_edit_escaped: Optional[Callable[[ND_LineEdit], None]] = on_line_edit_escaped

        # Scrollbar-related
        self.scrollbar_height: int = 10
        self.full_text_width: int = 0
        self.scroll_offset: int = 0
        self.scrollbar: ND_H_ScrollBar = ND_H_ScrollBar(
            window = self.window,
            elt_id = f"scrollbar_{self.elt_id}",
            position = ND_Position(self.x, self.y + self.h - self.scrollbar_height, self.w, self.scrollbar_height),
            content_width = self.window.get_text_size_with_font(self.text, self.font_size, self.font_name).x
        )

    #
    def set_text(self, txt: str) -> None:
        #
        self.text = txt
        self.cursor = len(self.text)

    #
    def get_value(self) -> Any:
        #
        return self.text

    #
    def set_value(self, new_value: Any) -> None:
        #
        self.set_text(txt = str(new_value))

    #
    def render(self) -> None:
        if not self.visible:
            return

        # Determine background and text color based on the state
        bg_color = self.base_bg_color
        fg_color = self.base_fg_color
        if self.state == "hover":
            bg_color = self.hover_bg_color
            fg_color = self.hover_fg_color
        elif self.state == "clicked":
            bg_color = self.clicked_bg_color
            fg_color = self.clicked_fg_color

        # Draw the background rectangle
        if self.border:
            self.window.draw_rounded_rect(
                self.x, self.y, self.w, self.h, self.border_radius, bg_color, fg_color
            )
        else:
            self.window.draw_filled_rect(self.x, self.y, self.w, self.h, bg_color)

        # Determine the visible portion of the text
        render_text = self.text if self.text else self.place_holder
        text_color = fg_color if self.text else cl("light gray")

        self.full_text_width = self.window.get_text_size_with_font(render_text, self.font_size, self.font_name).x

        #
        if self.scrollbar.scroll_position > 0:
            size_hidden: int
            count_hidden: int
            size_hidden, count_hidden = self.window.get_count_of_renderable_chars_fitting_given_width(txt=render_text, given_width=int(self.scrollbar.scroll_position), font_name=self.font_name, font_size=self.font_size)
            #
            if count_hidden > 0:
                render_text = render_text[count_hidden:]
                self.scroll_offset = int(self.scrollbar.scroll_position) - size_hidden
        else:
            self.scroll_offset = 0

        visible_text = render_text

        visible_text_width: int = self.full_text_width
        if self.full_text_width > self.w:
            while visible_text_width > self.w:
                visible_text = visible_text[1:]
                visible_text_width = self.window.get_text_size_with_font(visible_text, self.font_size, self.font_name).x

        # TODO: correct the text that is displayed and visible


        # Render the text
        self.window.draw_text(
            txt=visible_text,
            x=self.x + 5 - self.scroll_offset,
            y=self.y + (self.h - self.cursor_height) // 2,
            font_size=self.font_size,
            font_color=text_color,
            font_name=self.font_name,
        )

        # Render the cursor if focused
        if self.focused and len(self.text) >= self.cursor:

            txt_before_cursor_width: int = self.window.get_text_size_with_font(self.text[: self.cursor], self.font_size, self.font_name).x

            cursor_x = self.x + 5 + txt_before_cursor_width - self.scroll_offset
            self.window.draw_filled_rect(cursor_x, self.y + 5, self.cursor_width, self.cursor_height, fg_color)

        # Render horizontal scrollbar if necessary
        if self.full_text_width > self.w:
            self.scrollbar.render()

    #
    def write(self, char: str) -> None:
        #
        if self.max_text_length > 0 and len(self.text) + len(char) > self.max_text_length:
            return
        #
        self.text = self.text[: self.cursor] + char + self.text[self.cursor :]
        self.cursor += len(char)
        #
        self.full_text_width = self.window.get_text_size_with_font(self.text, self.font_size, self.font_name).x
        self.scrollbar.content_width = self.full_text_width

    #
    def print_debug_infos(self) -> None:
        #
        print(f"\nDEBUG | line_edit={self.elt_id} | visible={self.visible} | focused={self.focused} | text={self.text} | cursor={self.cursor} | full_text_width={self.full_text_width} | scroll_position={self.scrollbar.scroll_position}\n")

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if isinstance(event, nd_event.ND_EventKeyDown) and event.key == "F3":
            self.print_debug_infos()
        #
        if not self.visible:
            return
        #
        if isinstance(event, nd_event.ND_EventMouse):
            if event.x >= self.x and event.x <= self.x + self.w and event.y >= self.y and event.y <= self.y + self.h:
                if isinstance(event, nd_event.ND_EventMouseButtonDown):
                    if self.state == "clicked":
                        # TODO: move the cursor to the closest place possible of the click
                        pass
                    else:
                        self.state = "clicked"
                        self.focused = True
                elif isinstance(event, nd_event.ND_EventMouseMotion):
                    self.state = "hover"
            elif isinstance(event, nd_event.ND_EventMouseButtonDown):
                self.state = "normal"
                self.focused = False
                #
                if self.on_line_edit_escaped is not None:
                    self.on_line_edit_escaped(self)
            else:
                self.state = "normal"

            # Delegate scrollbar events
            if self.full_text_width > self.w:
                self.scrollbar.handle_event(event)
                self.scroll_offset = int(self.scrollbar.get_scroll_ratio() * (self.full_text_width - self.w))

        elif isinstance(event, nd_event.ND_EventKeyDown) and self.focused:
            #
            shift_pressed: bool = self.window.main_app.events_manager.is_shift_pressed()
            #
            # TODO: complete with all the keys, for instance the numpad keys, etc...
            if event.key == "escape":
                self.state = "normal"
                self.focused = False
                #
                if self.on_line_edit_escaped is not None:
                    self.on_line_edit_escaped(self)
            elif event.key == "return":
                self.state = "normal"
                self.focused = False
                #
                if self.on_line_edit_validated is not None:
                    self.on_line_edit_validated(self, self.text)
            #
            elif event.key == "backspace" and self.cursor > 0:
                self.text = self.text[: self.cursor - 1] + self.text[self.cursor :]
                self.cursor -= 1
                self.full_text_width = self.window.get_text_size_with_font(self.text, self.font_size, self.font_name).x
                self.scrollbar.content_width = self.full_text_width
            #
            elif event.key == "left arrow" and self.cursor > 0:
                self.cursor -= 1
            #
            elif event.key == "right arrow" and self.cursor < len(self.text):
                self.cursor += 1
                text_width = self.window.get_text_size_with_font(self.text[:self.cursor], self.font_size, self.font_name).x
                if text_width - self.scroll_offset > self.w:
                    self.scroll_offset = text_width - self.w
            #
            elif len(event.key) == 1:
                if shift_pressed:
                    self.write(event.key.upper())
                else:
                    self.write(event.key)
            #
            elif event.key == "espace":
                self.write(" ")
            #
            elif event.key == "semicolon":
                if shift_pressed:
                    self.write(".")
                else:
                    self.write(",")

            # Update scrollbar position
            if self.full_text_width > self.w:
                self.scrollbar.scroll_position = self.scroll_offset / (self.full_text_width - self.w)
            #
            # print(f"DEBUG | event = {event}")
            # self.print_debug_infos()


# ND_Checkbox
class ND_Checkbox(ND_Elt):
    def __init__(
        self,
        window: ND_Window,
        elt_id: str,
        position: ND_Position,
        checked: bool = False,
        on_pressed: Optional[Callable[["ND_Checkbox"], None]] = None
    ) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.on_pressed: Optional[Callable[["ND_Checkbox"], None]] = on_pressed
        #
        self.checked: bool = checked
        #
        self.bt_checked: ND_Button = ND_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_bt_checked",
            position=self.position,
            onclick=self.on_bt_checked_pressed,
            text="v",
            base_fg_color=cl("dark green"),
            hover_fg_color=cl("green")
            # TODO: style
        )
        #
        self.bt_unchecked: ND_Button = ND_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_bt_unchecked",
            position=self.position,
            onclick=self.on_bt_unchecked_pressed,
            text="x",
            base_fg_color=cl("dark red"),
            hover_fg_color=cl("red")
            # TODO: style
        )

    #
    def get_value(self) -> Any:
        #
        return self.checked

    #
    def set_value(self, new_value: Any) -> None:
        #
        self.checked = bool(new_value)

    #
    def render(self) -> None:
        if self.checked:
            self.bt_checked.render()
        else:
            self.bt_unchecked.render()

    #
    def on_bt_checked_pressed(self, clickable: ND_Clickable) -> None:
        #
        self.checked = False
        #
        self.bt_checked.visible = False
        self.bt_unchecked.visible = True
        #
        if self.on_pressed is not None:
            self.on_pressed(self)

    #
    def on_bt_unchecked_pressed(self, clickable: ND_Clickable) -> None:
        #
        self.checked = True
        #
        self.bt_checked.visible = True
        self.bt_unchecked.visible = False
        #
        if self.on_pressed is not None:
            self.on_pressed(self)

    #
    def is_checked(self) -> bool:
        return self.checked

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if not self.visible:
            return
        #
        if self.checked:
            self.bt_checked.handle_event(event)
        else:
            self.bt_unchecked.handle_event(event)


# ND_NumberInput
class ND_NumberInput(ND_Elt):
    def __init__(
        self,
        window: ND_Window,
        elt_id: str,
        position: ND_Position,
        value: float = 0,
        min_value: float = 0,
        max_value: float = 100,
        step: float = 1,
        digits_after_comma: int = 0,
        on_new_value_validated: Optional[Callable[["ND_NumberInput", float], None]] = None
    ) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.on_new_value_validated: Optional[Callable[["ND_NumberInput", float], None]] = on_new_value_validated
        #
        self.min_value: float = min_value
        self.max_value: float = max_value
        self.step: float = step
        self.digits_after_comma: int = digits_after_comma
        if self.digits_after_comma > 0:
            self.value = round(clamp(value, self.min_value, self.max_value), self.digits_after_comma)
        else:
            self.value = int(clamp(value, self.min_value, self.max_value))
        #
        self.main_row_container: ND_Container = ND_Container(
            window=self.window,
            elt_id=f"{self.elt_id}_main_row_container",
            position=self.position,
            element_alignment="row"
        )
        #
        self.line_edit: ND_LineEdit = ND_LineEdit(
            window=self.window,
            elt_id=f"{self.elt_id}_line_edit",
            position=ND_Position_Container(w="80%", h="100%", container=self.main_row_container),
            text=str(self.value),
            place_holder="value",
            font_name="FreeSans",
            font_size=24,
            on_line_edit_escaped=self.on_line_edit_escaped,
            on_line_edit_validated=self.on_line_edit_validated
        )
        #
        self.main_row_container.add_element(self.line_edit)
        #
        self.col_bts_container: ND_Container = ND_Container(
            window=self.window,
            elt_id=f"{self.elt_id}_col_bts_container",
            position=ND_Position_Container(w="20%", h="100%", container=self.main_row_container)
        )
        self.main_row_container.add_element(self.col_bts_container)
        #
        self.bt_up: ND_Button = ND_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_bt_up",
            position=ND_Position_Container(w="100%", h="50%", container=self.col_bts_container),
            onclick=self.on_bt_up_pressed,
            text="^",
            font_name="FreeSans",
            font_size=12
        )
        self.col_bts_container.add_element(self.bt_up)
        #
        self.bt_down: ND_Button = ND_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_bt_down",
            position=ND_Position_Container(w="100%", h="50%", container=self.col_bts_container),
            onclick=self.on_bt_down_pressed,
            text="v",
            font_name="FreeSans",
            font_size=12
        )
        self.col_bts_container.add_element(self.bt_down)


    #
    def get_value(self) -> Any:
        #
        return self.value

    #
    def set_value(self, new_value: Any) -> None:
        #
        self.value = int(new_value)

    #
    def update_layout(self) -> None:
        self.main_row_container.update_layout()

    #
    def render(self) -> None:
        #
        if not self.visible:
            return
        #
        self.main_row_container.render()
        #

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        self.line_edit.handle_event(event)
        self.bt_up.handle_event(event)
        self.bt_down.handle_event(event)

    #
    def on_bt_up_pressed(self, clickable: ND_Clickable) -> None:
        #
        new_value: float = self.value + self.step
        #
        if self.digits_after_comma > 0:
            self.value = round(clamp(new_value, self.min_value, self.max_value), self.digits_after_comma)
        else:
            self.value = int(clamp(new_value, self.min_value, self.max_value))
        #
        self.line_edit.set_text(str(self.value))

    #
    def on_bt_down_pressed(self, clickable: ND_Clickable) -> None:
        #
        new_value: float = self.value - self.step
        #
        if self.digits_after_comma > 0:
            self.value = round(clamp(new_value, self.min_value, self.max_value), self.digits_after_comma)
        else:
            self.value = int(clamp(new_value, self.min_value, self.max_value))
        #
        self.line_edit.set_text(str(self.value))

    #
    def on_line_edit_validated(self, line_edit: ND_LineEdit, value: str) -> None:
        #
        try:
            new_value: float = float(self.line_edit.text)
            #
            if self.digits_after_comma > 0:
                self.value = round(clamp(new_value, self.min_value, self.max_value), self.digits_after_comma)
            else:
                self.value = int(clamp(new_value, self.min_value, self.max_value))
        except Exception as _:
            pass
        finally:
            self.line_edit.set_text(str(self.value))
            #
            if self.on_new_value_validated is not None:
                #
                self.on_new_value_validated(self, self.value)

    #
    def on_line_edit_escaped(self, line_edit: ND_LineEdit) -> None:
        #
        value: str = self.line_edit.text
        #
        self.on_line_edit_validated(line_edit, value)
        #
        # self.line_edit.set_text(str(self.value))


# ND_SelectOptions
class ND_SelectOptions(ND_Elt):
    def __init__(
        self,
        window: ND_Window,
        elt_id: str,
        position: ND_Position,
        value: str,
        options: set[str],
        option_list_buttons_height: int = 300,
        on_value_selected: Optional[Callable[["ND_SelectOptions", str], None]] = None,
        font_size: int = 24,
        font_name: Optional[str] = None
    ) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.font_name: Optional[str] = font_name
        self.font_size: int = font_size
        #
        self.on_value_selected: Optional[Callable[[ND_SelectOptions, str], None]] = on_value_selected
        #
        self.value: str = value
        self.options: set[str] = options
        #
        self.options_bts: dict[str, ND_Button] = {}
        #
        self.option_list_buttons_height: int = option_list_buttons_height
        #
        self.state: str = "base"  # "base" or "selection"
        #
        # 1st side: the main button to show which element is selected, and if clicked, hide itself and show the 2nd part of it
        #
        self.main_button: ND_Button = ND_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_main_button",
            position=self.position,
            text=self.value,
            onclick=self.on_main_button_clicked,
            font_name=font_name,
            font_size=font_size
        )
        #
        # 2nd side: the buttons list to select a new option / see all the available options
        #
        self.bts_options_container: ND_Container = ND_Container(
            window=self.window,
            elt_id=f"{self.elt_id}_bts_options_container",
            position=ND_Position(x=self.x, y=self.y, w=self.w, h=self.option_list_buttons_height),
            element_alignment="col",
            scroll_h=True,
            overflow_hidden=True
        )
        self.bts_options_container.visible = False
        #
        option: str
        for option in self.options:
            self.options_bts[option] = ND_Button(
                window=self.window,
                elt_id=f"{self.elt_id}_bt_option_{option}",
                position=ND_Position_Container(w=self.w, h=self.h, container=self.bts_options_container),
                text=option,
                onclick=lambda x, option=option: self.on_option_button_clicked(option), # type: ignore
                font_name=self.font_name,
                font_size=self.font_size
            )
            self.bts_options_container.add_element(self.options_bts[option])

    #
    def get_value(self) -> Any:
        #
        return self.value

    #
    def set_value(self, new_value: Any) -> None:
        #
        if new_value in self.options:
            #
            self.value = new_value

    #
    def render(self) -> None:
        #
        if self.state == "base":
            self.main_button.render()
        else:
            self.bts_options_container.render()

    #
    def update_layout(self) -> None:
        #
        self.bts_options_container.position = ND_Position(x=self.x, y=self.y, w=self.w, h=self.option_list_buttons_height)
        #
        self.bts_options_container.update_layout()

    #
    def add_option(self, option_value: str) -> None:
        #
        if option_value in self.options:
            return
        #
        self.options.add(option_value)

        #
        self.options_bts[option_value] = ND_Button(
            window=self.window,
            elt_id=f"{self.elt_id}_bt_option_{option_value}",
            position=ND_Position_Container(w=self.w, h=self.h, container=self.bts_options_container),
            text=option_value,
            onclick=lambda x, option=option_value: self.on_option_button_clicked(option), # type: ignore
            font_name=self.font_name,
            font_size=self.font_size
        )
        self.bts_options_container.add_element(self.options_bts[option_value])

        #
        self.update_layout()

    #
    def remove_option(self, option_value: str, new_value: Optional[str] = None) -> None:
        #
        if option_value not in self.options:
            return
        #
        if len(self.options) == 1:  # On ne veut pas ne plus avoir d'options possibles
            return
        #
        self.bts_options_container.remove_element(self.options_bts[option_value])
        #
        del self.options_bts[option_value]
        self.options.remove(option_value)
        #
        if self.value == option_value:
            #
            if new_value is not None and new_value in self.options:
                self.value = new_value
            #
            else:
                #
                self.value = next(iter(self.options))
            #
            self.main_button.text = self.value
        #
        self.update_layout()

    #
    def update_options(self, new_options: set[str], new_value: Optional[str] = None) -> None:
        #
        if len(new_options) == 0:
            return
        #
        for bt in self.options_bts.values():
            self.bts_options_container.remove_element(bt)
        #
        self.options_bts = {}
        #
        self.options = new_options
        #
        option: str
        for option in self.options:
            self.options_bts[option] = ND_Button(
                window=self.window,
                elt_id=f"{self.elt_id}_bt_option_{option}",
                position=ND_Position_Container(w=self.w, h=self.h, container=self.bts_options_container),
                text=option,
                onclick=lambda x, option=option: self.on_option_button_clicked(option), # type: ignore
                font_name=self.font_name,
                font_size=self.font_size
            )
            self.bts_options_container.add_element(self.options_bts[option])

        #
        if self.value not in self.options:
            #
            if new_value is not None and new_value in self.options:
                self.value = new_value
            #
            else:
                #
                self.value = next(iter(self.options))
            #
            self.main_button.text = self.value
        #
        self.update_layout()

    #
    def set_state_base(self) -> None:
        #
        self.state = "base"
        self.bts_options_container.visible = False
        self.main_button.visible = True

    #
    def set_state_selection(self) -> None:
        #
        self.state = "selection"
        #
        self.bts_options_container.visible = True
        self.main_button.visible = False

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if self.state == "base":
            self.main_button.handle_event(event)
        else:
            self.bts_options_container.handle_event(event)
            #
            if isinstance(event, nd_event.ND_EventMouseButtonDown):
                if not self.bts_options_container.position.rect.contains_point(ND_Point(event.x, event.y)):
                    self.set_state_base()

    #
    def on_main_button_clicked(self, clickable: ND_Clickable) -> None:
        #
        self.set_state_selection()

    #
    def on_option_button_clicked(self, new_option: str) -> None:
        #
        self.value = new_option
        self.main_button.text = self.value
        #
        self.set_state_base()
        #
        if self.on_value_selected is not None:
            self.on_value_selected(self, self.value)


# ND_Container class implementation
class ND_Container(ND_Elt):
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position: ND_Position,
            overflow_hidden: bool = True,
            scroll_w: bool = False,
            scroll_h: bool = False,
            element_alignment: str = "row_wrap",
            element_alignment_kargs: dict[str, int | float | str | bool] = {},
            inverse_z_order: bool = False,
            min_space_width_containing_elements: int = 0,
            min_space_height_containing_elements: int = 0,
            scrollbar_w_height: int = 20,
            scrollbar_h_width: int = 20,
            scroll_speed_w: int = 4,
            scroll_speed_h: int = 4
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position)

        # If the elements overflows are hidden or not (only used in the render() function)
        self.overflow_hidden: bool = overflow_hidden

        # If the container is a scrollable container in theses directions
        self.scroll_w: bool = scroll_w
        self.scroll_h: bool = scroll_h

        #
        self.scroll_speed_w: int = scroll_speed_w
        self.scroll_speed_h: int = scroll_speed_h

        #
        self.scroll_x: float = 0
        self.scroll_y: float = 0
        self.last_scroll_x: float = 0
        self.last_scroll_y: float = 0

        # The current scroll value
        self.scroll: ND_Point = ND_Point(0, 0)

        # If the elements are aligned in a row, a column, a row with wrap, a column with wrap or a grid
        self.element_alignment: str = element_alignment
        self.element_alignment_kargs: dict[str, int | float | str | bool] = element_alignment_kargs
        self.inverse_z_order: bool = inverse_z_order

        # List of contained elements
        self.elements: list[ND_Elt] = []
        #
        self.elements_by_id: dict[str, ND_Elt] = {}

        # Elements that represents the scrollbar if there is one
        self.w_scrollbar: Optional[ND_H_ScrollBar] = None
        self.h_scrollbar: Optional[ND_V_ScrollBar] = None

        #
        self.scrollbar_w_height: int = scrollbar_w_height
        self.scrollbar_h_width: int = scrollbar_h_width

        # Representing the total contained content width and height
        self.content_width: int = 0
        self.content_height: int = 0

        # To help giving contained element space.
        self.min_space_width_containing_elements: int = min_space_width_containing_elements
        self.min_space_height_containing_elements: int = min_space_height_containing_elements

    #
    def get_element_recursively_from_subchild(self, elt_id: str) -> Optional[ND_Elt]:
        #
        if elt_id in self.elements_by_id:
            return self.elements_by_id[elt_id]
        #
        r: Optional[ND_Elt]
        #
        for elt in self.elements_by_id.values():
            #
            if isinstance(elt, ND_Container):
                #
                r = elt.get_element_recursively_from_subchild(elt_id=elt_id)
                #
                if r is not None:
                    #
                    return r
            #
            if isinstance(elt, ND_MultiLayer):
                #
                r = elt.get_element_recursively_from_subchild(elt_id=elt_id)
                #
                if r is not None:
                    #
                    return r
        #
        return None

    #
    def update_scroll_layout(self) -> None:
        #
        self.scroll_x = -self.w_scrollbar.scroll_position if self.w_scrollbar else 0
        self.scroll_y = -self.h_scrollbar.scroll_position if self.h_scrollbar else 0
        #
        self.update_layout()
        #
        return
        # #
        # scroll_dx: int = int(self.last_scroll_x - self.scroll_x)
        # scroll_dy: int = int(self.last_scroll_y - self.scroll_y)
        # #
        # elt: ND_Elt
        # for elt in self.elements:
        #     #
        #     elt.position.x += scroll_dx
        #     elt.position.y += scroll_dy
        #     #
        #     if hasattr(elt, "update_scroll_layout"):
        #         elt.update_scroll_layout()
        # #
        # self.last_scroll_x = self.scroll_x
        # self.last_scroll_y = self.scroll_y

    #
    def add_element(self, element: ND_Elt) -> None:
        #
        if element.elt_id in self.elements_by_id:
            raise IndexError(f"Error: Trying to add an element with id {element.elt_id} in container {self.elt_id}, but there was already an element with the same id in there!")
        #
        self.elements.append(element)
        self.elements_by_id[element.elt_id] = element
        #
        self.update_layout()
        #
        if hasattr(element, "update_layout"):
            element.update_layout()

    #
    def remove_element(self, element: ND_Elt) -> None:
        #
        if element.elt_id not in self.elements_by_id:
            raise IndexError(f"Error: Trying to remove an element with id {element.elt_id} in container {self.elt_id}, but there aren't such elements in there !")
        #
        self.elements.remove(element)
        del self.elements_by_id[element.elt_id]
        #
        self.update_layout()

    #
    def remove_element_from_elt_id(self, elt_id: str) -> None:
        #
        if elt_id not in self.elements_by_id:
            raise IndexError(f"Error: Trying to remove an element with id {elt_id} in container {self.elt_id}, but there aren't such elements in there !")
        #
        element: ND_Elt = self.elements_by_id[elt_id]
        #
        self.elements.remove(element)
        del self.elements_by_id[element.elt_id]
        #
        self.update_layout()

    #
    def update_layout(self) -> None:
        #
        if self.element_alignment == "row_wrap":
            self._layout_row_wrap()
        elif self.element_alignment == "col_wrap":
            self._layout_column_wrap()
        elif self.element_alignment == "grid":
            self._layout_grid()
        elif self.element_alignment == "col":
            self._layout_column()
        else:  #  self.element_alignment == "row"
            self._layout_row()

        #
        for elt in self.elements:
            if hasattr(elt, "update_layout"):
                elt.update_layout()

        #
        if self.scroll_w:
            #
            if self.content_width > self.w:
                #
                if not self.w_scrollbar:
                    self.w_scrollbar = ND_H_ScrollBar(
                                                        window=self.window,
                                                        elt_id=f"{self.elt_id}_wscroll",
                                                        position=ND_Position(self.x, self.y + self.h - self.scrollbar_w_height, self.w, self.scrollbar_w_height),
                                                        content_width=self.content_width,
                                                        on_value_changed=lambda elt, value: self.update_scroll_layout()
                    )
                #
                else:
                    self.w_scrollbar.content_width = self.content_width
                    self.w_scrollbar.position.set_x(self.x)
                    self.w_scrollbar.position.set_y(self.y + self.h - self.scrollbar_w_height)
                    self.w_scrollbar.position.set_w(self.w)
                    self.w_scrollbar.position.set_h(self.scrollbar_w_height)
            #
            elif self.w_scrollbar:
                #
                del(self.w_scrollbar)
                self.w_scrollbar = None

        #
        if self.scroll_h:
            #
            if self.content_height > self.h:
                #
                if not self.h_scrollbar:
                    self.h_scrollbar = ND_V_ScrollBar(
                                                        window=self.window,
                                                        elt_id=f"{self.elt_id}_hscroll",
                                                        position=ND_Position(self.x + self.w - self.scrollbar_h_width, self.y, self.scrollbar_h_width, self.h),
                                                        content_height=self.content_height,
                                                        on_value_changed=lambda elt, value: self.update_scroll_layout()
                    )
                #
                else:
                    self.h_scrollbar.content_height = self.content_height
                    self.h_scrollbar.position.set_x(self.x + self.w - self.scrollbar_h_width)
                    self.h_scrollbar.position.set_y(self.y)
                    self.h_scrollbar.position.set_w(self.scrollbar_h_width)
                    self.h_scrollbar.position.set_h(self.h)
            #
            elif self.h_scrollbar:
                #
                del(self.h_scrollbar)
                self.h_scrollbar = None

    #
    def _layout_row_wrap(self) -> None:
        # Initialize row tracking variables
        rows_height: list[int] = [0]
        rows_width: list[int] = [0]
        rows_left_width_total_weight: list[float] = [0]
        rows: list[list[ND_Elt]] = [ [] ]

        #
        crt_x: int = 0
        max_x: int = self.w

        # First pass
        for elt in self.elements:
            #
            elt_w: int = max(elt.w, self.min_space_width_containing_elements) + elt.get_margin_left() + elt.get_margin_right()
            elt_h: int = max(elt.h, self.min_space_height_containing_elements) + elt.get_margin_top() + elt.get_margin_bottom()
            elt_stretch_ratio: float = elt.get_width_stretch_ratio()

            # Si ca dépasse, on crée une nouvelle ligne
            if rows_width[-1] + elt_w >= max_x:
                #
                rows_height.append(elt_h)
                rows_width.append(elt_w)
                rows_left_width_total_weight.append(elt_stretch_ratio)
                rows.append([elt])
                #
                continue

            # Sinon, on ajoute à la ligne actuelle
            #
            rows_height[-1] = max( rows_height[-1], elt_h )
            rows_width[-1] = rows_width[-1] + elt_w
            rows_left_width_total_weight[-1] += elt_stretch_ratio
            rows[-1].append( elt )

        #
        self.content_height = sum(rows_height)
        self.content_width = max(rows_width)
        #
        self.last_scroll_y = self.scroll_y
        self.last_scroll_x = self.scroll_x
        crt_y: int = self.y + int(self.scroll_y)
        space_left: int = 0

        # Second pass
        for i_row in range(len(rows)):
            #
            crt_x = self.x + int(self.scroll_x)
            space_left = self.w - rows_width[i_row]
            #
            for elt in rows[i_row]:
                #
                margin_left: int = 0
                margin_right: int = 0
                margin_top: int = 0
                elt_space_left: int = 0
                #
                if isinstance(elt.position, ND_Position_Container):
                    #
                    elt_stretch_ratio = elt.position.get_width_stretch_ratio()
                    #
                    if elt_stretch_ratio > 0:
                        # We can assume that if elt_stretch_ratio is > 0, the rows_left_width_total_weight[i_row] is > 0
                        elt_space_left = int( float(space_left) * (elt_stretch_ratio / rows_left_width_total_weight[i_row] ) )
                    #
                    margin_left = elt.get_margin_left(elt_space_left)
                    margin_right = elt.get_margin_right(elt_space_left)
                    margin_top = elt.get_margin_top(rows_height[i_row] - elt.h)
                #
                elt.position.set_x(crt_x + margin_left)
                crt_x += elt.w + margin_left + margin_right
                elt.position.set_y(crt_y + margin_top)
            #
            crt_y += rows_height[i_row]

    #
    def _layout_row(self) -> None:

        # Initialize row tracking variables
        row_width: int = 0
        row_left_width_total_weight: float = 0

        #
        crt_x: int = 0

        # First pass
        for elt in self.elements:
            #
            elt_w: int = max(elt.w, self.min_space_width_containing_elements) + elt.get_margin_left() + elt.get_margin_right()
            elt_stretch_ratio: float = elt.get_width_stretch_ratio()

            # On ajoute à la ligne actuelle
            row_width = row_width + elt_w
            row_left_width_total_weight += elt_stretch_ratio

        ##
        self.content_width = row_width
        #
        if isinstance(self.position, ND_Position_Container) and self.position.is_w_auto():
            #
            self.position.set_w(new_w=self.content_width)
            # self.position._w = self.content_width
        #
        self.last_scroll_y = self.scroll_y
        crt_y: int = self.y + int(self.scroll_y)
        space_left: int = 0

        # Second pass
        #
        self.content_height = 0
        #
        self.last_scroll_x = self.scroll_x
        crt_x = self.x + int(self.scroll_x)
        space_left = self.w - row_width
        #
        for elt in self.elements:
            #
            margin_left: int = 0
            margin_right: int = 0
            margin_top: int = 0
            margin_bottom: int = 0
            elt_space_left: int = 0
            #
            if isinstance(elt.position, ND_Position_Container):
                #
                elt_stretch_ratio = elt.position.get_width_stretch_ratio()
                #
                if elt_stretch_ratio > 0:
                    # We can assume that if elt_stretch_ratio is > 0, the rows_left_width_total_weight[i_row] is > 0
                    elt_space_left = int( float(space_left) * (elt_stretch_ratio / row_left_width_total_weight ) )
                #
                margin_left = elt.get_margin_left(elt_space_left)
                margin_right = elt.get_margin_right(elt_space_left)
                margin_top = elt.get_margin_top(self.h - elt.h)
                margin_bottom = elt.get_margin_bottom(self.h - elt.h)
            #
            elt.position.set_x(crt_x + margin_left)
            crt_x += elt.w + margin_left + margin_right
            elt.position.set_y(crt_y + margin_top)
            #
            if margin_top + elt.h + margin_bottom > self.content_height:
                self.content_height = margin_top + elt.h + margin_bottom

    #
    def _layout_column_wrap(self) -> None:

        # Initialize col tracking variables
        cols_height: list[int] = [0]
        cols_width: list[int] = [0]
        cols_left_height_total_weight: list[float] = [0]
        cols: list[list[ND_Elt]] = [ [] ]

        #
        crt_y: int = 0
        max_y: int = self.h

        # First pass
        for elt in self.elements:
            #
            elt_w: int = max(elt.w, self.min_space_width_containing_elements) + elt.get_margin_left() + elt.get_margin_right()
            elt_h: int = max(elt.h, self.min_space_height_containing_elements) + elt.get_margin_top() + elt.get_margin_bottom()
            elt_stretch_ratio: float = elt.get_height_stretch_ratio()

            # Si ca dépasse, on crée une nouvelle ligne
            if cols_height[-1] + elt_h > max_y:
                #
                cols_height.append(elt_h)
                cols_width.append(elt_w)
                cols_left_height_total_weight.append(elt_stretch_ratio)
                cols.append([elt])
                #
                continue

            # Sinon, on ajoute à la ligne actuelle
            #
            cols_width[-1] = max( cols_width[-1], elt_w )
            cols_height[-1] = cols_height[-1] + elt_h
            cols_left_height_total_weight[-1] += elt_stretch_ratio
            cols[-1].append( elt )

        #
        self.content_height = max(cols_height)
        self.content_width = sum(cols_width)
        #
        self.last_scroll_x = self.scroll_x
        self.last_scroll_y = self.scroll_y
        crt_x: int = self.x + int(self.scroll_x)
        space_left: int = 0

        # Second pass
        for i_col in range(len(cols)):
            #
            crt_y = self.y + int(self.scroll_y)
            space_left = self.h - cols_height[i_col]
            #
            for elt in cols[i_col]:
                #
                margin_top: int = 0
                margin_bottom: int = 0
                margin_left: int = 0
                elt_space_left: int = 0
                #
                if isinstance(elt.position, ND_Position_Container):
                    #
                    elt_stretch_ratio = elt.position.get_width_stretch_ratio()
                    #
                    if elt_stretch_ratio > 0:
                        # We can assume that if elt_stretch_ratio is > 0, the cols_left_height_total_weight[i_col] is > 0
                        elt_space_left = int( float(space_left) * (elt_stretch_ratio / cols_left_height_total_weight[i_col] ) )
                    #
                    margin_top = elt.get_margin_top(elt_space_left)
                    margin_bottom = elt.get_margin_bottom(elt_space_left)
                    margin_left = elt.get_margin_top(cols_width[i_col] - elt.w)
                #
                elt.position.set_x(crt_x + margin_left)
                elt.position.set_y(crt_y + margin_top)
                crt_y += elt.h + margin_top + margin_bottom
            #
            crt_x += cols_width[i_col]

    #
    def _layout_column(self) -> None:

        # Initialize col tracking variables
        col_height: int = 0
        col_left_height_total_weight: float = 0

        #
        crt_y: int = 0

        # First pass
        for elt in self.elements:
            #
            elt_h: int = max(elt.h, self.min_space_height_containing_elements) + elt.get_margin_top() + elt.get_margin_bottom()
            elt_stretch_ratio: float = elt.get_height_stretch_ratio()

            # Sinon, on ajoute à la ligne actuelle
            #
            col_height = col_height + elt_h
            col_left_height_total_weight += elt_stretch_ratio

        #
        self.last_scroll_x = self.scroll_x
        crt_x: int = self.x + int(self.scroll_x)
        space_left: int = 0


        ##
        self.content_height = col_height
        #
        if isinstance(self.position, ND_Position_Container) and self.position.is_h_auto():
            #
            self.position.set_h(new_h=col_height)
            # self.position._h = col_height

        # Second pass
        #
        self.content_width = 0
        #
        self.last_scroll_y = self.scroll_y
        crt_y = self.y + int(self.scroll_y)
        space_left = self.h - col_height
        #
        for elt in self.elements:
            #
            margin_top: int = 0
            margin_bottom: int = 0
            margin_left: int = 0
            margin_right: int = 0
            elt_space_left: int = 0
            #
            if isinstance(elt.position, ND_Position_Container):
                #
                elt_stretch_ratio = elt.position.get_width_stretch_ratio()
                #
                if elt_stretch_ratio > 0 and col_left_height_total_weight > 0:
                    # We can assume that if elt_stretch_ratio is > 0, the col_left_height_total_weight is > 0
                    elt_space_left = int( float(space_left) * (elt_stretch_ratio / col_left_height_total_weight ) )
                #
                margin_top = elt.get_margin_top(elt_space_left)
                margin_bottom = elt.get_margin_bottom(elt_space_left)
                margin_left = elt.get_margin_left(self.w - elt.w)
                margin_right = elt.get_margin_right(self.w - elt.w)
            #
            elt.position.set_x(crt_x + margin_left)
            elt.position.set_y(crt_y + margin_top)
            crt_y += elt.h + margin_top + margin_bottom
            #
            if margin_left + elt.w + margin_right > self.content_width:
                self.content_width = margin_left + elt.w + margin_right
        #
        self.content_height = crt_y

    #
    def _layout_grid(self):
        #
        cols: int = int( self.element_alignment_kargs.get("cols", 3) )
        row_spacing: int = int( self.element_alignment_kargs.get("row_spacing", 5) )
        col_spacing: int = int( self.element_alignment_kargs.get("col_spacing", 5) )
        #
        max_width: int = (self.w - (cols - 1) * col_spacing) // cols
        #
        x: int = 0
        y: int = 0
        #
        row_height: int = 0

        #
        self.last_scroll_x = self.scroll_x
        self.last_scroll_y = self.scroll_y

        #
        for i, element in enumerate(self.elements):
            #
            # element.position._w = min(element.w, max_width)
            element.position.set_w(new_w=min(element.w, max_width))
            #
            if i % cols == 0 and i != 0:
                x = 0
                y += row_height + row_spacing
                row_height = 0
            #
            element.position.set_x(new_x=self.x + int(self.scroll_x) + x)
            element.position.set_y(new_y=self.y + int(self.scroll_y) + y)
            # element._x = self.x + int(self.scroll_x) + x
            # element._y = self.y + int(self.scroll_y) + y
            #
            x += element.w + col_spacing
            # x += element.tx + col_spacing
            #
            row_height = max(row_height, element.h)
            # row_height = max(row_height, element.ty)

        self.content_width = self.w
        self.content_height = y + row_height

    #
    def render(self) -> None:
        #
        if not self.visible:
            return

        #
        if self.overflow_hidden:
            self.window.enable_area_drawing_constraints(self.x, self.y, self.w, self.h)

        # Render each element with the scrollbar offsets applied
        elt: ND_Elt
        rendering_order = range(len(self.elements))
        #
        if self.inverse_z_order:
            rendering_order = rendering_order[::-1]
        #
        for i in rendering_order:
            #
            elt = self.elements[i]

            #
            elt.render()


        # Remove clipping
        if self.overflow_hidden:
            self.window.disable_area_drawing_constraints()

        # Render scrollbars
        if self.w_scrollbar:
            self.w_scrollbar.render()
        if self.h_scrollbar:
            self.h_scrollbar.render()

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if self.w_scrollbar:
            self.w_scrollbar.handle_event(event)
        if self.h_scrollbar:
            self.h_scrollbar.handle_event(event)

        # Mouse scroll events
        if isinstance(event, nd_event.ND_EventMouseWheelScrolled):
            #
            update_scroll: bool = False
            #
            if self.h_scrollbar is not None:
                #
                self.h_scrollbar.scroll_position = clamp(self.h_scrollbar.scroll_position + event.scroll_y * self.scroll_speed_h, 0, self.h_scrollbar.content_height)
                #
                update_scroll = True
            #
            if self.w_scrollbar is not None:
                #
                self.w_scrollbar.scroll_position = clamp(self.w_scrollbar.scroll_position + event.scroll_x * self.scroll_speed_w, 0, self.w_scrollbar.content_width)
                #
                update_scroll = True
            #
            if update_scroll:
                self.update_scroll_layout()


        # Propagate events to child elements
        elt_order = range(len(self.elements))
        #
        if not self.inverse_z_order:
            elt_order = elt_order[::-1]
        #
        for i in elt_order:
            #
            element = self.elements[i]
            if hasattr(element, 'handle_event'):
                element.handle_event(event)


# ND_MultiLayer class implementation
class ND_MultiLayer(ND_Elt):
    #
    def __init__(
                    self,
                    window: ND_Window,
                    elt_id: str,
                    position: ND_Position,
                    elements_layers: dict[int, ND_Elt] = {}
    ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position)


        # list of elements sorted by render importance with layers (ascending order)
        self.elements_layers: dict[int, ND_Elt] = elements_layers
        self.elements_by_id: dict[str, ND_Elt] = {}

        #
        layer: int
        elt: ND_Elt
        #
        for layer in self.elements_layers:
            #
            elt = self.elements_layers[layer]
            element_id = elt.elt_id
            #
            if element_id in self.elements_by_id:
                raise UserWarning(f"Error: at least two elements have the same id: {element_id}!")
            #
            self.elements_by_id[element_id] = elt
            #
            self.update_layout_of_element(elt)
        #
        self.layers_keys: list[int] = sorted(list(self.elements_layers.keys()))

    #
    def get_element_recursively_from_subchild(self, elt_id: str) -> Optional[ND_Elt]:
        #
        if elt_id in self.elements_by_id:
            return self.elements_by_id[elt_id]
        #
        r: Optional[ND_Elt] = None
        #
        for elt in self.elements_by_id.values():
            #
            if isinstance(elt, ND_Container):
                #
                r = elt.get_element_recursively_from_subchild(elt_id=elt_id)
                #
                if r is not None:
                    #
                    return r
            #
            if isinstance(elt, ND_MultiLayer):
                #
                r = self.get_element_recursively_from_subchild(elt_id=elt_id)
                #
                if r is not None:
                    #
                    return r
        #
        return None

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        for elt in self.elements_by_id.values():

            #
            if hasattr(elt, "handle_event"):
                elt.handle_event(event)

        # TODO: gérer les évenenements en fonctions de si un layer du dessus bloque les évenements en dessous

        # #
        # layer: int
        # for layer in self.layers_keys[::-1]:

        #     elt_list: list[str] = self.collisions_layers[layer].get_colliding_ids( (event.button.x, event.button.y) )

        #     for elt_id in elt_list:
        #         self.elements_by_id[elt_id].handle_event(event)

        #     if len(elt_list) > 0:
        #         return

    #
    def update_layout_of_element(self, elt: ND_Elt) -> None:
        #
        ew: int = elt.w
        eh: int = elt.h
        emt: int = elt.get_margin_top(self.h - eh)
        eml: int = elt.get_margin_left(self.w - ew)
        #
        enx: int = self.x + eml
        eny: int = self.y + emt
        #
        elt.position.set_x(enx)
        elt.position.set_y(eny)
        #
        if hasattr(elt, "update_layout"):
            elt.update_layout()

    #
    def update_layout(self) -> None:
        #
        for elt in self.elements_by_id.values():
            #
            self.update_layout_of_element(elt)

    #
    def insert_to_layers_keys(self, layer_key: int) -> None:

        if ( len(self.layers_keys) == 0 ) or ( layer_key > self.layers_keys[-1] ):
            self.layers_keys.append(layer_key)
            return

        # Insertion inside a sorted list by ascendant
        i: int
        k: int
        for i, k in enumerate(self.layers_keys):
            if k > layer_key:
                self.layers_keys.insert(i, layer_key)
                return

    #
    def add_element(self, layer_id: int, elt: ND_Elt) -> None:
        #
        elt_id: str = elt.elt_id

        #
        if elt_id in self.elements_by_id:
            raise UserWarning(f"Error: at least two elements in the multi-layer {self.elt_id} have the same id: {elt_id}!")

        #
        if layer_id not in self.elements_layers:
            self.elements_layers[layer_id] = elt
            self.elements_by_id[elt.elt_id] = elt
            self.insert_to_layers_keys(layer_id)
            #
            self.update_layout_of_element(elt)
        #
        else:
            raise UserWarning(f"Error: trying to insert an element to multi-layer {self.elt_id} on the same layer than another element!")

    #
    def render(self) -> None:
        #
        layer_key: int
        for layer_key in self.layers_keys:
            #
            element: ND_Elt = self.elements_layers[layer_key]
            #
            element.render()


#
class ND_CameraScene(ND_Elt):
    #
    def __init__(self, window: ND_Window, elt_id: str, position: ND_Position, scene_to_render: ND_Scene, zoom: float = 1.0) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.scene_to_render: ND_Scene = scene_to_render
        self.zoom: float = zoom

    #
    def render(self) -> None:
        # TODO
        pass


#
class ND_CameraGrid(ND_Elt):
    #
    def __init__(self, window: ND_Window, elt_id: str, position: ND_Position, grids_to_render: list["ND_RectGrid"], zoom_x: float = 1.0, zoom_y: float = 1.0) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.grids_to_render: list[ND_RectGrid] = grids_to_render
        #
        self.origin: ND_Point = ND_Point(0, 0)
        self.zoom_x: float = zoom_x
        self.zoom_y: float = zoom_y
        #
        self.min_zoom: float = 0.1
        self.max_zoom: float = 100
        #
        self.grid_lines_width: int = 0
        self.grid_lines_color: ND_Color = ND_Color(255, 255, 255)
        grid_to_render: ND_RectGrid
        for grid_to_render in self.grids_to_render:
            if grid_to_render.grid_lines_width > self.grid_lines_width:
                self.grid_lines_width = grid_to_render.grid_lines_width
                self.grid_lines_color = grid_to_render.grid_lines_color

    #
    def render(self) -> None:
        #
        if len(self.grids_to_render) == 0:  # If no grids to render
            return
        #
        zx: float = clamp(self.zoom_x, self.min_zoom, self.max_zoom)
        zy: float = clamp(self.zoom_y, self.min_zoom, self.max_zoom)
        #
        self.window.enable_area_drawing_constraints(self.x, self.y, self.w, self.h)
        #
        gtx: int = int(zx * self.grids_to_render[0].grid_tx)
        gty: int = int(zy * self.grids_to_render[0].grid_ty)
        #
        lines_width: int = 0
        if self.grid_lines_width > 0:
            lines_width = max( 1, round( max(zx, zy) * self.grid_lines_width ) )
        #
        deb_x: int = self.origin.x # math.ceil( self.origin.x / (gtx + lines_width) )
        deb_y: int = self.origin.y # math.ceil( self.origin.y / (gty + lines_width) )
        fin_x: int = self.origin.x + math.ceil( (self.w) / (gtx) ) + 1
        fin_y: int = self.origin.y + math.ceil( (self.h) / (gty) ) + 1

        # Dessin des lignes
        cx: int
        cy: int
        dcx: int
        dcy: int
        for cx in range(deb_x, fin_x + 1):
            #
            dcx = self.x + int((cx-deb_x) * gtx)

            # Dessin ligne
            self.window.draw_thick_line(
                                            x1=dcx, x2=dcx, y1=self.y, y2=self.y+self.h,
                                            color=self.grid_lines_color,
                                            line_thickness=lines_width
            )

        #
        for cy in range(deb_y, fin_y + 1):
            #
            dcy = self.y + int((cy-deb_y) * gty)

            # Dessin Ligne
            self.window.draw_thick_line(
                                            x1=self.x, x2=self.x+self.w, y1=dcy, y2=dcy,
                                            color=self.grid_lines_color,
                                            line_thickness=lines_width
            )

        #
        grid_to_render: ND_RectGrid
        for grid_to_render in self.grids_to_render:

            # Dessin des éléments
            for cx in range(deb_x, fin_x + 1):
                #
                dcx = self.x + int((cx-deb_x) * gtx)
                #
                for cy in range(deb_y, fin_y + 1):
                    #
                    dcy = self.y + int((cy-deb_y) * gty)
                    #
                    elt: Optional[ND_Elt] = grid_to_render.get_element_at_grid_case(ND_Point(cx, cy))
                    #
                    if elt is None:
                        continue
                    #
                    old_position: ND_Position = elt.position
                    #
                    old_transformations: ND_Transformation = elt.transformations
                    #
                    if ND_Point(cx, cy) in grid_to_render.grid_transformations:
                        elt.transformations = elt.transformations + grid_to_render.grid_transformations[ND_Point(cx, cy)]
                    #
                    elt.position = ND_Position(dcx, dcy, int(gtx), int(gty))
                    #
                    elt.render()
                    #
                    elt.position = old_position
                    #
                    elt.transformations = old_transformations
                    #

        #
        self.window.disable_area_drawing_constraints()
        #

    #
    def move_camera_to_grid_area(self, grid_area: ND_Rect, force_square_tiles: bool = True) -> None:
        #
        if not self.grids_to_render:
            return
        #
        self.origin.x = grid_area.x - 1
        self.origin.y = grid_area.y - 1
        #
        self.zoom_x = float(self.w) / float((grid_area.w+3) * (self.grids_to_render[0].grid_tx+self.grid_lines_width))
        self.zoom_y = float(self.h) / float((grid_area.h+3) * (self.grids_to_render[0].grid_ty+self.grid_lines_width))
        #
        if force_square_tiles:
            mz: float = min(self.zoom_x, self.zoom_y)
            self.zoom_x = mz
            self.zoom_y = mz


#
class ND_RectGrid(ND_Elt):
    #
    def __init__(self, window: ND_Window, elt_id: str, position: ND_Position, grid_tx: int, grid_ty: int, grid_lines_width: int = 0, grid_lines_color: ND_Color = ND_Color(0, 0, 0)) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.default_element_grid_id: int = -1  # elt_grid_id < 0 => is None, Nothing is displayed
        #
        self.grid_tx: int = grid_tx
        self.grid_ty: int = grid_ty
        #
        self.grid_lines_width: int = grid_lines_width
        self.grid_lines_color: ND_Color = grid_lines_color
        #
        self.grid_elements_by_id: dict[int, ND_Elt] = {}
        self.grid_positions_by_id: dict[int, set[ND_Point]] = {}
        self.elements_to_grid_id: dict[ND_Elt, int] = {}  # hash = object's pointer / (general/memory) id
        #
        self.next_available_id: int = 0
        #
        self.grid: dict[ND_Point, int] = {}  # dict key = (ND_Point=hash(f"{x}_{y}")) -> elt_grid_id
        self.grid_transformations: dict[ND_Point, ND_Transformation] = {}

    # Supprime tout, grille, éléments, ...
    def clean(self) -> None:
        #
        self.default_elt_grid_id = -1
        #
        self.grid_elements_by_id = {}
        self.grid_positions_by_id = {}
        self.elements_to_grid_id = {}
        #
        self.next_available_id = 0
        #
        self.grid = {}

    #
    def _set_grid_position(self, position: ND_Point, elt_grid_id: int = -1) -> None:
        #
        if elt_grid_id >= 0:
            self.grid[position] = elt_grid_id
            self.grid_positions_by_id[elt_grid_id].add(position)  # On ajoute la position de l'élement
        #
        elif position in self.grid:
            #
            old_elt_grid_id: int = self.grid[position]
            if old_elt_grid_id in self.grid_positions_by_id:  # On supprime la position de l'ancien element
                #
                if position in self.grid_positions_by_id[old_elt_grid_id]:
                    self.grid_positions_by_id[old_elt_grid_id].remove(position)
            #
            del self.grid[position]

    #
    def add_element_to_grid(self, element: ND_Elt, position: ND_Point | list[ND_Point]) -> int:
        #
        if element not in self.elements_to_grid_id:
            self.elements_to_grid_id[element] = self.next_available_id
            self.grid_elements_by_id[self.next_available_id] = element
            self.grid_positions_by_id[self.next_available_id] = set()
            self.next_available_id += 1
        #
        elt_grid_id = self.elements_to_grid_id[element]
        #
        self.add_element_position(elt_grid_id, position)
        #
        return elt_grid_id

    #
    def add_element_position(self, elt_id: int, position: ND_Point | list[ND_Point]) -> None:
        #
        if isinstance(position, list):  # liste de points
            #
            for pos in position:
                self._set_grid_position(pos, elt_id)
        #
        else:  # Point unique
            self._set_grid_position(position, elt_id)

    #
    def set_transformations_to_position(self, position: ND_Point, transformations: Optional[ND_Transformation]) -> None:
        #
        if transformations is None:
            if position in self.grid_transformations:
                del self.grid_transformations[position]
            return
        #
        self.grid_transformations[position] = transformations

    #
    def remove_element_of_grid(self, element: ND_Elt) -> None:
        #
        if element not in self.elements_to_grid_id:
            return
        #
        elt_id: int = self.elements_to_grid_id[element]

        # On va supprimer toutes les cases de la grille où l'élément était
        position: ND_Point
        for position in self.grid_positions_by_id[elt_id]:
            #
            self._set_grid_position(position, -1)

        # Si l'élément était l'élément par défaut
        if self.default_elt_grid_id == elt_id:
            #
            self.default_elt_grid_id = -1

        #
        del self.grid_positions_by_id[elt_id]
        del self.grid_elements_by_id[elt_id]
        del self.elements_to_grid_id[element]

    #
    def remove_at_position(self, pos: ND_Point) -> None:
        #
        if pos not in self.grid:
            return
        #
        elt_id: int = self.grid[pos]

        #
        if elt_id < 0:
            return

        # On supprimer la position de l'élément
        self.grid_positions_by_id[elt_id].remove(pos)
        self._set_grid_position(pos, -1)

    #
    def get_element_at_grid_case(self, case: ND_Point) -> Optional[ND_Elt]:
        #
        if case not in self.grid:
            return None
        #
        grid_elt_id: int = self.grid[case]
        #
        if grid_elt_id not in self.grid_elements_by_id:
            return None
        #
        return self.grid_elements_by_id[grid_elt_id]

    #
    def get_element_id_at_grid_case(self, case: ND_Point) -> Optional[int]:
        #
        if case not in self.grid:
            return None
        #
        return self.grid[case]

    #
    def get_empty_case_in_range(self, x_min: int, x_max: int, y_min: int, y_max: int) -> Optional[ND_Point]:
        #
        if x_min > x_max or y_min > y_max:
            #
            return None
        #
        dx: int = x_max - x_min
        dy: int = y_max - y_min
        r: int = int(math.sqrt(dx**2 + dy**2))

        # randoms
        xx: int
        yy: int
        p: ND_Point
        for _ in range(0, r):
            #
            xx = random.randint(x_min, x_max)
            yy = random.randint(y_min, y_max)
            p = ND_Point(xx, yy)
            #
            if p not in self.grid:
                return p

        # Brute si le random n'a rien trouvé
        for xx in range(x_min, x_max+1):
            for yy in range(y_min, y_max+1):
                #
                p = ND_Point(xx, yy)
                #
                if p not in self.grid:
                    return p

        #
        return None

    #
    def render(self) -> None:
        # Do nothing here, because it is a camera that have to render
        return

    #
    def export_chunk_of_grid_to_numpy(self, x_0: int, y_0: int, x_1: int, y_1: int, fn_elt_to_value: Callable[[Optional[ND_Elt], Optional[int]], int | float], np_type: type = np.float32) -> np.ndarray[Any, Any]:
        #
        dtx: int = x_1 - x_0
        dty: int = y_1 - y_0
        #
        grid: np.ndarray[Any, Any] = np.zeros((dtx, dty), dtype=np_type)
        #
        for dx in range(dtx):
            for dy in range(dty):
                #
                case_point: ND_Point = ND_Point(x_0 + dx, y_0 + dy)
                #
                elt: Optional[ND_Elt] = self.get_element_at_grid_case(case_point)
                elt_id: Optional[int] = self.get_element_id_at_grid_case(case_point)
                #
                grid[dx, dy] = fn_elt_to_value(elt, elt_id)
        #
        return grid


#
class ND_Position_RectGrid(ND_Position):
    #
    def __init__(self, rect_grid: ND_RectGrid) -> None:
        #
        super().__init__()
        #
        self.rect_grid: ND_RectGrid = rect_grid
        #

    #
    @property
    def w(self) -> int:
        return self.rect_grid.grid_tx

    #
    @w.setter
    def w(self, new_w: int) -> None:
        # TODO
        pass

    #
    @property
    def h(self) -> int:
        return self.rect_grid.grid_ty

    #
    @h.setter
    def h(self, new_h: int) -> None:
        # TODO
        pass

    #
    def current_grid_case(self, case: ND_Point) -> None:
        self._x = case.x
        self._y = case.y


#
class ND_Position_FullWindow(ND_Position):
    #
    def __init__(self, window: ND_Window) -> None:
        #
        super().__init__()
        #
        self.window = window

    #
    @property
    def x(self) -> int:
        return 0

    #
    @x.setter
    def x(self, new_x: int) -> None:
        # TODO
        pass

    #
    @property
    def y(self) -> int:
        return 0

    #
    @y.setter
    def y(self, new_y: int) -> None:
        # TODO
        pass

    #
    @property
    def w(self) -> int:
        return self.window.width

    #
    @w.setter
    def w(self, new_w: int) -> None:
        # TODO
        pass

    #
    @property
    def h(self) -> int:
        return self.window.height

    #
    @h.setter
    def h(self, new_h: int) -> None:
        # TODO
        pass


#
class ND_Position_Container(ND_Position):
    #
    def __init__(
                    self,
                    w: int | str,
                    h: int | str,
                    container: ND_Container,
                    position_constraints: Optional[ND_Position_Constraints] = None,
                    position_margins: Optional[ND_Position_Margins] = None
    ) -> None:

        #
        self.w_str: Optional[str] = None
        self.h_str: Optional[str] = None

        #
        if isinstance(w, str):
            self.w_str = w
            w = -1

        #
        if isinstance(h, str):
            self.h_str = h
            h = -1

        #
        if self.w_str == "square" and self.h_str == "square":
            raise UserWarning("Error: width and height cannot have attribute 'square' !!!")

        #
        super().__init__(0, 0, w, h)

        #
        self.container: ND_Container = container
        #
        self.positions_constraints: Optional[ND_Position_Constraints] = position_constraints
        self.position_margins: Optional[ND_Position_Margins] = position_margins

    #
    def is_w_auto(self) -> bool:
        return self.w_str == "auto"

    #
    def is_h_auto(self) -> bool:
        return self.h_str == "auto"

    #
    @property
    def w(self) -> int:
        #
        if self.w_str is None:
            return self._w
        #
        elif self.w_str == "auto":
            return max(self._w, 0)
        #
        elif self.w_str == "square":
            return self.h
        #
        w: float = get_percentage_from_str(self.w_str) / 100.0
        #
        width: int = int(w * self.container.w)
        #
        if self.positions_constraints:
            #
            if self.positions_constraints.min_width and width < self.positions_constraints.min_width:
                width = self.positions_constraints.min_width
            #
            if self.positions_constraints.max_width and width > self.positions_constraints.max_width:
                width = self.positions_constraints.max_width
        #
        return width

    #
    @w.setter
    def w(self, new_w: int) -> None:
        # TODO
        pass

    #
    @property
    def h(self) -> int:
        #
        if self.h_str is None:
            return self._h
        #
        elif self.h_str == "auto":
            return max(self._h, 0)
        #
        elif self.h_str == "square":
            return self.w
        #
        h: float = get_percentage_from_str(self.h_str) / 100.0
        #
        height: int = int(h * self.container.h)
        #
        if self.positions_constraints:
            #
            if self.positions_constraints.min_height and height < self.positions_constraints.min_height:
                height = self.positions_constraints.min_height
            #
            if self.positions_constraints.max_height and height > self.positions_constraints.max_height:
                height = self.positions_constraints.max_height
        #
        return height

    #
    @h.setter
    def h(self, new_h: int) -> None:
        # TODO
        pass

    #
    @property
    def visible(self) -> bool:
        return self.container.visible

    #
    def get_margin_left(self, space_left: int = -1) -> int:
        #
        if self.position_margins is None:
            return 0

        #
        mleft: Optional[int | str] = self.position_margins.margin_left
        if mleft is None:
            mleft = self.position_margins.margin
        #
        if mleft is None:
            mleft = self.position_margins.min_margin_left

        #
        pleft: float = 0.0

        #
        if isinstance(mleft, int):
            if not isinstance(self.position_margins.margin_right, str):
                return mleft
            #
            pleft = (100.0 - get_percentage_from_str(self.position_margins.margin_right)) / 100.0
        else:
            pleft = get_percentage_from_str(mleft) / 100.0

        #
        return max(
                    self.position_margins.min_margin_left,
                    int( space_left * pleft )
        )

    #
    def get_margin_right(self, space_left: int = -1) -> int:
        #
        if self.position_margins is None:
            return 0

        #
        mval: Optional[int | str] = self.position_margins.margin_right
        if mval is None:
            mval = self.position_margins.margin
        #
        if mval is None:
            mval = self.position_margins.min_margin_right

        #
        pval: float = 0.0

        #
        if isinstance(mval, int):
            if not isinstance(self.position_margins.margin_left, str):
                return mval
            #
            pval = (100.0 - get_percentage_from_str(self.position_margins.margin_left)) / 100.0
        else:
            pval = get_percentage_from_str(mval) / 100.0

        #
        return max(
                    self.position_margins.min_margin_right,
                    int( space_left * pval )
        )

    #
    def get_margin_top(self, space_left: int = -1) -> int:
        #
        if self.position_margins is None:
            return 0

        #
        mval: Optional[int | str] = self.position_margins.margin_top
        if mval is None:
            mval = self.position_margins.margin
        #
        if mval is None:
            mval = self.position_margins.min_margin_top

        #
        pval: float = 0.0

        #
        if isinstance(mval, int):
            if not isinstance(self.position_margins.margin_bottom, str):
                return mval
            #
            pval = (100.0 - get_percentage_from_str(self.position_margins.margin_bottom)) / 100.0
        else:
            pval = get_percentage_from_str(mval) / 100.0

        #
        return max(
                    self.position_margins.min_margin_top,
                    int( space_left * pval )
        )

    #
    def get_margin_bottom(self, space_left: int = -1) -> int:
        #
        if self.position_margins is None:
            return 0

        #
        mval: Optional[int | str] = self.position_margins.margin_bottom
        if mval is None:
            mval = self.position_margins.margin
        #
        if mval is None:
            mval = self.position_margins.min_margin_bottom

        #
        pval: float = 0.0

        #
        if isinstance(mval, int):
            if not isinstance(self.position_margins.margin_top, str):
                return mval
            #
            pval = (100.0 - get_percentage_from_str(self.position_margins.margin_top)) / 100.0
        else:
            pval = get_percentage_from_str(mval) / 100.0

        #
        return max(
                    self.position_margins.min_margin_bottom,
                    int( space_left * pval )
        )

    #
    def get_width_stretch_ratio(self) -> float:
        #
        if self.position_margins is None:
            return 0.0
        #
        if isinstance(self.position_margins.margin_left, str) or isinstance(self.position_margins.margin_right, str):
            return self.position_margins.width_stretch_ratio
        #
        return 0.0

    #
    def get_height_stretch_ratio(self) -> float:
        #
        if self.position_margins is None:
            return 0.0
        #
        if isinstance(self.position_margins.margin_top, str) or isinstance(self.position_margins.margin_bottom, str):
            return self.position_margins.height_stretch_ratio
        #
        return 0.0


#
class ND_Position_MultiLayer(ND_Position):
    #
    def __init__(
                    self,
                    multilayer: ND_MultiLayer,
                    w: int | str = -1,
                    h: int | str = -1,
                    position_constraints: Optional[ND_Position_Constraints] = None,
                    position_margins: Optional[ND_Position_Margins] = None
    ) -> None:

        #
        self.w_str: Optional[str] = None
        self.h_str: Optional[str] = None

        #
        w_int: int = -1
        h_int: int = -1

        if isinstance(w, str):
            self.w_str = w
            w_int = -1
        #
        else:
            #
            w_int = int(w)

        #
        if isinstance(h, str):
            self.h_str = h
            h_int = -1
        #
        else:
            #
            h_int = int(h)

        #
        super().__init__(0, 0, w_int, h_int)

        #
        self.multilayer: ND_MultiLayer = multilayer
        #
        self.positions_constraints: Optional[ND_Position_Constraints] = position_constraints
        self.position_margins: Optional[ND_Position_Margins] = position_margins

    #
    @property
    def w(self) -> int:
        #
        if self.w_str is None:
            if self._w <= 0:
                return self.multilayer.w
            #
            return self._w
        #
        w: float = get_percentage_from_str(self.w_str) / 100.0
        #
        return int(w * self.multilayer.w)

    #
    @w.setter
    def w(self, new_value: int) -> None:  # type: ignore
        # TODO
        pass

    #
    @property
    def h(self) -> int:
        #
        if self.h_str is None:
            if self._h <= 0:
                return self.multilayer.h
            #
            return self._h
        #
        h: float = get_percentage_from_str(self.h_str) / 100.0
        #
        return int(h * self.multilayer.h)

    #
    @h.setter
    def h(self, new_value: int) -> None:  # type: ignore
        # TODO
        pass

    #
    @property
    def visible(self) -> bool:
        return self.multilayer.visible

    #
    def get_margin_left(self, space_left: int = -1) -> int:
        #
        if self.position_margins is None:
            return 0

        #
        mleft: Optional[int | str] = self.position_margins.margin_left
        if mleft is None:
            mleft = self.position_margins.margin
        #
        if mleft is None:
            mleft = self.position_margins.min_margin_left

        #
        pleft: float = 0.0

        #
        if isinstance(mleft, int):
            if not isinstance(self.position_margins.margin_right, str):
                return mleft
            #
            pleft = (100.0 - get_percentage_from_str(self.position_margins.margin_right)) / 100.0
        else:
            pleft = get_percentage_from_str(mleft) / 100.0

        #
        return max(
                    self.position_margins.min_margin_left,
                    int( space_left * pleft )
        )

    #
    def get_margin_right(self, space_left: int = -1) -> int:
        #
        if self.position_margins is None:
            return 0

        #
        mval: Optional[int | str] = self.position_margins.margin_right
        if mval is None:
            mval = self.position_margins.margin
        #
        if mval is None:
            mval = self.position_margins.min_margin_right

        #
        pval: float = 0.0

        #
        if isinstance(mval, int):
            if not isinstance(self.position_margins.margin_left, str):
                return mval
            #
            pval = (100.0 - get_percentage_from_str(self.position_margins.margin_left)) / 100.0
        else:
            pval = get_percentage_from_str(mval) / 100.0

        #
        return max(
                    self.position_margins.min_margin_right,
                    int( space_left * pval )
        )

    #
    def get_margin_top(self, space_left: int = -1) -> int:
        #
        if self.position_margins is None:
            return 0

        #
        mval: Optional[int | str] = self.position_margins.margin_top
        if mval is None:
            mval = self.position_margins.margin
        #
        if mval is None:
            mval = self.position_margins.min_margin_top

        #
        pval: float = 0.0

        #
        if isinstance(mval, int):
            if not isinstance(self.position_margins.margin_bottom, str):
                return mval
            #
            pval = (100.0 - get_percentage_from_str(self.position_margins.margin_bottom)) / 100.0
        else:
            pval = get_percentage_from_str(mval) / 100.0

        #
        return max(
                    self.position_margins.min_margin_top,
                    int( space_left * pval )
        )

    #
    def get_margin_bottom(self, space_left: int = -1) -> int:
        #
        if self.position_margins is None:
            return 0

        #
        mval: Optional[int | str] = self.position_margins.margin_bottom
        if mval is None:
            mval = self.position_margins.margin
        #
        if mval is None:
            mval = self.position_margins.min_margin_bottom

        #
        pval: float = 0.0

        #
        if isinstance(mval, int):
            if not isinstance(self.position_margins.margin_top, str):
                return mval
            #
            pval = (100.0 - get_percentage_from_str(self.position_margins.margin_top)) / 100.0
        else:
            pval = get_percentage_from_str(mval) / 100.0

        #
        return max(
                    self.position_margins.min_margin_bottom,
                    int( space_left * pval )
        )

    #
    def get_width_stretch_ratio(self) -> float:
        #
        if self.position_margins is None:
            return 0.0
        #
        if isinstance(self.position_margins.margin_left, str) or isinstance(self.position_margins.margin_right, str):
            return self.position_margins.width_stretch_ratio
        #
        return 0.0

    #
    def get_height_stretch_ratio(self) -> float:
        #
        if self.position_margins is None:
            return 0.0
        #
        if isinstance(self.position_margins.margin_top, str) or isinstance(self.position_margins.margin_bottom, str):
            return self.position_margins.height_stretch_ratio
        #
        return 0.0


#
class ND_Elt_3D:

    #
    def __init__(self, origin: ND_Point_3D) -> None:
        #
        self.origin: ND_Point_3D = origin

    #
    def render(self) -> None:
        #
        pass


#
class ND_Space_3D(ND_Elt):

    #
    def __init__(self, window: ND_Window, elt_id: str, position: ND_Position, elts: Optional[list[ND_Elt_3D]] = None ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position)

        #
        self.elts: list[ND_Elt_3D] = elts if elts is not None else []

    #
    def render(self) -> None:
        # Will be rendered by a ND_Camera_3D
        pass


#
class ND_Camera_3D(ND_Elt):

    #
    def __init__(self, window: ND_Window, elt_id: str, position: ND_Position, space_3D: ND_Space_3D) -> None:
        #
        super().__init__(window=window, elt_id=elt_id, position=position)
        #
        self.space_3D: ND_Space_3D = space_3D

    #
    def render(self) -> None:
        # TODO
        return



###########################################################################


def prepare_backend(backend: str = "sdl2_sdlgfx"):

    #
    if backend == "sdl2_sdlgfx":
        #
        from lib_nadisplay_sdl2_sdlgfx import ND_Display_SDL2_SDLGFX as DisplayClass, ND_Window_SDL2_SDLGFX as WindowClass     # type: ignore
        from lib_nadisplay_sdl2 import ND_EventsManager_SDL as EventsManagerClass     # type: ignore

    #
    elif backend == "sdl2_opengl":
        #
        from lib_nadisplay_sdl2_opengl import ND_Display_SDL2_OPENGL as DisplayClass, ND_Window_SDL2_OPENGL as WindowClass     # type: ignore
        from lib_nadisplay_sdl2 import ND_EventsManager_SDL as EventsManagerClass     # type: ignore

    #
    elif backend == "glfw_opengl":
        #
        from lib_nadisplay_glfw_opengl import ND_Display_GLFW_OPENGL as DisplayClass, ND_Window_GLFW_OPENGL as WindowClass     # type: ignore
        from lib_nadisplay_glfw import ND_EventsManager_GLFW as EventsManagerClass     # type: ignore

    #
    elif backend == "glfw_vulkan":
        #
        from lib_nadisplay_glfw_vulkan import ND_Display_GLFW_VULKAN as DisplayClass, ND_Window_GLFW_VULKAN as WindowClass     # type: ignore
        from lib_nadisplay_glfw import ND_EventsManager_GLFW as EventsManagerClass     # type: ignore

    #
    elif backend == "pygame":
        #
        from lib_nadisplay_pygame import ND_Display_Pygame as DisplayClass, ND_Window_Pygame as WindowClass, ND_EventsManager_Pygame as EventsManagerClass     # type: ignore

    #
    else:
        #
        raise UserWarning(f"Unsupportend backend : `{backend}`.\n\nList of supported backends :\n\t- `sdl2_sdlgfx`\n\t- `sdl2_opengl`\n\t- `glfw_opengl`\n\t- `glfw_vulkan`\n\t- `pygame`\n")

    #
    return DisplayClass, WindowClass, EventsManagerClass


