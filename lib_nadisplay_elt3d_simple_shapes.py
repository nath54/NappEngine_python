"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""


#
from typing import Optional, Any
#
from math import floor, ceil
#
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Elt, ND_EventsHandler_Elts
from lib_nadisplay_point_3d import ND_Point_3D
from lib_nadisplay_elt3d_core import ND_Elt_3D, generate_elt_id, apply_point_transformation, project_3d_point_global_space_to_camera_space_view
from lib_nadisplay_colors import ND_Color


#
class ND_Elt3D_SimpleSphere(ND_Elt_3D):

    #
    def __init__(
        self,
        win: ND_Window,
        elt_id: str = generate_elt_id(),
        origin: ND_Point_3D = ND_Point_3D(x=0, y=0, z=0),
        rotation: ND_Point_3D = ND_Point_3D(x=0, y=0, z=0),
        scale: ND_Point_3D = ND_Point_3D(x=0, y=0, z=0),
        radius: float,
        color: ND_Color,
    ) -> None:

        #
        super().__init__(
            win=win,
            elt_id=elt_id,
            origin=origin,
            rotation=rotation,
            scale=scale
        )

        #
        ###
        #
        self.origine_cache_transform: Optional[ND_Point_3D] = None
        self.radius_cache_transform: Optional[float] = None

        #
        ###
        #
        self.camera_cache: Optional[Any] = None  # TODO: complete the type

    #
    def render(self, cam_origin: ND_Point_3D, cam_direction: ND_Point_3D, cam_fov: float) -> None:

        #
        ### TODO: Render a sphere (or ellipse in function of scaling and rotation). ###
        #
        pass



