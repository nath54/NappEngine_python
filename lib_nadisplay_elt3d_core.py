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
class ND_Elt_3D:

    #
    def __init__(self, elt_id: str = generate_elt_id(), origin: ND_Point_3D = ND_Point_3D(x=0, y=0, z=0)) -> None:
        #
        self.elt_id: str = elt_id
        #
        self.origin: ND_Point_3D = origin

    #
    def render(self) -> None:
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
        ### Z order cache ###
        ### List of the id of the elements to render in the correct order, from the farthest to the closest. ###
        #
        self.z_order_cache: list[str] = []

    #
    ### Function to do a full check for all the visibles objects. (To do at initialisation after all objects added to the scene, or for abrupt camera movement) ###
    #
    def full_check_for_visible_objects(self) -> None:

        #
        ### TODO: for all the objects in the scene, check if they are visible. ###
        #
        pass

    #
    ### Function to do a check for visibles objects only with objects that are at the limit / edges of the camera. (for soft camera movements) ###
    #
    def soft_check_for_visible_objects(self) -> None:

        #
        ### TODO. ###
        #
        pass

    #
    ### Function to update the visibility of an unique elements. (For elements movements) ###
    #
    def update_visibility_of_elt(self, elt_id: Optional[str] = None, elt: Optional[ND_Elt_3D] = None):

        #
        if elt_id:
            #
            elt = self.space_3D.elts[elt_id]

        #
        if not elt:
            #
            return

        #
        ### TODO. ###
        #
        pass

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
        elt_id: str
        #
        for elt_id in self.z_order_cache:

            #
            ### TODO. ###
            #
            pass

        #
        return

