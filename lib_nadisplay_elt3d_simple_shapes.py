"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

_summary_

"""


#
import numpy as np
#
from lib_nadisplay_core import ND_Window
from lib_nadisplay_point_3d import ND_Point_3D
from lib_nadisplay_elt3d_core import ND_Elt_3D, ND_Elt_Camera_3D, generate_elt_id, apply_points_transformation, project_3d_points_global_space_to_camera_space_view
from lib_nadisplay_colors import ND_Color


#
class ND_Elt3D_SimpleSphere(ND_Elt_3D):

    #
    def __init__(
        self,
        win: ND_Window,
        radius: float,
        color: ND_Color,
        elt_id: str = generate_elt_id(),
        origin: ND_Point_3D = ND_Point_3D(x=0, y=0, z=0),
        rotation: ND_Point_3D = ND_Point_3D(x=0, y=0, z=0),
        scale: ND_Point_3D = ND_Point_3D(x=0, y=0, z=0),
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
        self.radius: float = radius
        self.color: ND_Color = color
        #
        self.cache_transform_key: str = f"transform_cache"


    #
    def render(self, cam_origin: ND_Point_3D, cam_direction: ND_Point_3D, cam_fov: float, cam_elt: ND_Elt_Camera_3D) -> None:

        #
        if not self.visible:
            #
            return

        #
        ### Approximate rendering: Sample points on the sphere's surface (equator and meridians), ###
        ### transform them (scale, rotate, translate), project to 2D, and draw as filled polygon. ###
        ### Use 32 points for smoothness. Cache if no changes. ###
        #

        #
        cache_key: str = f"cam_{cam_origin}_{cam_direction}_{cam_fov}"
        #
        if cache_key in self.caches:
            #
            screen_x_coords, screen_y_coords = self.caches[cache_key]
        #
        else:
            #
            ### Generate local sphere points (simple icosphere approx or parametric). ###
            ### For simplicity, sample in theta/phi. ###
            #
            num_samples: int = 32
            #
            local_points: list[ND_Point_3D] = []
            #
            for i in range(num_samples):
                #
                theta: float = 2 * np.pi * i / num_samples
                for j in range(num_samples // 2):
                    phi: float = np.pi * j / (num_samples // 2)
                    x: float = self.radius * np.sin(phi) * np.cos(theta)
                    y: float = self.radius * np.sin(phi) * np.sin(theta)
                    z: float = self.radius * np.cos(phi)
                    local_points.append(ND_Point_3D(x=x, y=y, z=z))

            #
            ### Transform to world space. ###
            #
            transformed_points: list[ND_Point_3D]
            #
            if self.cache_transform_key in self.caches:
                #
                transformed_points = self.caches[self.cache_transform_key]
            #
            else:
                #
                transformed_points = apply_points_transformation(
                    points_to_transform_in_element_space=local_points,
                    elt3d_origin=self.origin,
                    elt3d_rotation=self.rotation,
                    elt3d_scale=self.scale,
                )
                #
                self.caches[self.cache_transform_key] = transformed_points

            #
            ### Project to normalized camera space. ###
            #
            projected_points: list[ND_Point_3D] = project_3d_points_global_space_to_camera_space_view(
                points_in_global_coords=transformed_points,
                cam_origin=cam_origin,
                cam_direction=cam_direction,
                cam_fov=cam_fov
            )

            #
            ### Map to screen coordinates (assuming camera elt has x, y, w, h). ###
            #
            screen_x_coords: list[int] = []
            screen_y_coords: list[int] = []
            #
            for proj in projected_points:
                #
                screen_x: int = int(cam_elt.x + cam_elt.w / 2 + proj.x * (cam_elt.w / 2))
                screen_y: int = int(cam_elt.y + cam_elt.h / 2 - proj.y * (cam_elt.h / 2))  # Flip y for top-left
                #
                screen_x_coords.append(screen_x)
                screen_y_coords.append(screen_y)

            #
            self.caches[cache_key] = (screen_x_coords, screen_y_coords)

        #
        ### Draw filled polygon with the projected points. ###
        #
        self.win.draw_filled_polygon(
            x_coords=screen_x_coords,
            y_coords=screen_y_coords,
            fill_color=self.color
        )

