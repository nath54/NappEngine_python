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
import numpy as np
from numpy.typing import NDArray
#
from lib_nadisplay_position import ND_Position
from lib_nadisplay_core import ND_Window, ND_Elt, ND_EventsHandler_Elts
from lib_nadisplay_point_3d import ND_Point_3D, EPSILON


#
unique_elt_id_counter: int = 0

#
def generate_elt_id() -> str:

    #
    global unique_elt_id_counter

    #
    unique_elt_id_counter += 1

    #
    return f"unique_elt_id_{unique_elt_id_counter}"


#
def apply_point_transformation(
    point_to_transform_in_element_space: ND_Point_3D,
    elt3d_origin: ND_Point_3D,
    elt3d_rotation: ND_Point_3D,
    elt3d_scale: ND_Point_3D,
) -> ND_Point_3D:

    #
    ### Apply rotation (in degrees) and scaling relative to the element origin. ###
    #
    point: ND_Point_3D = point_to_transform_in_element_space.clone()

    #
    # Apply scaling component-wise.
    #
    point.data *= np.array([elt3d_scale.x, elt3d_scale.y, elt3d_scale.z])

    #
    # Apply rotation using Euler angles in XYZ order.
    #
    rx: float = np.deg2rad(elt3d_rotation.x)
    ry: float = np.deg2rad(elt3d_rotation.y)
    rz: float = np.deg2rad(elt3d_rotation.z)

    #
    rot_x_lst: list[list[float]] = [
        [1, 0, 0],
        [0, np.cos(rx), -np.sin(rx)],
        [0, np.sin(rx), np.cos(rx)]
    ]

    #
    rot_y_lst: list[list[float]] = [
        [np.cos(ry), 0, np.sin(ry)],
        [0, 1, 0],
        [-np.sin(ry), 0, np.cos(ry)]
    ]

    #
    rot_z_lst: list[list[float]] = [
        [np.cos(rz), -np.sin(rz), 0],
        [np.sin(rz), np.cos(rz), 0],
        [0, 0, 1]
    ]

    #
    rot_x: NDArray[np.float32] = np.array(rot_x_lst)
    rot_y: NDArray[np.float32] = np.array(rot_y_lst)
    rot_z: NDArray[np.float32] = np.array(rot_z_lst)

    #
    R = rot_z @ rot_y @ rot_x
    #
    point.data = (R @ point.data).astype(dtype=np.float32)

    #
    ### Apply translation by origin. ###
    #
    point += elt3d_origin

    #
    return point


#
def project_3d_point_global_space_to_camera_space_view(
    point_in_global_coords: ND_Point_3D,
    cam_origin: ND_Point_3D,
    cam_direction: ND_Point_3D,
    cam_fov: float
) -> ND_Point_3D:

    #
    ### Project a point to the 2d camera space. Returns a 2d point in a 3d point container with z=0 ###
    #
    world_up = ND_Point_3D(x=0, y=1, z=0)

    #
    ### Normalize camera direction to get forward vector. ###
    #
    forward: ND_Point_3D = cam_direction.clone()
    #
    norm: float = float( np.linalg.norm(forward.data) )
    #
    if norm > EPSILON:
        #
        forward.data /= norm
    #
    else:
        #
        ### Degenerate case: invalid direction, return origin. ###
        #
        return ND_Point_3D()

    #
    ### Compute right vector: cross(world_up, forward). ###
    #
    right_data: NDArray[np.float32] = np.cross(world_up.data, forward.data)
    right: ND_Point_3D = ND_Point_3D(from_data=right_data)
    #
    norm: float = float( np.linalg.norm(right.data) )
    #
    if norm > EPSILON:
        #
        right.data /= norm
    #
    else:
        #
        ### Gimbal lock or degenerate: fallback to arbitrary right. ###
        #
        right = ND_Point_3D(x=1, y=0, z=0)

    #
    ### Compute up vector: cross(forward, right). ###
    #
    up_data: NDArray[np.float32] = np.cross(forward.data, right.data)
    up: ND_Point_3D = ND_Point_3D(from_data=up_data)
    norm: float = float( np.linalg.norm(up.data) )
    #
    if norm > EPSILON:
        #
        up.data /= norm

    #
    ### Build view rotation matrix (transpose of basis). ###
    #
    basis: NDArray[np.float32] = np.column_stack((right.data, up.data, forward.data))
    R_view: NDArray[np.float32] = basis.T

    #
    ### Transform to camera space. ###
    #
    point_cam_data: NDArray[np.float32] = ( R_view @ (point_in_global_coords.data - cam_origin.data) ).astype(dtype=np.float32)
    point_cam: ND_Point_3D = ND_Point_3D(from_data=point_cam_data)

    #
    ### Perspective projection to normalized [-1, 1]. ###
    #
    rad_fov: float = np.deg2rad(cam_fov)
    tan_half_fov: float = np.tan(rad_fov / 2)
    #
    if abs(point_cam.z) < EPSILON:
        #
        ### Avoid division by zero: treat as at infinity or clip. ###
        #
        return ND_Point_3D()

    #
    x_proj: float = point_cam.x / (point_cam.z * tan_half_fov)
    y_proj: float = point_cam.y / (point_cam.z * tan_half_fov)

    #
    return ND_Point_3D(x=x_proj, y=y_proj, z=0)


