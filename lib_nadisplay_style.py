"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""

#
### Import Modules. ###
#
from typing import Optional, Any
#
from lib_nadisplay_colors import ND_Color, cl
#
from lib_nadisplay_transformation import ND_Transformation


#
### NaDisplay Style Class. ###
#
class ND_Style:

    #
    def __init__(
            self,

            #
            ### font related attributes for texts. ###
            #
            ## Font Name. ##
            #
            font_name: Optional[str] = None,
            font_name_hover: Optional[str] = None,
            font_name_clicked: Optional[str] = None,
            font_name_deactivated: Optional[str] = None,
            #
            ## Font Size. ##
            #
            font_size: int = 24,
            font_size_hover: Optional[int] = None,
            font_size_clicked: Optional[int] = None,
            font_size_deactivated: Optional[int] = None,
            #
            ## Font Color. ##
            #
            font_color: ND_Color = cl("black"),
            font_color_hover: Optional[ND_Color] = None,
            font_color_clicked: Optional[ND_Color] = None,
            font_color_deactivated: Optional[ND_Color] = None,

            #
            ### Border related attributes for rectangle / box / ... ###
            #
            ## Border Size, if border_size == 0 -> no border. ##
            #
            border_size: int = 1,
            border_size_hover: Optional[int] = None,
            border_size_clicked: Optional[int] = None,
            border_size_deactivated: Optional[int] = None,
            #
            ## Border Radius. ##
            #
            border_radius: int = 5,
            border_radius_hover: Optional[int] = None,
            border_radius_clicked: Optional[int] = None,
            border_deactivated: Optional[int] = None,
            #
            ## Border Color. ##
            #
            border_color: ND_Color = cl("white"),
            border_color_hover: Optional[ND_Color] = None,
            border_color_clicked: Optional[ND_Color] = None,
            border_color_deactivated: Optional[ND_Color] = None,

            #
            ### Background color for buttons / LineEdit / Checkbox / SelectOption / NumberInput / ... ###
            #
            bg_color: ND_Color = cl("light grey"),
            bg_color_hover: Optional[ND_Color] = None,
            bg_color_clicked: Optional[ND_Color] = None,
            bg_color_deactivated: Optional[ND_Color] = None,

            #
            ### Background texture for buttons / Checkbox / ... ###
            #
            bg_texture: Optional[int | str] = None,
            bg_texture_hover: Optional[int | str] = None,
            bg_texture_clicked: Optional[int | str] = None,
            bg_texture_deactivated: Optional[int | str] = None,

            #
            ### Texture Transformations for buttons / Checkbox / ... ###
            #
            transformation: ND_Transformation = ND_Transformation(),
            transformation_hover: Optional[ND_Transformation] = None,
            transformation_clicked: Optional[ND_Transformation] = None,
            transformation_deactivated: Optional[ND_Transformation] = None

    ) -> None:

        #
        ### font related attributes for texts. ###
        #
        ## Font Name. ##
        #
        self.font_name: Optional[str] = font_name
        self.font_name_hover: Optional[str] = font_name_hover
        self.font_name_clicked: Optional[str] = font_name_clicked
        self.font_name_deactivated: Optional[str] = font_name_deactivated
        #
        ## Font Size. ##
        #
        self.font_size: int = font_size
        self.font_size_hover: Optional[int] = font_size_hover
        self.font_size_clicked: Optional[int] = font_size_clicked
        self.font_size_deactivated: Optional[int] = font_size_deactivated
        #
        ## Font Color. ##
        #
        self.font_color: ND_Color = font_color
        self.font_color_hover: Optional[ND_Color] = font_color_hover
        self.font_color_clicked: Optional[ND_Color] = font_color_clicked
        self.font_color_deactivated: Optional[ND_Color] = font_color_deactivated

        #
        ### Border related attributes for rectangle / box / ... ###
        #
        ## Border Size, if border_size == 0 -> no border. ##
        #
        self.border_size: int = border_size
        self.border_size_hover: Optional[int] = border_size_hover
        self.border_size_clicked: Optional[int] = border_size_clicked
        self.border_size_deactivated: Optional[int] = border_size_deactivated
        #
        ## Border Radius. ##
        #
        self.border_radius: int = border_radius
        self.border_radius_hover: Optional[int] = border_radius_hover
        self.border_radius_clicked: Optional[int] = border_radius_clicked
        self.border_deactivated: Optional[int] = border_deactivated
        #
        ## Border Color. ##
        #
        self.border_color: ND_Color = border_color
        self.border_color_hover: Optional[ND_Color] = border_color_hover
        self.border_color_clicked: Optional[ND_Color] = border_color_clicked
        self.border_color_deactivated: Optional[ND_Color] = border_color_deactivated

        #
        ### Background color for buttons / LineEdit / Checkbox / SelectOption / NumberInput / ... ###
        #
        self.bg_color: ND_Color = bg_color
        self.bg_color_hover: Optional[ND_Color] = bg_color_hover
        self.bg_color_clicked: Optional[ND_Color] = bg_color_clicked
        self.bg_color_deactivated: Optional[ND_Color] = bg_color_deactivated

        #
        ### Background texture for buttons / Checkbox / ... ###
        #
        self.bg_texture: Optional[int | str] = bg_texture
        self.bg_texture_hover: Optional[int | str] = bg_texture_hover
        self.bg_texture_clicked: Optional[int | str] = bg_texture_clicked
        self.bg_texture_deactivated: Optional[int | str] = bg_texture_deactivated

        #
        ### Texture Transformations for buttons / Checkbox / ... ###
        #
        self.transformation: ND_Transformation = transformation
        self.transformation_hover: Optional[ND_Transformation] = transformation_hover
        self.transformation_clicked: Optional[ND_Transformation] = transformation_clicked
        self.transformation_deactivated: Optional[ND_Transformation] = transformation_deactivated


    #
    def get_attribute(self, attribute_name: str, elt_state: str = "normal", styles_override: Optional[dict[str, Any]] = None) -> Optional[Any]:

        #
        attribute_name_with_state_full: str = f"{attribute_name}_{elt_state}"
        #
        attribute_name_with_state: str = attribute_name if elt_state == "normal" else attribute_name_with_state_full

        #
        if styles_override is not None:
            #
            if attribute_name in styles_override:
                #
                return styles_override[attribute_name]
            #
            elif attribute_name_with_state_full in styles_override:
                #
                return styles_override[attribute_name_with_state_full]

        #
        if not hasattr(self, attribute_name):
            #
            return None

        #
        if not hasattr(self, attribute_name_with_state) or getattr(self, attribute_name_with_state) is None:
            #
            return getattr(self, attribute_name)

        #
        return getattr(self, attribute_name_with_state)
