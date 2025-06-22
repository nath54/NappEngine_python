"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


from typing import Optional

from lib_nadisplay_rects import ND_Rect



#
class ND_Quadtree:
    #
    def __init__(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        max_objects: int = 10,
        max_levels: int = 4,
        level: int = 0
    ) -> None:
        """Initialize the quadtree node with optional bounds and no fixed size."""

        #
        self.bounds: ND_Rect = ND_Rect(x or 0, y or 0, width or 0, height or 0)
        self.max_objects: int = max_objects
        self.max_levels: int = max_levels
        self.level: int = level
        self.objects: list[tuple[ND_Rect, str]] = []  # Now stores tuples of (rect, id)
        self.nodes: list['ND_Quadtree'] = []
        self.has_fixed_bounds: bool = x is not None and y is not None and width is not None and height is not None

    #
    def _expand(self, rect: ND_Rect) -> None:
        """Expand the quadtree boundaries to accommodate the new rect."""

        #
        if self.bounds.w == 0 and self.bounds.h == 0:
            # First insertion, establish the boundary with the size of the object
            self.bounds = ND_Rect(rect.x, rect.y, rect.w, rect.h)
            return

        # Expand the current bounds if the rect is outside
        new_x = min(self.bounds.x, rect.x)
        new_y = min(self.bounds.y, rect.y)
        new_right = max(self.bounds.x + self.bounds.w, rect.x + rect.w)
        new_bottom = max(self.bounds.y + self.bounds.h, rect.y + rect.h)

        new_width = new_right - new_x
        new_height = new_bottom - new_y

        # Create a new root that covers the expanded area
        new_bounds = ND_Rect(new_x, new_y, new_width, new_height)
        self._shift_and_expand(new_bounds)

    #
    def _shift_and_expand(self, new_bounds: ND_Rect) -> None:
        """Shift current tree and redistribute existing objects."""

        #
        self.bounds = new_bounds

        # If this was a non-empty quadtree, we need to reinsert the existing elements
        if self.objects or self.nodes:
            temp_objects = self.objects[:]
            self.objects.clear()

            # Reset the nodes and reinsert objects
            self.nodes.clear()
            for obj, obj_id in temp_objects:
                self.insert(obj, obj_id)

    #
    def subdivide(self) -> None:
        """Subdivide the current node into 4 quadrants."""

        #
        sub_width = self.bounds.w // 2
        sub_height = self.bounds.h // 2
        x, y = self.bounds.x, self.bounds.y

        self.nodes = [
            ND_Quadtree(x, y, sub_width, sub_height, self.max_objects, self.max_levels, self.level + 1),
            ND_Quadtree(x + sub_width, y, sub_width, sub_height, self.max_objects, self.max_levels, self.level + 1),
            ND_Quadtree(x, y + sub_height, sub_width, sub_height, self.max_objects, self.max_levels, self.level + 1),
            ND_Quadtree(x + sub_width, y + sub_height, sub_width, sub_height, self.max_objects, self.max_levels, self.level + 1)
        ]

    #
    def insert(self, rect: ND_Rect, obj_id: str) -> None:
        """Insert an object (with its id) into the quadtree, expanding it as needed."""

        #
        if not self.has_fixed_bounds:
            # If the quadtree is dynamically expanding, we may need to adjust the boundaries
            self._expand(rect)

        if self.nodes:
            # Insert into one of the sub-nodes if we are subdivided
            index = self.get_index(rect)
            if index != -1:
                self.nodes[index].insert(rect, obj_id)
                return

        # Otherwise, insert into this node
        self.objects.append((rect, obj_id))

        # If the number of objects exceeds the limit, subdivide if necessary
        if len(self.objects) > self.max_objects and self.level < self.max_levels:
            if not self.nodes:
                self.subdivide()

            i = 0
            while i < len(self.objects):
                obj_rect, obj_id = self.objects[i]
                index = self.get_index(obj_rect)
                if index != -1:
                    self.objects.pop(i)
                    self.nodes[index].insert(obj_rect, obj_id)
                else:
                    i += 1

    #
    def get_index(self, rect: ND_Rect) -> int:
        """Determine which quadrant the object belongs to in the current node."""

        #
        mid_x = self.bounds.x + self.bounds.w / 2
        mid_y = self.bounds.y + self.bounds.h / 2

        top = rect.y < mid_y
        bottom = rect.y + rect.h > mid_y
        left = rect.x < mid_x
        right = rect.x + rect.w > mid_x

        if top and right:
            return 1
        elif bottom and left:
            return 2
        elif bottom and right:
            return 3
        elif top and left:
            return 0
        return -1

    #
    def retrieve(self, rect: ND_Rect) -> list[tuple[ND_Rect, str]]:
        """Retrieve all objects that could collide with the given rect."""

        #
        result = self.objects[:]
        if self.nodes:
            index = self.get_index(rect)
            if index != -1:
                result.extend(self.nodes[index].retrieve(rect))
        return result

    #
    def get_colliding_ids(self, point: tuple[int, int]) -> list[str]:
        """Retrieve IDs of all elements colliding with a given point."""

        #
        point_rect = ND_Rect(point[0], point[1], 1, 1)  # Represent the point as a tiny rectangle
        potential_collisions = self.retrieve(point_rect)

        colliding_ids: list[str] = []
        for obj_rect, obj_id in potential_collisions:
            if (obj_rect.x <= point[0] <= obj_rect.x + obj_rect.w and
                obj_rect.y <= point[1] <= obj_rect.y + obj_rect.h):
                colliding_ids.append(obj_id)

        return colliding_ids