#
def apply_points_transformation(
    points_to_transform_in_element_space: list[ND_Point_3D],
    elt3d_origin: ND_Point_3D,
    elt3d_rotation: ND_Point_3D,
    elt3d_scale: ND_Point_3D,
) -> list[ND_Point_3D]:

    #
    n: int = len(points_to_transform_in_element_space)

    #
    points_data: NDArray[np.float32] = np.zeros( (n, 3), dtype=np.float32 )
    #
    for i, p in enumerate(points_to_transform_in_element_space):
        #
        points_data[i] = p.data

    #
    ### Apply scaling component-wise. ###
    #
    points_data *= elt3d_scale.data

    #
    ### Apply rotation using Euler angles in XYZ order. ###
    #
    rx: float = np.deg2rad(elt3d_rotation.x)
    ry: float = np.deg2rad(elt3d_rotation.y)
    rz: float = np.deg2rad(elt3d_rotation.z)

    #
    rot_x_lst: list[list[float]] = [
        [1, 0, 0],
        [0, np.cos(rx), -np.sin(rx)],
        [0, np.sin(rx), np.cos(rx)]
    ]

    #
    rot_y_lst: list[list[float]] = [
        [np.cos(ry), 0, np.sin(ry)],
        [0, 1, 0],
        [-np.sin(ry), 0, np.cos(ry)]
    ]

    #
    rot_z_lst: list[list[float]] = [
        [np.cos(rz), -np.sin(rz), 0],
        [np.sin(rz), np.cos(rz), 0],
        [0, 0, 1]
    ]

    #
    rot_x: NDArray[np.float32] = np.array(rot_x_lst)
    rot_y: NDArray[np.float32] = np.array(rot_y_lst)
    rot_z: NDArray[np.float32] = np.array(rot_z_lst)

    #
    R = rot_z @ rot_y @ rot_x
    #
    points_data = (R @ points_data.T).T.astype(dtype=np.float32)

    #
    ### Apply translation by origin. ###
    #
    points_data += elt3d_origin.data

    #
    ### Returns points ###
    #
    transformed_points: list[ND_Point_3D] = [
        ND_Point_3D(from_data=points_data[i])
        for i in range(n)
    ]

    #
    return transformed_points


