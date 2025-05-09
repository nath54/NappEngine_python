"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Some utility classes for manipuling points, rects and base elements positions.

"""

#
from typing import Optional, Union
from dataclasses import dataclass
#
from math import sqrt
import numpy as np

# Define a small epsilon for floating point comparisons to handle precision issues
# Adjust based on expected scale of coordinates if needed
EPSILON: float = 1e-6

#
class ND_Point:
    #
    def __init__(self, x: int, y: int) -> None:
        #
        self.x: int = x
        self.y: int = y


    #
    def __hash__(self) -> int:
        return hash(f"{self.x}_{self.y}")


    #
    def __repr__(self) -> str:
        #
        return f"ND_Point(x={self.x}, y={self.y})"


    #
    def __eq__(self, other: object) -> bool:
        #
        if not isinstance(other, ND_Point):
            return NotImplemented
        #
        return self.x == other.x and self.y == other.y


    #
    def __add__(self, other: 'ND_Point') -> 'ND_Point':
        #
        return ND_Point(self.x + other.x, self.y + other.y)


    #
    def __sub__(self, other: 'ND_Point') -> 'ND_Point':
        #
        return ND_Point(self.x - other.x, self.y - other.y)


    #
    def __neg__(self) -> 'ND_Point':
        return ND_Point(-self.x, -self.y)


    #
    def distance_to(self, other: 'ND_Point') -> float:
        #
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


    #
    def in_rect(self, rect: 'ND_Rect') -> bool:
        #
        return (rect.left <= self.x < rect.right and
                rect.top <= self.y < rect.bottom)


    #
    def np_normalize(self) -> np.ndarray:
        #
        norm: float = self.x + self.y
        return np.array([self.x / norm, self.y / norm])


    #
    @staticmethod
    def from_tuple(t: tuple[int, int]) -> 'ND_Point':
        #
        return ND_Point(t[0], t[1])


    #
    def to_tuple(self) -> tuple[int, int]:
        #
        return (self.x, self.y)


#
class ND_Rect:
    #
    def __init__(self, x: int, y: int, w: int = 1, h: int = 1) -> None:
        #
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h


    #
    def __hash__(self) -> int:
        return hash(f"{self.x}_{self.y}_{self.w}_{self.h}")


    #
    def __repr__(self) -> str:
        #
        return f"ND_Rect(x={self.x}, y={self.y}, w={self.w}, h={self.h})"


    #
    @property
    def left(self) -> int:
        #
        return self.x


    #
    @property
    def right(self) -> int:
        #
        return self.x + self.w


    #
    @property
    def top(self) -> int:
        #
        return self.y


    #
    @property
    def bottom(self) -> int:
        #
        return self.y + self.h


    #
    def intersects_with_other_rect(self, other: "ND_Rect") -> bool:
        #
        return (self.left < other.right and self.right > other.left and
                self.top < other.bottom and self.bottom > other.top)


    #
    def get_intersection_area_with_other_rect(self, other: "ND_Rect") -> Optional["ND_Rect"]:
        #
        if not self.intersects_with_other_rect(other):
            return None

        #
        x: int = max(self.left, other.left)
        y: int = max(self.top, other.top)
        w: int = min(self.right, other.right) - x
        h: int = min(self.bottom, other.bottom) - y

        #
        return ND_Rect(x, y, w, h)


    #
    def union(self, other: "ND_Rect") -> "ND_Rect":
        #
        x: int = min(self.left, other.left)
        y: int = min(self.top, other.top)
        w: int = max(self.right, other.right) - x
        h: int = max(self.bottom, other.bottom) - y

        #
        return ND_Rect(x, y, w, h)


    #
    @staticmethod
    def enclose_points(points: list[tuple[int, int] | ND_Point]) -> Optional["ND_Rect"]:
        #
        if not points:
            return None

        #
        def get_x(p: tuple[int, int] | ND_Point):
            return p[0] if isinstance(p, tuple) else p.x

        #
        def get_y(p: tuple[int, int] | ND_Point):
            return p[1] if isinstance(p, tuple) else p.y

        #
        x_min: int = get_x(min(points, key=get_x))
        y_min: int = get_y(min(points, key=get_y))
        x_max: int = get_x(max(points, key=get_x))
        y_max: int = get_y(max(points, key=get_y))

        #
        return ND_Rect(x_min, y_min, x_max - x_min, y_max - y_min)


    #
    def contains_point(self, point: ND_Point) -> bool:
        #
        return point.in_rect(self)


#
@dataclass
class ND_Position_Margins:
    """
    if is int, it is pixel value, else if is string, is "value_float%",
    where it indicates the repartition of available empty space between the element to share between his sides.
    """

    margin: Optional[int | str] = None
    margin_left: Optional[int | str] = None
    margin_right: Optional[int | str] = None
    margin_top: Optional[int | str] = None
    margin_bottom: Optional[int | str] = None
    #
    min_margin_left: int = 0
    min_margin_right: int = 0
    min_margin_top: int = 0
    min_margin_bottom: int = 0
    #
    width_stretch_ratio: float = 1.0
    height_stretch_ratio: float = 1.0


#
@dataclass
class ND_Position_Constraints:
    """
    If is int, it is pixel value, else if is string, it is "value_float%" where it indicates the percentage of the containers row or column size.
    If the min and max values are both specified and of the same value, it forces the size to be that value.
    """
    min_width: Optional[int] = None
    max_width: Optional[int] = None
    min_height: Optional[int] = None
    max_height: Optional[int] = None


#
class ND_Position:
    #
    def __init__(self, x: int = 0, y: int = 0, w: int = -1, h: int = -1) -> None:
        """
        With or Height with negative value is like auto width and height.
        In a grid it will take the maximum grid size.
        If a min and max value are specified, and a maximum column/row size are specified to, it will try to adjust to the best while beeing clamped.
        If a min and max value are specified, and no other constraints, it will just sit in the middle of the min and max values.
        """
        #
        self._x: int = x
        self._y: int = y
        self._w: int = w
        self._h: int = h

    #
    @property
    def x(self) -> int:
        #
        return self._x

    #
    @x.setter
    def x(self, value: int) -> None:
        #
        self._x = value

    #
    @property
    def y(self) -> int:
        #
        return self._y

    #
    @y.setter
    def y(self, value: int) -> None:
        #
        self._y = value

    #
    @property
    def w(self) -> int:
        #
        return self._w

    #
    @w.setter
    def w(self, value: int) -> None:
        #
        self._w = value

    #
    @property
    def h(self) -> int:
        #
        return self._h

    #
    @h.setter
    def h(self, value: int) -> None:
        #
        self._h = value

    #
    @property
    def rect(self) -> ND_Rect:
        #
        return ND_Rect(self.x, self.y, self.w, self.h)

    #
    def __repr__(self) -> str:
        return f"Position(x={self.x}, y={self.y}, w={self.w}, h={self.h})"

    #
    def set_x(self, new_x: int) -> None:
        self._x = new_x

    #
    def set_y(self, new_y: int) -> None:
        self._y = new_y

    #
    def set_w(self, new_w: int) -> None:
        self._w = new_w

    #
    def set_h(self, new_h: int) -> None:
        self._h = new_h


# --- Helper Collision Class ---
# This class will contain static methods for various geometric intersection tests
class Collision:
    """
    A helper class containing static methods for performing intersection tests
    between different 3D geometric primitives.
    """

    @staticmethod
    def point_point(p1: 'ND_Point_3D', p2: 'ND_Point_3D') -> bool:
        """Checks if two points are approximately equal."""
        # Uses the __eq__ method which likely already handles float comparison
        return p1 == p2

    @staticmethod
    def point_rect(p: 'ND_Point_3D', r: 'ND_Rect_3D') -> bool:
        """Checks if a point is inside a rectangle (cuboid)."""
        # Delegate to the method implemented in ND_Point_3D
        return p.in_rect_3D(r)

    @staticmethod
    def point_sphere(p: 'ND_Point_3D', s: 'ND_Sphere_3D') -> bool:
        """Checks if a point is inside a sphere."""
        # A point is inside a sphere if its distance to the center <= radius
        return p.distance_to(s.center) <= s.radius + EPSILON # Add epsilon for boundary inclusion

    @staticmethod
    def point_segment(p: 'ND_Point_3D', segment: 'ND_Line_3D') -> bool:
        """Checks if a point lies on a line segment in 3D."""
        # Convert to numpy for vector math
        p_np = p.to_numpy()
        a_np = segment.p1.to_numpy()
        b_np = segment.p2.to_numpy()

        # Vector representing the segment
        segment_vec = b_np - a_np
        # Vector from segment start to point
        point_vec = p_np - a_np

        # Check if the point is collinear with the segment endpoints
        # The cross product of two collinear vectors is the zero vector
        cross_product = np.cross(segment_vec, point_vec)
        if np.linalg.norm(cross_product) > EPSILON:
            return False # Not collinear

        # Check if the point lies within the segment bounds using the dot product
        # The dot product of point_vec and segment_vec divided by segment_vec magnitude squared
        # gives the projection of point_vec onto segment_vec, scaled by segment length.
        # This value (t) should be between 0 and 1 for the point to be on the segment.
        segment_length_sq = np.dot(segment_vec, segment_vec)

        # Handle the case of a zero-length segment (p1 == p2)
        if segment_length_sq < EPSILON:
            return Collision.point_point(p, segment.p1) # Check if point is the same as the endpoint

        t = np.dot(point_vec, segment_vec) / segment_length_sq

        # Check if the projected point is within the segment (0 <= t <= 1)
        # Use epsilon for robust boundary check
        return 0.0 - EPSILON <= t <= 1.0 + EPSILON

    @staticmethod
    def point_triangle(p: 'ND_Point_3D', t: 'ND_Triangle_3D') -> bool:
        """
        Checks if a point lies inside a triangle in 3D.
        Assumes the point is coplanar with the triangle.
        Uses barycentric coordinates.
        """
        p_np = p.to_numpy()
        a_np = t.p1.to_numpy()
        b_np = t.p2.to_numpy()
        c_np = t.p3.to_numpy()

        # Check if the point is coplanar with the triangle first (optional but good practice)
        # This can be done by checking if the vector from one vertex to P
        # is orthogonal to the triangle's normal vector.
        # Or by checking if the scalar triple product of (B-A), (C-A), (P-A) is close to zero.
        v0 = b_np - a_np
        v1 = c_np - a_np
        v2 = p_np - a_np

        # Calculate area of the main triangle and subtriangles using cross product magnitude
        # or dot product and Cramer's rule for barycentric coords.
        # A more robust 3D method checks the point's side relative to each edge plane.
        # Project points to a 2D plane where triangle area is maximized to simplify the check.
        # However, a common method is based on barycentric coordinates directly in 3D using vectors.

        # Calculate dot products for barycentric coordinates
        dot00 = np.dot(v0, v0)
        dot01 = np.dot(v0, v1)
        dot11 = np.dot(v1, v1)
        dot20 = np.dot(v2, v0)
        dot21 = np.dot(v2, v1)

        # Compute denominator
        inv_denom = (dot00 * dot11 - dot01 * dot01)
        if abs(inv_denom) < EPSILON:
            # Degenerate triangle or point very close to edge. Handle cases.
            # If inv_denom is 0, the vectors v0 and v1 are linearly dependent, meaning
            # the triangle is degenerate (a line segment or a point).
            # In a robust implementation, you'd check if the point is on this line segment.
            # For simplicity here, we return False for degenerate triangles unless point is a vertex.
             if Collision.point_point(p, t.p1) or Collision.point_point(p, t.p2) or Collision.point_point(p, t.p3):
                 return True
             return False


        inv_denom = 1 / inv_denom

        # Compute barycentric coordinates
        u = (dot11 * dot20 - dot01 * dot21) * inv_denom
        v = (dot00 * dot21 - dot01 * dot20) * inv_denom

        # Check if point is inside triangle (u >= 0, v >= 0, u + v <= 1)
        # Use epsilon for robust boundary checks
        return (u >= 0.0 - EPSILON) and (v >= 0.0 - EPSILON) and (u + v <= 1.0 + EPSILON)


    # --- Rect Intersections ---
    @staticmethod
    def rect_rect(r1: 'ND_Rect_3D', r2: 'ND_Rect_3D') -> bool:
        """Checks if two rectangles (cuboids) intersect."""
        # Delegate to the method implemented in ND_Rect_3D
        return r1.intersects_with_other_rect_3D(r2)

    @staticmethod
    def rect_sphere(r: 'ND_Rect_3D', s: 'ND_Sphere_3D') -> bool:
        """Checks if a rectangle (cuboid) intersects with a sphere."""
        # Find the closest point on the rectangle to the sphere's center
        center_np = s.center.to_numpy()

        closest_np = np.copy(center_np)
        closest_np[0] = max(r.min_x, min(center_np[0], r.max_x))
        closest_np[1] = max(r.min_y, min(center_np[1], r.max_y))
        closest_np[2] = max(r.min_z, min(center_np[2], r.max_z))

        # Calculate the distance squared from the sphere center to this closest point
        dist_sq = np.sum((center_np - closest_np)**2)

        # Intersection occurs if the distance squared is less than or equal to the radius squared
        return dist_sq <= s.radius**2 + EPSILON


    # --- Sphere Intersections ---
    @staticmethod
    def sphere_sphere(s1: 'ND_Sphere_3D', s2: 'ND_Sphere_3D') -> bool:
        """Checks if two spheres intersect."""
        # Distance between centers
        dist = s1.center.distance_to(s2.center)
        # Sum of radii
        radii_sum = s1.radius + s2.radius
        # Intersection occurs if distance <= sum of radii
        return dist <= radii_sum + EPSILON


    @staticmethod
    def sphere_segment(s: 'ND_Sphere_3D', segment: 'ND_Line_3D') -> bool:
        """Checks if a sphere intersects with a line segment."""
        # Based on algorithm to find closest point on line to point, and check if it's on segment
        # Then check distance. If closest point not on segment, check segment endpoints.

        center_np = s.center.to_numpy()
        a_np = segment.p1.to_numpy()
        b_np = segment.p2.to_numpy()

        # Vector representing the segment
        segment_vec = b_np - a_np

        # If segment is a point
        segment_length_sq = np.dot(segment_vec, segment_vec)
        if segment_length_sq < EPSILON:
            return Collision.point_sphere(segment.p1, s) # Check if the single point intersects the sphere

        # Project sphere center onto the line containing the segment
        # t = dot(Center - A, B - A) / |B - A|^2
        t = np.dot(center_np - a_np, segment_vec) / segment_length_sq

        # Clamp t to the [0, 1] range to find the closest point *on the segment*
        t_clamped = max(0.0, min(1.0, t))

        # Closest point on the segment to the sphere center
        closest_on_segment_np = a_np + t_clamped * segment_vec
        closest_point = ND_Point_3D(*closest_on_segment_np)

        # Distance from sphere center to the closest point on the segment
        dist_to_segment_sq = s.center.distance_to(closest_point)**2

        # Intersection occurs if this distance is <= radius squared
        return dist_to_segment_sq <= s.radius**2 + EPSILON


    # --- Segment Intersections ---
    # Segment-Segment intersection in 3D is complex (parallel, skew, intersecting)
    # Implementing a robust version is non-trivial.
    # Let's implement a basic check for intersection points assuming non-parallel/non-collinear lines
    # and then check if the point is on both segments.

    @staticmethod
    def segment_segment(seg1: 'ND_Line_3D', seg2: 'ND_Line_3D') -> tuple[bool, Optional[Union['ND_Point_3D', tuple['ND_Point_3D', 'ND_Point_3D']]]]:
        """
        Checks for intersection between two line segments in 3D.
        Returns a tuple: (intersects: bool, intersection_point(s): Optional['ND_Point_3D' | tuple['ND_Point_3D', 'ND_Point_3D']]
        Returns True and the intersection point(s) if they intersect.
        Returns False and None otherwise.
        Handles parallel/collinear cases partially.
        """
        p1 = seg1.p1.to_numpy()
        q1 = seg1.p2.to_numpy()
        p2 = seg2.p1.to_numpy()
        q2 = seg2.p2.to_numpy()

        v1 = q1 - p1 # Direction vector for seg1
        v2 = q2 - p2 # Direction vector for seg2
        w0 = p2 - p1 # Vector between starting points

        # Solve for parameters s and t in the equation: P1 + s*v1 = P2 + t*v2
        # s*v1 - t*v2 = w0

        # Using Cramer's rule or vector algebra. A common method for closest points
        # on lines can be adapted. For intersection, the closest points must be the same.

        # Calculate parameters for the closest points on the *infinite* lines
        # These parameters (sc, tc) tell us where the closest points lie on the lines.
        # If the lines intersect, the distance between the closest points is zero,
        # and these parameters correspond to the intersection point on each line.

        dot_v1_v1 = np.dot(v1, v1) # |v1|^2
        dot_v2_v2 = np.dot(v2, v2) # |v2|^2
        dot_v1_v2 = np.dot(v1, v2) # v1 . v2
        dot_w0_v1 = np.dot(w0, v1) # w0 . v1
        dot_w0_v2 = np.dot(w0, v2) # w0 . v2

        # Denominator for the parameter calculation
        denominator = dot_v1_v1 * dot_v2_v2 - dot_v1_v2 * dot_v1_v2

        # Handle parallel or collinear lines
        if abs(denominator) < EPSILON:
            # Lines are parallel or collinear.
            # Check for overlap if collinear. This is complex and depends on projection.
            # For simplicity in this example, we'll treat parallel non-overlapping
            # as no intersection, and require more specific logic for collinear overlap.
            # A basic check for collinear overlap: check if endpoints of one segment
            # lie on the other line, and if the segments overlap on that line.
            # This is beyond the scope of a simple example.
            # Let's just return False for non-collinear parallel and handle collinear cases later if needed.
            # A rough check for collinearity: cross product of v1 and v2 is zero, AND w0 is collinear with v1 (or v2).
            if np.linalg.norm(np.cross(v1, v2)) < EPSILON and np.linalg.norm(np.cross(w0, v1)) < EPSILON:
                 # Assume collinear for now. Need to check for segment overlap.
                 # Project all points onto the line. Check if the 1D intervals overlap.
                 # This requires careful handling of the projection basis.
                 # Leaving this as a TODO for a full implementation.
                 # For this simplified version, we just return False for overlap on collinear lines.
                return False, None # Collinear overlap check is complex TODO
            else:
                 # Parallel but not collinear, no intersection
                 return False, None

        # Calculate parameters s and t for the intersection point on the infinite lines
        s_inf = (dot_w0_v2 * dot_v1_v2 - dot_w0_v1 * dot_v2_v2) / denominator
        t_inf = (dot_w0_v2 * dot_v1_v1 - dot_w0_v1 * dot_v1_v2) / denominator

        # Check if the intersection point lies on both segments (0 <= s <= 1 and 0 <= t <= 1)
        # Use epsilon for robust boundary check
        if (0.0 - EPSILON <= s_inf <= 1.0 + EPSILON) and (0.0 - EPSILON <= t_inf <= 1.0 + EPSILON):
            # Intersection point is on both segments
            intersection_point_np = p1 + s_inf * v1
            intersection_point = ND_Point_3D(*intersection_point_np)
            return True, intersection_point
        else:
            # Intersection point is on the infinite lines, but not on both segments
            return False, None

    # --- Add more intersection methods here as needed (Sphere-Rect, Line-Plane, etc.) ---


# --- ND_Point_3D (Updated with to_numpy) ---
class ND_Point_3D:
    """
    Represents a point in 3D space.
    """
    def __init__(self, x: float = 0, y: float = 0, z: float = 0) -> None:
        self.x: float = float(x)
        self.y: float = float(y)
        self.z: float = float(z)

    def __hash__(self) -> int:
        return hash(f"{self.x}_{self.y}_{self.z}")

    def __repr__(self) -> str:
        return f"ND_Point_3D(x={self.x}, y={self.y}, z={self.z})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ND_Point_3D):
            return NotImplemented
        # Using epsilon for robust floating point comparison
        return (abs(self.x - other.x) < EPSILON and
                abs(self.y - other.y) < EPSILON and
                abs(self.z - other.z) < EPSILON)

    def __add__(self, other: 'ND_Point_3D') -> 'ND_Point_3D':
        return ND_Point_3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'ND_Point_3D') -> 'ND_Point_3D':
        return ND_Point_3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self) -> 'ND_Point_3D':
        return ND_Point_3D(-self.x, -self.y, -self.z)

    def distance_to(self, other: 'ND_Point_3D') -> float:
        """
        Calculates the Euclidean distance between this point and another point.
        """
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return sqrt(dx**2 + dy**2 + dz**2)

    def in_rect_3D(self, rect: 'ND_Rect_3D') -> bool:
        """
        Checks if the point is inside a 3D rectangle (inclusive of boundaries).
        """
        return Collision.point_rect(self, rect) # Delegate to Collision helper

    def np_normalize(self) -> np.ndarray:
        """
        Normalizes the 3D point vector to a unit vector using NumPy.
        Returns a NumPy array representing the normalized vector.
        Returns a zero vector if the magnitude is zero.
        """
        vec = np.array([self.x, self.y, self.z])
        magnitude = np.linalg.norm(vec)
        if magnitude < EPSILON: # Use epsilon for zero check
            return np.array([0.0, 0.0, 0.0])
        else:
            return vec / magnitude

    @staticmethod
    def from_tuple(t: tuple[float, float, float]) -> 'ND_Point_3D':
        """
        Creates a ND_Point_3D instance from a 3-element tuple.
        """
        if len(t) != 3:
            raise ValueError("Input tuple must contain exactly 3 elements for a 3D point.")
        return ND_Point_3D(t[0], t[1], t[2])

    def to_tuple(self) -> tuple[float, float, float]:
        """
        Converts the ND_Point_3D instance to a 3-element tuple.
        """
        return (self.x, self.y, self.z)

    def to_numpy(self) -> np.ndarray:
        """
        Converts the ND_Point_3D instance to a NumPy array.
        """
        return np.array([self.x, self.y, self.z])

    # --- Intersection Methods for Point ---
    def intersects_with(self, other: object) -> bool:
        """Checks for intersection with another 3D geometric object."""
        if isinstance(other, ND_Point_3D):
            return Collision.point_point(self, other)
        elif isinstance(other, ND_Rect_3D):
            return Collision.point_rect(self, other)
        elif isinstance(other, ND_Sphere_3D):
            return Collision.point_sphere(self, other)
        elif isinstance(other, ND_Line_3D):
             # Point-Line (Segment) intersection
             return Collision.point_segment(self, other)
        elif isinstance(other, ND_Circle_3D):
             # Point-Circle intersection (complex, needs plane check) - TODO
             print("Warning: Point-Circle intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Triangle_3D):
             # Point-Triangle intersection
             return Collision.point_triangle(self, other)
        elif isinstance(other, ND_Polygon_3D):
             # Point-Polygon intersection (complex, needs plane check and point-in-polygon) - TODO
             print("Warning: Point-Polygon intersection check is not fully implemented.")
             return False # Not implemented
        else:
            # Add checks for other types as they are implemented
            print(f"Warning: Intersection check between Point_3D and {type(other).__name__} is not implemented.")
            return False


# --- ND_Rect_3D (Updated with intersects_with and using Collision helper) ---
class ND_Rect_3D:
    """
    Represents a 3D axis-aligned rectangle (cuboid) defined by two opposite corners.
    """
    def __init__(self, corner1: ND_Point_3D, corner2: ND_Point_3D) -> None:
        self.corner1: ND_Point_3D = corner1
        self.corner2: ND_Point_3D = corner2

    @property
    def min_x(self) -> float:
        return min(self.corner1.x, self.corner2.x)

    @property
    def max_x(self) -> float:
        return max(self.corner1.x, self.corner2.x)

    @property
    def min_y(self) -> float:
        return min(self.corner1.y, self.corner2.y)

    @property
    def max_y(self) -> float:
        return max(self.corner1.y, self.corner2.y)

    @property
    def min_z(self) -> float:
        return min(self.corner1.z, self.corner2.z)

    @property
    def max_z(self) -> float:
        return max(self.corner1.z, self.corner2.z)

    # Helper property for min corner (canonical representation)
    @property
    def min_corner(self) -> ND_Point_3D:
        return ND_Point_3D(self.min_x, self.min_y, self.min_z)

     # Helper property for max corner (canonical representation)
    @property
    def max_corner(self) -> ND_Point_3D:
        return ND_Point_3D(self.max_x, self.max_y, self.max_z)

    def __hash__(self) -> int:
        # Hash based on canonical min/max corners for consistency
        return hash((self.min_corner, self.max_corner))

    def __repr__(self) -> str:
        return f"ND_Rect_3D(corner1={self.corner1}, corner2={self.corner2})" # Keep original repr format

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ND_Rect_3D):
            return NotImplemented
        # Compare using canonical min/max corners with epsilon for robustness
        return (abs(self.min_x - other.min_x) < EPSILON and abs(self.max_x - other.max_x) < EPSILON and
                abs(self.min_y - other.min_y) < EPSILON and abs(self.max_y - other.max_y) < EPSILON and
                abs(self.min_z - other.min_z) < EPSILON and abs(self.max_z - other.max_z) < EPSILON)


    def intersects_with_other_rect_3D(self, other: "ND_Rect_3D") -> bool:
         """
         Checks if this rectangle intersects with another 3D rectangle.
         Returns True if they intersect, False otherwise.
         """
         # Delegate to Collision helper
         return Collision.rect_rect(self, other)


    def get_intersection_area_with_other_rect(self, other: "ND_Rect_3D") -> Optional["ND_Rect_3D"]:
        """
        Returns a new ND_Rect_3D representing the intersection of this rectangle
        with another rectangle. Returns None if they do not intersect.
        """
        # Delegate intersection logic to Collision helper, although the helper
        # currently only does boolean check. We'll keep the return type here.
        # Recalculate intersection logic directly as it returns geometry.
        if not self.intersects_with_other_rect_3D(other):
            return None

        intersect_min_x = max(self.min_x, other.min_x)
        intersect_min_y = max(self.min_y, other.min_y)
        intersect_min_z = max(self.min_z, other.min_z)

        intersect_max_x = min(self.max_x, other.max_x)
        intersect_max_y = min(self.max_y, other.max_y)
        intersect_max_z = min(self.max_z, other.max_z)

        # This check is important: if the intersection is valid, min should be <= max
        # Due to intersects_with_other_rect_3D, this should hold if the intersection exists,
        # but numerical precision might require epsilon checks here too if needed.
        if intersect_min_x > intersect_max_x + EPSILON or \
           intersect_min_y > intersect_max_y + EPSILON or \
           intersect_min_z > intersect_max_z + EPSILON:
             # Should not happen if intersects_with_other_rect_3D is true and logic is correct
             return None # No valid intersection rectangle

        return ND_Rect_3D(
            ND_Point_3D(intersect_min_x, intersect_min_y, intersect_min_z),
            ND_Point_3D(intersect_max_x, intersect_max_y, intersect_max_z)
        )


    def union(self, other: "ND_Rect_3D") -> "ND_Rect_3D":
        """
        Returns a new ND_Rect_3D representing the smallest rectangle that
        encloses both this rectangle and another rectangle.
        """
        union_min_x = min(self.min_x, other.min_x)
        union_min_y = min(self.min_y, other.min_y)
        union_min_z = min(self.min_z, other.min_z)

        union_max_x = max(self.max_x, other.max_x)
        union_max_y = max(self.max_y, other.max_y)
        union_max_z = max(self.max_z, other.max_z)

        return ND_Rect_3D(
            ND_Point_3D(union_min_x, union_min_y, union_min_z),
            ND_Point_3D(union_max_x, union_max_y, union_max_z)
        )


    @staticmethod
    def enclose_points(points: list[ND_Point_3D]) -> Optional["ND_Rect_3D"]:
        """
        Creates the smallest possible 3D rectangle that encloses all given points.
        Returns None if the list of points is empty.
        """
        if not points:
            return None

        min_x = points[0].x
        max_x = points[0].x
        min_y = points[0].y
        max_y = points[0].y
        min_z = points[0].z
        max_z = points[0].z

        for point in points[1:]:
            min_x = min(min_x, point.x)
            max_x = max(max_x, point.x)
            min_y = min(min_y, point.y)
            max_y = max(max_y, point.y)
            min_z = min(min_z, point.z)
            max_z = max(max_z, point.z)

        return ND_Rect_3D(
            ND_Point_3D(min_x, min_y, min_z),
            ND_Point_3D(max_x, max_y, max_z)
        )

    def contains_point(self, point: ND_Point_3D) -> bool:
        """
        Checks if a given point is contained within this rectangle.
        This method delegates the check to the Collision helper.
        """
        return Collision.point_rect(point, self)

    # --- Intersection Methods for Rect ---
    def intersects_with(self, other: object) -> bool:
        """Checks for intersection with another 3D geometric object."""
        if isinstance(other, ND_Point_3D):
             # Rect-Point is the same as Point-Rect
             return Collision.point_rect(other, self)
        elif isinstance(other, ND_Rect_3D):
             return Collision.rect_rect(self, other)
        elif isinstance(other, ND_Sphere_3D):
             return Collision.rect_sphere(self, other)
        elif isinstance(other, ND_Line_3D):
             # Rect-Line (Segment) intersection (complex) - TODO
             print("Warning: Rect-Line (Segment) intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Circle_3D):
             # Rect-Circle intersection (very complex) - TODO
             print("Warning: Rect-Circle intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Triangle_3D):
             # Rect-Triangle intersection (very complex) - TODO
             print("Warning: Rect-Triangle intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Polygon_3D):
             # Rect-Polygon intersection (very complex) - TODO
             print("Warning: Rect-Polygon intersection check is not fully implemented.")
             return False # Not implemented
        else:
            print(f"Warning: Intersection check between Rect_3D and {type(other).__name__} is not implemented.")
            return False


# --- ND_Sphere_3D ---
class ND_Sphere_3D:
    """
    Represents a sphere in 3D space.
    """
    def __init__(self, center: ND_Point_3D, radius: float) -> None:
        if radius < 0:
            raise ValueError("Sphere radius cannot be negative.")
        self.center: ND_Point_3D = center
        self.radius: float = float(radius)

    def __hash__(self) -> int:
        return hash((self.center, self.radius))

    def __repr__(self) -> str:
        return f"ND_Sphere_3D(center={self.center}, radius={self.radius})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ND_Sphere_3D):
            return NotImplemented
        # Compare center and radius with epsilon for robustness
        return self.center == other.center and abs(self.radius - other.radius) < EPSILON

    # --- Intersection Methods for Sphere ---
    def intersects_with(self, other: object) -> bool:
        """Checks for intersection with another 3D geometric object."""
        if isinstance(other, ND_Point_3D):
            # Sphere-Point is the same as Point-Sphere
            return Collision.point_sphere(other, self)
        elif isinstance(other, ND_Rect_3D):
            # Sphere-Rect is the same as Rect-Sphere
            return Collision.rect_sphere(other, self)
        elif isinstance(other, ND_Sphere_3D):
            return Collision.sphere_sphere(self, other)
        elif isinstance(other, ND_Line_3D):
             # Sphere-Line (Segment) intersection
             return Collision.sphere_segment(self, other)
        elif isinstance(other, ND_Circle_3D):
             # Sphere-Circle intersection (complex) - TODO
             print("Warning: Sphere-Circle intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Triangle_3D):
             # Sphere-Triangle intersection (complex) - TODO
             print("Warning: Sphere-Triangle intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Polygon_3D):
             # Sphere-Polygon intersection (very complex) - TODO
             print("Warning: Sphere-Polygon intersection check is not fully implemented.")
             return False # Not implemented
        else:
            print(f"Warning: Intersection check between Sphere_3D and {type(other).__name__} is not implemented.")
            return False


# --- ND_Line_3D (Represents a Segment) ---
class ND_Line_3D:
    """
    Represents a line segment in 3D space defined by two endpoints.
    """
    def __init__(self, p1: ND_Point_3D, p2: ND_Point_3D) -> None:
        self.p1: ND_Point_3D = p1
        self.p2: ND_Point_3D = p2

    def __hash__(self) -> int:
         # Hash based on sorted points to handle (A, B) vs (B, A) segments
         # Using tuples of coordinates for hashing points consistently
         return hash(tuple(sorted((self.p1.to_tuple(), self.p2.to_tuple()))))

    def __repr__(self) -> str:
        return f"ND_Line_3D(p1={self.p1}, p2={self.p2})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ND_Line_3D):
            return NotImplemented
        # Segments are equal if their endpoints are the same, regardless of order
        return (self.p1 == other.p1 and self.p2 == other.p2) or \
               (self.p1 == other.p2 and self.p2 == other.p1)

    # --- Intersection Methods for Line (Segment) ---
    def intersects_with(self, other: object) -> bool:
        """Checks for intersection with another 3D geometric object."""
        if isinstance(other, ND_Point_3D):
             # Line-Point (Segment-Point) is the same as Point-Segment
             return Collision.point_segment(other, self)
        elif isinstance(other, ND_Rect_3D):
             # Line-Rect (Segment-Rect) is the same as Rect-Line - TODO
             print("Warning: Line-Rect (Segment-Rect) intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Sphere_3D):
             # Line-Sphere (Segment-Sphere) is the same as Sphere-Segment
             return Collision.sphere_segment(other, self)
        elif isinstance(other, ND_Line_3D):
             # Line-Line (Segment-Segment) intersection (returns bool, doesn't get point)
             intersects, _ = Collision.segment_segment(self, other)
             return intersects
        elif isinstance(other, ND_Circle_3D):
             # Line-Circle (Segment-Circle) intersection (complex) - TODO
             print("Warning: Line-Circle (Segment-Circle) intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Triangle_3D):
             # Line-Triangle (Segment-Triangle) intersection (complex) - TODO
             print("Warning: Line-Triangle (Segment-Triangle) intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Polygon_3D):
             # Line-Polygon (Segment-Polygon) intersection (very complex) - TODO
             print("Warning: Line-Polygon (Segment-Polygon) intersection check is not fully implemented.")
             return False # Not implemented
        else:
            print(f"Warning: Intersection check between Line_3D and {type(other).__name__} is not implemented.")
            return False


# --- ND_Circle_3D ---
class ND_Circle_3D:
    """
    Represents a circle in 3D space.
    Requires a center, radius, and a normal vector defining its plane.
    """
    def __init__(self, center: ND_Point_3D, radius: float, normal: ND_Point_3D) -> None:
        if radius < 0:
            raise ValueError("Circle radius cannot be negative.")
        # Ensure normal is non-zero and normalized
        normal_np = normal.to_numpy()
        normal_magnitude = np.linalg.norm(normal_np)
        if normal_magnitude < EPSILON:
            raise ValueError("Circle normal vector cannot be a zero vector.")

        self.center: ND_Point_3D = center
        self.radius: float = float(radius)
        # Store the normal as a normalized NumPy array
        self.normal: np.ndarray = normal_np / normal_magnitude

    def __hash__(self) -> int:
        # Hashing involves the center, radius, and normal (as a tuple for consistency)
        # Convert normal numpy array to tuple for hashing
        return hash((self.center, self.radius, tuple(self.normal)))

    def __repr__(self) -> str:
        # Represent normal as a Point_3D for readability, even though stored as numpy
        normal_point = ND_Point_3D(*self.normal)
        return f"ND_Circle_3D(center={self.center}, radius={self.radius}, normal={normal_point})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ND_Circle_3D):
            return NotImplemented
        # Compare center, radius, and normal (with epsilon)
        # Compare normal vectors allowing for opposite direction (normal or -normal)
        return bool( self.center == other.center and abs(self.radius - other.radius) < EPSILON and (np.linalg.norm(self.normal - other.normal) < EPSILON or np.linalg.norm(self.normal + other.normal) < EPSILON) ) # Allow opposing normals


    # --- Intersection Methods for Circle ---
    def intersects_with(self, other: object) -> bool:
        """Checks for intersection with another 3D geometric object."""
        if isinstance(other, ND_Point_3D):
             # Circle-Point intersection (complex, needs plane check) - TODO
             print("Warning: Circle-Point intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Rect_3D):
             # Circle-Rect intersection (very complex) - TODO
             print("Warning: Circle-Rect intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Sphere_3D):
             # Circle-Sphere intersection (complex) - TODO
             print("Warning: Circle-Sphere intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Line_3D):
             # Circle-Line (Segment) intersection (complex) - TODO
             print("Warning: Circle-Line (Segment) intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Circle_3D):
             # Circle-Circle intersection (very complex) - TODO
             print("Warning: Circle-Circle intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Triangle_3D):
             # Circle-Triangle intersection (very complex) - TODO
             print("Warning: Circle-Triangle intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Polygon_3D):
             # Circle-Polygon intersection (extremely complex) - TODO
             print("Warning: Circle-Polygon intersection check is not fully implemented.")
             return False # Not implemented
        else:
            print(f"Warning: Intersection check between Circle_3D and {type(other).__name__} is not implemented.")
            return False


# --- ND_Triangle_3D ---
class ND_Triangle_3D:
    """
    Represents a triangle in 3D space defined by three vertices.
    Assumed to be non-degenerate (not collinear).
    """
    def __init__(self, p1: ND_Point_3D, p2: ND_Point_3D, p3: ND_Point_3D) -> None:
        # Basic check for degeneracy (collinearity) - cross product of two edges should be non-zero
        v1 = (p2 - p1).to_numpy()
        v2 = (p3 - p1).to_numpy()
        if np.linalg.norm(np.cross(v1, v2)) < EPSILON:
             print("Warning: Degenerate triangle (collinear vertices). Intersection tests may be unreliable.")
        self.p1: ND_Point_3D = p1
        self.p2: ND_Point_3D = p2
        self.p3: ND_Point_3D = p3

    def __hash__(self) -> int:
        # Hash based on sorted vertices to handle different vertex orders
        return hash(tuple(sorted((self.p1.to_tuple(), self.p2.to_tuple(), self.p3.to_tuple()))))

    def __repr__(self) -> str:
        return f"ND_Triangle_3D(p1={self.p1}, p2={self.p2}, p3={self.p3})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ND_Triangle_3D):
            return NotImplemented
        # Triangles are equal if they have the same set of vertices
        # Convert vertices to tuples and compare as sets
        self_vertices = {self.p1.to_tuple(), self.p2.to_tuple(), self.p3.to_tuple()}
        other_vertices = {other.p1.to_tuple(), other.p2.to_tuple(), other.p3.to_tuple()}
        return self_vertices == other_vertices


    # --- Intersection Methods for Triangle ---
    def intersects_with(self, other: object) -> bool:
        """Checks for intersection with another 3D geometric object."""
        if isinstance(other, ND_Point_3D):
             # Triangle-Point is the same as Point-Triangle
             return Collision.point_triangle(other, self)
        elif isinstance(other, ND_Rect_3D):
             # Triangle-Rect intersection (very complex) - TODO
             print("Warning: Triangle-Rect intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Sphere_3D):
             # Triangle-Sphere intersection (complex) - TODO
             print("Warning: Triangle-Sphere intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Line_3D):
             # Triangle-Line (Segment) intersection (complex) - TODO
             print("Warning: Triangle-Line (Segment) intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Circle_3D):
             # Triangle-Circle intersection (very complex) - TODO
             print("Warning: Triangle-Circle intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Triangle_3D):
             # Triangle-Triangle intersection (very complex) - TODO
             print("Warning: Triangle-Triangle intersection check is not fully implemented.")
             return False # Not implemented
        elif isinstance(other, ND_Polygon_3D):
             # Triangle-Polygon intersection (extremely complex) - TODO
             print("Warning: Triangle-Polygon intersection check is not fully implemented.")
             return False # Not implemented
        else:
            print(f"Warning: Intersection check between Triangle_3D and {type(other).__name__} is not implemented.")
            return False


# --- ND_Polygon_3D ---
class ND_Polygon_3D:
    """
    Represents a planar polygon in 3D space defined by a list of vertices.
    Assumed to be coplanar and vertices are ordered (e.g., winding order defines normal).
    Intersection with other primitives is generally complex.
    """
    def __init__(self, vertices: list[ND_Point_3D]) -> None:
        if len(vertices) < 3:
            raise ValueError("A polygon must have at least 3 vertices.")
        # TODO: Add check for coplanarity and calculate normal.
        # TODO: Add check for simple polygon (non-self-intersecting)
        self.vertices: list[ND_Point_3D] = vertices
        self.normal: Optional[np.ndarray] = None # Store calculated normal (TODO)
        # Calculate normal if possible (requires coplanarity check)
        if len(vertices) >= 3:
             try:
                 # Get two vectors along edges from the first vertex
                 v1 = (vertices[1] - vertices[0]).to_numpy()
                 v2 = (vertices[2] - vertices[0]).to_numpy()
                 cross_prod = np.cross(v1, v2)
                 magnitude = np.linalg.norm(cross_prod)
                 if magnitude > EPSILON:
                     self.normal = cross_prod / magnitude
                 else:
                     # Degenerate polygon (vertices collinear)
                     self.normal = None
                     print("Warning: Polygon vertices are collinear or degenerate.")
                 # TODO: For non-convex polygons, the normal calculation is more complex.
                 # This simple method assumes the first three vertices define the plane.
             except Exception as e:
                 print(f"Warning: Could not calculate polygon normal: {e}")
                 self.normal = None


    def __hash__(self) -> int:
        # Hashing a polygon is tricky. Order of vertices in the list matters for this hash,
        # but geometric equality shouldn't depend on starting vertex or winding order.
        # A robust hash would canonicalize the representation (e.g., sort vertices by some criteria,
        # possibly store two hashes for both winding orders if convex).
        # For simplicity here, we hash based on the tuple of vertex hashes in order.
        return hash(tuple(v.to_tuple() for v in self.vertices))


    def __repr__(self) -> str:
        return f"ND_Polygon_3D(vertices={self.vertices})"


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ND_Polygon_3D):
            return NotImplemented
        # Checking polygon equality is complex (same vertices, same order or reverse order if simple, coplanar)
        # A simple check here is just if the vertex lists are identical (order matters).
        # A more robust check would compare sets of vertices and check coplanarity/ordering.
        if len(self.vertices) != len(other.vertices):
             return False

        # Check if the lists of vertices are the same (order matters)
        # For geometric equality, one would need to check for cyclic permutations
        # and reverse order permutations.
        return self.vertices == other.vertices


    # --- Intersection Methods for Polygon ---
    def intersects_with(self, other: object) -> bool:
        """Checks for intersection with another 3D geometric object."""
        # Intersection tests for general polygons are highly complex.
        # Often involves clipping algorithms (e.g., Sutherland-Hodgman in 3D),
        # plane-intersection tests, and point-in-polygon tests on the plane.
        print(f"Warning: Intersection checks involving Polygon_3D ({type(other).__name__}) are not fully implemented.")

        # Add checks for implemented intersections if any (e.g., Point-Polygon requires plane check)
        if isinstance(other, ND_Point_3D):
             # Point-Polygon intersection (needs coplanarity and 2D point-in-polygon) - TODO
             return False # Not implemented
        # Add other types as implemented

        return False # Not implemented


# --- Example Usage (Optional - for testing) ---
if __name__ == "__main__":
    # Create some points
    p1 = ND_Point_3D(0, 0, 0)
    p2 = ND_Point_3D(1, 1, 1)
    p3 = ND_Point_3D(0.5, 0.5, 0.5)
    p4 = ND_Point_3D(10, 10, 10)

    print(f"{p1} equals {p2}: {p1 == p2}")
    print(f"{p1} equals {p3}: {p1 == p3}")
    print(f"Distance between {p1} and {p2}: {p1.distance_to(p2)}")

    # Create some rectangles
    rect1 = ND_Rect_3D(ND_Point_3D(0, 0, 0), ND_Point_3D(2, 2, 2))
    rect2 = ND_Rect_3D(ND_Point_3D(1, 1, 1), ND_Point_3D(3, 3, 3))
    rect3 = ND_Rect_3D(ND_Point_3D(5, 5, 5), ND_Point_3D(6, 6, 6))

    print(f"\n{rect1} intersects {rect2}: {rect1.intersects_with(rect2)}")
    print(f"{rect1} intersects {rect3}: {rect1.intersects_with(rect3)}")

    intersection_rect = rect1.get_intersection_area_with_other_rect(rect2)
    print(f"Intersection of {rect1} and {rect2}: {intersection_rect}")

    union_rect = rect1.union(rect2)
    print(f"Union of {rect1} and {rect2}: {union_rect}")

    print(f"Is {p3} in {rect1}: {p3.intersects_with(rect1)}")
    print(f"Is {p4} in {rect1}: {p4.intersects_with(rect1)}")

    # Create some spheres
    sphere1 = ND_Sphere_3D(ND_Point_3D(0, 0, 0), 1.5)
    sphere2 = ND_Sphere_3D(ND_Point_3D(2, 0, 0), 1.0)
    sphere3 = ND_Sphere_3D(ND_Point_3D(5, 5, 5), 1.0)

    print(f"\n{sphere1} intersects {sphere2}: {sphere1.intersects_with(sphere2)}")
    print(f"{sphere1} intersects {sphere3}: {sphere1.intersects_with(sphere3)}")
    print(f"{rect1} intersects {sphere1}: {rect1.intersects_with(sphere1)}")
    print(f"{rect3} intersects {sphere1}: {rect3.intersects_with(sphere1)}")
    print(f"Is {p3} in {sphere1}: {p3.intersects_with(sphere1)}")
    print(f"Is {p4} in {sphere1}: {p4.intersects_with(sphere1)}")


    # Create some segments (Lines)
    line1 = ND_Line_3D(ND_Point_3D(0, 0, 0), ND_Point_3D(2, 2, 2))
    line2 = ND_Line_3D(ND_Point_3D(0, 2, 0), ND_Point_3D(2, 0, 2)) # Intersects line1
    line3 = ND_Line_3D(ND_Point_3D(10, 10, 10), ND_Point_3D(11, 11, 11)) # Does not intersect line1

    print(f"\n{line1} intersects {line2}: {line1.intersects_with(line2)}")
    print(f"{line1} intersects {line3}: {line1.intersects_with(line3)}")
    print(f"{sphere1} intersects {line1}: {sphere1.intersects_with(line1)}")
    print(f"{sphere3} intersects {line1}: {sphere3.intersects_with(line1)}")
    print(f"Is {p3} on {line1}: {p3.intersects_with(line1)}")
    print(f"Is {p4} on {line1}: {p4.intersects_with(line1)}")


    # Create a triangle
    triangle1 = ND_Triangle_3D(ND_Point_3D(0, 0, 0), ND_Point_3D(1, 0, 0), ND_Point_3D(0, 1, 0))
    point_on_triangle = ND_Point_3D(0.3, 0.3, 0) # Should be inside
    point_outside_triangle = ND_Point_3D(0.7, 0.7, 0) # Should be outside
    point_off_plane = ND_Point_3D(0.3, 0.3, 1) # Not coplanar

    print(f"\nIs {point_on_triangle} in {triangle1}: {point_on_triangle.intersects_with(triangle1)}")
    print(f"Is {point_outside_triangle} in {triangle1}: {point_outside_triangle.intersects_with(triangle1)}")
    # Note: Point-Triangle check implemented here assumes coplanarity.
    # A robust check needs to confirm coplanarity first. The current implementation might
    # return true for points off-plane that project inside.
    print(f"Is {point_off_plane} in {triangle1}: {point_off_plane.intersects_with(triangle1)}") # Might give unexpected results if off-plane

    # Create a circle
    circle1 = ND_Circle_3D(ND_Point_3D(0, 0, 0), 1.0, ND_Point_3D(0, 0, 1))
    print(f"\n{circle1}")

    # Create a polygon
    polygon1 = ND_Polygon_3D([ND_Point_3D(0, 0, 0), ND_Point_3D(1, 0, 0), ND_Point_3D(1, 1, 0), ND_Point_3D(0, 1, 0)])
    print(f"\n{polygon1}")
    if polygon1.normal is not None:
        print(f"Polygon Normal: {ND_Point_3D(*polygon1.normal)}") # Convert numpy back for display

    # Demonstrate intersection dispatching
    print(f"\nDoes {p1} intersect {sphere1}: {p1.intersects_with(sphere1)}")
    print(f"Does {rect1} intersect {sphere1}: {rect1.intersects_with(sphere1)}")
    print(f"Does {sphere1} intersect {rect1}: {sphere1.intersects_with(rect1)}") # Should call the same underlying logic
    print(f"Does {line1} intersect {sphere1}: {line1.intersects_with(sphere1)}")
    print(f"Does {triangle1} intersect {p1}: {triangle1.intersects_with(p1)}")
