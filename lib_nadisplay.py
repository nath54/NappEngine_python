# type: ignore

"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""

#
from lib_nadisplay_core import ND_MainApp, ND_Display, ND_Window, ND_Elt, ND_Scene, ND_EventsManager
#
from lib_nadisplay_prepare_backend import prepare_backend
#
from lib_nadisplay_colors import ND_Color, cl
#
from lib_nadisplay_point import ND_Point
from lib_nadisplay_rects import ND_Rect
#
from lib_nadisplay_transformation import ND_Transformation
#
from lib_nadisplay_position import ND_Position, ND_Position_Constraints, ND_Position_Margins
from lib_nadisplay_position_full_windows import ND_Position_FullWindow
#
from lib_nadisplay_elt_container import ND_Container, ND_Position_Container
from lib_nadisplay_elt_multilayer import ND_MultiLayer, ND_Position_MultiLayer
#
from lib_nadisplay_elt_text import ND_Elt_Text
from lib_nadisplay_elt_button import ND_Button
from lib_nadisplay_elt_rectangle import ND_Elt_Rectangle
from lib_nadisplay_elt_sprite import ND_Elt_Sprite
from lib_nadisplay_elt_animated_sprite import ND_Elt_AnimatedSprite
from lib_nadisplay_elt_sprite_of_atlas_texture import ND_Elt_Sprite_of_AtlasTexture, ND_AtlasTexture