#
def project_3d_points_global_space_to_camera_space_view(
    points_in_global_coords: list[ND_Point_3D],
    cam_origin: ND_Point_3D,
    cam_direction: ND_Point_3D,
    cam_fov: float
) -> list[ND_Point_3D]:

    #
    n: int = len(points_in_global_coords)
    #
    if n == 0:
        #
        return []

    #
    points_data: NDArray[np.float32] = np.zeros( (n, 3), dtype=np.float32 )
    #
    for i, p in enumerate(points_in_global_coords):
        #
        points_data[i] = p.data

    #
    world_up = np.array([0, 1, 0], dtype=np.float32)

    #
    ### Normalize camera direction to get forward vector. ###
    #
    forward_data: NDArray[np.float32] = cam_direction.data.copy()
    #
    norm: float = float( np.linalg.norm(forward_data) )
    #
    if norm > EPSILON:
        #
        forward_data /= norm
    #
    else:
        #
        ### Degenerate case: invalid direction, return list of origins. ###
        #
        return [ND_Point_3D() for _ in range(n)]

    #
    ### Compute right vector: cross(world_up, forward). ###
    #
    right_data: NDArray[np.float32] = np.cross(world_up, forward_data)
    #
    norm: float = float( np.linalg.norm(right_data) )
    #
    if norm > EPSILON:
        #
        right_data /= norm
    #
    else:
        #
        ### Gimbal lock or degenerate: fallback to arbitrary right. ###
        #
        right_data = np.array([1, 0, 0], dtype=np.float32)

    #
    ### Compute up vector: cross(forward, right). ###
    #
    up_data: NDArray[np.float32] = np.cross(forward_data, right_data)
    norm: float = float( np.linalg.norm(up_data) )
    #
    if norm > EPSILON:
        #
        up_data /= norm

    #
    ### Build view rotation matrix (transpose of basis). ###
    #
    basis: NDArray[np.float32] = np.column_stack((right_data, up_data, forward_data))
    R_view: NDArray[np.float32] = basis.T

    #
    ### Transform to camera space. ###
    #
    points_cam_data: NDArray[np.float32] = ( R_view @ (points_data - cam_origin.data).T ).T.astype(dtype=np.float32)

    #
    ### Perspective projection to normalized [-1, 1]. ###
    #
    rad_fov: float = np.deg2rad(cam_fov)
    tan_half_fov: float = np.tan(rad_fov / 2)

    #
    z: NDArray[np.float32] = points_cam_data[:, 2]
    #
    mask: NDArray[np.bool_] = np.abs(z) >= EPSILON

    #
    x_proj: NDArray[np.float32] = np.zeros(n, dtype=np.float32)
    y_proj: NDArray[np.float32] = np.zeros(n, dtype=np.float32)
    #
    x_proj[mask] = points_cam_data[mask, 0] / (z[mask] * tan_half_fov)
    y_proj[mask] = points_cam_data[mask, 1] / (z[mask] * tan_half_fov)

    #
    proj_data: NDArray[np.float32] = np.zeros((n, 3), dtype=np.float32)
    proj_data[:, 0] = x_proj
    proj_data[:, 1] = y_proj
    proj_data[:, 2] = 0

    #
    return [ND_Point_3D(from_data=proj_data[i]) for i in range(n)]


#
### Abstract class for 3d elements that will be rendered. ###
#
class ND_Elt_3D:

    #
    def __init__(
        self,
        win: ND_Window,
        elt_id: str = generate_elt_id(),
        origin: ND_Point_3D = ND_Point_3D(x=0, y=0, z=0),
        rotation: ND_Point_3D = ND_Point_3D(x=0, y=0, z=0),
        scale: ND_Point_3D = ND_Point_3D(x=1, y=1, z=1)
    ) -> None:

        #
        self.win: ND_Window = win
        #
        self.elt_id: str = elt_id
        #
        self.visible: bool = True
        #
        self.origin: ND_Point_3D = origin
        #
        self.rotation: ND_Point_3D = rotation
        #
        self.scale: ND_Point_3D = scale

        #
        ### Caches to avoid calculating transformations and camera projections at each drawing frame if not needed. ###
        ### Cache variables for transformation (rotation, scaling) starts with "transform_".  ###
        ### Cache variables for camera projections starts with "cam_".  ###
        #
        self.caches: dict[str, Any] = {}

    #
    ### Called when this element moves, rotates or scales. ###
    #
    def clear_full_cache(self) -> None:

        #
        self.caches.clear()


    #
    def clear_camera_cache(self) -> None:

        #
        for k in list( self.caches.keys() ):
            #
            if k.startswith("cam_"):
                #
                del self.caches[k]


    #
    def render(self, cam_origin: ND_Point_3D, cam_direction: ND_Point_3D, cam_fov: float, cam_elt: 'ND_Elt_Camera_3D') -> None:

        #
        ### Abstract Function. ###
        #
        pass


#
class ND_Space_3D(ND_Elt):

    #
    ### Init function. ###
    #
    def __init__(
            self, window: ND_Window,
            elt_id: str,
            position: ND_Position,
            elts: Optional[list[ND_Elt_3D]] = None,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)

        #
        self.elts: dict[str, ND_Elt_3D] = {}

        #
        ### Sub Chunks for efficient collisions & elements recovery. ###
        #
        self.chunk_size: float = 20.0
        #
        self.chunks: dict[str, set[str]] = {}
        #
        self.elts_chunks: dict[str, str] = {}

        #
        if elts:

            #
            for elt in elts:
                #
                self.add_elt_to_chunk(elt=elt)

    #
    ### Function to get chunk position. ###
    #
    def get_chunk_position(self, position: ND_Point_3D) -> tuple[int, int, int]:

        #
        cx: int = floor( position.x / self.chunk_size )
        cy: int = floor( position.y / self.chunk_size )
        cz: int = floor( position.z / self.chunk_size )

        #
        return cx, cy, cz

    #
    ### Function to get chunk key from chunk position. ###
    #
    def get_chunk_id_from_chunk_position(self, cx: int, cy: int, cz: int) -> str:

        #
        return f"{cx}_{cy}_{cz}"

    #
    ### Function to get chunk key from a 3d point. ###
    #
    def get_chunk_id_from_position(self, position: ND_Point_3D) -> str:

        #
        return self.get_chunk_id_from_chunk_position(
            *self.get_chunk_position(position=position)
        )

    #
    ### Function to add a 3d element to the chunk. ###
    #
    def add_elt_to_chunk(self, elt: ND_Elt_3D) -> None:

        #
        ckey: str = self.get_chunk_id_from_position(elt.origin)

        #
        if ckey not in self.chunks:

            #
            self.chunks[ckey] = set()

        #
        self.chunks[ckey].add( elt.elt_id )
        #
        self.elts_chunks[elt.elt_id] = ckey
        #
        self.elts[elt.elt_id] = elt

    #
    ### Function to update the chunk of an element (to use when elements move). ###
    #
    def update_elt_chunk(self, elt_id: Optional[str] = None, elt: Optional[ND_Elt_3D] = None) -> None:

        #
        if elt is not None:

            #
            elt_id = elt.elt_id

        #
        if elt_id is not None:

            #
            ckey: str = self.get_chunk_id_from_position(self.elts[elt_id].origin)

            #
            if ckey not in self.chunks:

                #
                self.chunks[ckey] = set()

            #
            if elt_id not in self.elts_chunks:

                #
                self.chunks[ckey].add( elt_id )
                #
                self.elts_chunks[elt_id] = ckey
                #
                return

            #
            old_ckey: str = self.elts_chunks[elt_id]

            #
            if ckey != old_ckey:

                #
                self.chunks[old_ckey].remove( elt_id )

                #
                if len( self.chunks[old_ckey] ) == 0:
                    #
                    del self.chunks[old_ckey]

                #
                self.chunks[ckey].add( elt_id )
                #
                self.elts_chunks[elt_id] = ckey
                #
                return

    #
    ### Function to remove an element from the 3d scene. ###
    #
    def remove_elt(self, elt_id: Optional[str] = None, elt: Optional[ND_Elt_3D] = None) -> None:

        #
        if elt is not None:

            #
            elt_id = elt.elt_id

        #
        if elt_id is not None:

            #
            old_ckey: str = self.elts_chunks[elt_id]

            #
            if old_ckey in self.chunks:

                #
                self.chunks[old_ckey].remove( elt_id )

                #
                if len( self.chunks[old_ckey] ) == 0:
                    #
                    del self.chunks[old_ckey]

            #
            del self.elts_chunks[elt_id]

            #
            del self.elts[elt_id]

    #
    ### Function to get all the elements that are inside a sphere of a certain radius. (To check collisions for instance) ###
    #
    def get_all_elts_inside_sphere_of_radius(self, center: ND_Point_3D, radius: float) -> list[ND_Elt_3D]:

        #
        result: list[ND_Elt_3D] = []

        #
        cx: int
        cy: int
        cz: int

        #
        ocx, ocy, ocz = self.get_chunk_position(position=center)

        #
        rad: int = ceil( radius / self.chunk_size )

        #
        for cx in range( ocx - rad, ocx + rad + 1 ):

            #
            for cy in range( ocy - rad, ocy + rad + 1 ):

                #
                for cz in range( ocz - rad, ocz + rad + 1):

                    #
                    ckey: str = self.get_chunk_id_from_chunk_position(cx=cx, cy=cy, cz=cz)

                    #
                    if ckey not in self.chunks:
                        #
                        continue

                    #
                    elt_id: str
                    #
                    for elt_id in self.chunks[ckey]:
                        #
                        elt: ND_Elt_3D = self.elts[elt_id]
                        #
                        d: float = center.distance_to( elt.origin )
                        #
                        if d < radius:
                            #
                            result.append( elt )

        #
        return result

    #
    ### Function to render the 3D space. ###
    #
    def render(self) -> None:
        #
        ### Will be rendered by a ND_Elt_Camera_3D. ###
        #
        pass


#
class ND_Elt_Camera_3D(ND_Elt):

    #
    ### Init function, constructor. ###
    #
    def __init__(
            self,
            window: ND_Window,
            elt_id: str,
            position:ND_Position,
            origin: ND_Point_3D,
            direction: ND_Point_3D,
            fov: float,
            rendering_distance: float,
            space_3D: ND_Space_3D,
            edges_margin: float = 20,
            style_name: str ="default",
            styles_override: Optional[dict[str, Any]] = None,
            events_handler: Optional[ND_EventsHandler_Elts] = None
        ) -> None:

        #
        super().__init__(window=window, elt_id=elt_id, position=position, style_name=style_name, styles_override=styles_override, events_handler=events_handler)
        #
        self.space_3D: ND_Space_3D = space_3D

        #
        ### 3D Camera transformations. ###
        #
        self.origin: ND_Point_3D = origin
        self.direction: ND_Point_3D = direction
        self.fov: float = fov
        self.rendering_distance: float = rendering_distance

        #
        ### Each distance to origin for each visible objects. ###
        #
        self.visible_objects_distances_to_origin: dict[str, float] = {}

        #
        ### Elements that are close to the limit of the camera field of view. ###
        #
        self.edges_margin: float = edges_margin
        #
        self.edges_elements: set[str] = set()

        #
        ### Z order cache ###
        ### List of the id of the elements to render in the correct order, from the farthest to the closest. ###
        #
        self.z_order_cache: list[str] = []


    #
    ###
    #
    def elt_visible_check(self, elt: ND_Elt_3D) -> tuple[bool, bool, float]:

        #
        ### Compute camera-space position of the element's origin. ###
        #
        world_up = ND_Point_3D(x=0, y=1, z=0)
        forward: ND_Point_3D = self.direction.clone()
        #
        norm: float = float(np.linalg.norm(forward.data))
        #
        if norm > EPSILON:
            #
            forward.data /= norm
        #
        else:
            #
            return (False, False, -1)  # Invalid camera direction

        #
        right_data: NDArray[np.float32] = np.cross(world_up.data, forward.data)
        right: ND_Point_3D = ND_Point_3D(from_data=right_data)
        #
        norm = float(np.linalg.norm(right.data))
        #
        if norm > EPSILON:
            #
            right.data /= norm
        #
        else:
            #
            right = ND_Point_3D(x=1, y=0, z=0)

        #
        up_data: NDArray[np.float32] = np.cross(forward.data, right.data)
        up: ND_Point_3D = ND_Point_3D(from_data=up_data)
        #
        norm = float(np.linalg.norm(up.data))
        #
        if norm > EPSILON:
            #
            up.data /= norm

        #
        basis: NDArray[np.float32] = np.column_stack((right.data, up.data, forward.data))
        R_view: NDArray[np.float32] = basis.T

        #
        point_cam_data: NDArray[np.float32] = (R_view @ (elt.origin.data - self.origin.data)).astype(dtype=np.float32)
        point_cam: ND_Point_3D = ND_Point_3D(from_data=point_cam_data)

        #
        ### Check if in front and within rendering distance. ###
        #
        if point_cam.z <= EPSILON or point_cam.z >= self.rendering_distance:
            #
            return (False, False, -1)

        #
        ### Project to normalized [-1, 1]. ###
        #
        rad_fov: float = np.deg2rad(self.fov)
        tan_half_fov: float = np.tan(rad_fov / 2)
        #
        x_proj: float = point_cam.x / (point_cam.z * tan_half_fov)
        y_proj: float = point_cam.y / (point_cam.z * tan_half_fov)

        #
        ### Check if within view frustum (ignoring aspect for simplicity). ###
        #
        is_visible: bool = abs(x_proj) <= 1 and abs(y_proj) <= 1

        #
        ### Compute edge: Use normalized margin based on screen size (assume square). ###
        #
        margin_norm: float = self.edges_margin / (self.w / 2.0)  # Approx, horizontal
        #
        is_in_edge: bool = (
            is_visible and (
                abs(x_proj) > 1 - margin_norm or
                abs(y_proj) > 1 - margin_norm or
                point_cam.z > self.rendering_distance - self.edges_margin or  # Distance margin (arbitrary units)
                point_cam.z < self.edges_margin  # Near edge
            )
        )

        #
        distance_from_camera_origin_z_order: float = point_cam.z

        #
        return (is_visible, is_in_edge, distance_from_camera_origin_z_order)


    #
    ### Function to do a full check for all the visibles objects. (To do at initialisation after all objects added to the scene, or for abrupt camera movement) ###
    #
    def full_check_for_visible_elts(self) -> None:

        #
        self.visible_objects_distances_to_origin.clear()
        self.edges_elements.clear()

        #
        elt_id: str
        elt: ND_Elt_3D
        #
        for elt_id, elt in self.space_3D.elts.items():

            #
            is_visible, is_edge, distance_to_origin = self.elt_visible_check(elt=elt)
            #
            if is_visible:
                #
                self.visible_objects_distances_to_origin[elt_id] = distance_to_origin
            #
            if is_edge:
                #
                self.edges_elements.add( elt_id )


    #
    ### Function to do a check for visibles objects only with objects that are at the limit / edges of the camera. (for soft camera movements) ###
    #
    def soft_check_for_visible_elts(self) -> None:

        #
        for elt_id in list( self.edges_elements ):

            #
            is_visible, is_edge, distance_to_origin = self.elt_visible_check(elt=self.space_3D.elts[elt_id])

            #
            if not is_visible:
                #
                del self.visible_objects_distances_to_origin[elt_id]
                self.edges_elements.remove(elt_id)
            #
            else:
                #
                self.visible_objects_distances_to_origin[elt_id] = distance_to_origin

                #
                if not is_edge:
                    #
                    self.edges_elements.remove( elt_id )


    #
    ### Update visible elements distance to origin. ###
    #
    def update_visible_elts_distance_to_origin(self) -> None:

        #
        for elt_id in list( self.visible_objects_distances_to_origin.keys() ):

            #
            is_visible, is_edge, distance_to_origin = self.elt_visible_check(elt=self.space_3D.elts[elt_id])

            #
            if not is_visible:
                #
                del self.visible_objects_distances_to_origin[elt_id]
                #
                if elt_id in self.edges_elements:
                    #
                    self.edges_elements.remove(elt_id)
            #
            else:
                #
                self.visible_objects_distances_to_origin[elt_id] = distance_to_origin

                #
                if elt_id not in self.edges_elements and is_edge:
                    #
                    self.edges_elements.add( elt_id )
                #
                elif elt_id in self.edges_elements and not is_edge:
                    #
                    self.edges_elements.remove( elt_id )


    #
    ### Function to update the z order cache. (for each camera movements / large elements movements) ###
    #
    def update_z_order_cache(self) -> None:

        #
        self.z_order_cache = list( self.visible_objects_distances_to_origin.keys() )

        #
        self.z_order_cache.sort( key=lambda elt_id: self.visible_objects_distances_to_origin[elt_id], reverse=True )


    #
    ### Function to render the 3D scene. ###
    #
    def render(self) -> None:

        #
        self.window.enable_area_drawing_constraints(
            x=self.x, y=self.y, width=self.w, height=self.h
        )

        #
        elt_id: str
        #
        for elt_id in self.z_order_cache:

            #
            self.space_3D.elts[elt_id].render(
                cam_origin=self.origin,
                cam_direction=self.direction,
                cam_fov=self.fov,
                cam_elt=self
            )

        #
        self.window.disable_area_drawing_constraints()

        #
        return

