# Abstract attributes and methods list for ND_Window class

```py
#
class ND_Window:

    #
    ### Attributes: ###
    #

        #
        self.window_id: int
        self.display: ND_Display
        self.main_app: ND_MainApp

        #
        ## Global Window Position in Global Desktop Space. ##
        #
        self.x: int
        self.y: int
        self.width: int
        self.height: int
        self.rect: ND_Rect

        #
        self.sdl_or_glfw_window_id: int
        #
        self.display_states: dict[str, Optional[Callable[[], None]]]
        self.state: Optional[str]

        #
        self.clip_rect_stack: list[ND_Rect]

        #
        self.scenes: dict[str, ND_Scene]

        #
        self.next_texture_id: int

        #
        ## Styles management. ##
        #
        self.styles: dict[str, ND_Style]
        #
        self._default_style: str

    #
    ### Methods: ###
    #

    #
    def get_style_attribute(self, style_name: str, attribute_name: str, elt_state: str = "normal", styles_override: Optional[dict[str, Any]] = None) -> Optional[Any]

    #
    def get_default_style(self) -> ND_Style

    #
    def set_default_style(self, new_style: ND_Style) -> None

    #
    def get_style(self, style_name: str) -> ND_Style

    #
    def add_style(self, style_name: str, new_style: ND_Style) -> None

    #
    def push_to_clip_rect_stack(self, x: int, y: int, w: int, h: int) -> None

    #
    def get_top_of_clip_rect_stack(self) -> Optional[ND_Rect]

    #
    def remove_top_of_clip_rect_stack(self) -> None

    #
    def destroy_window(self) -> None

    #
    def set_title(self, new_title: str) -> None

    #
    def set_position(self, new_x: int, new_y: int) -> None

    #
    def update_position(self, new_x: int, new_y: int) -> None

    #
    def update_size(self, new_w: int, new_h: int) -> None

    #
    def set_fullscreen(self, mode: int) -> None

    #
    def set_size(self, new_width: int, new_height: int) -> None

    #
    def add_scene(self, scene: "ND_Scene") -> None

    #
    def update_scene_sizes(self) -> None

    #
    def set_state(self, state: str) -> None

    #
    def is_hovered_by_mouse(self) -> bool

    #
    def blit_texture(self, texture: Any, dst_rect: ND_Rect) -> None

    #
    def prepare_text_to_render(self, text: str, color: ND_Color, font_size: int, font_name: Optional[str] = None) -> int

    #
    def prepare_image_to_render(self, img_path: str) -> int

    #
    def render_prepared_texture(self, texture_id: int, x: int, y: int, width: int, height: int, transformations: ND_Transformation = ND_Transformation()) -> None

    #
    def render_part_of_prepared_texture(self, texture_id: int, x: int, y: int, w: int, h: int, src_x: int, src_y: int, src_w: int, src_h: int, transformations: ND_Transformation = ND_Transformation()) -> None

    #
    def get_prepared_texture_size(self, texture_id: int) -> ND_Point

    #
    def destroy_prepared_texture(self, texture_id: int) -> None

    #
    def draw_text(self, txt: str, x: int, y: int, font_size: int, font_color: ND_Color, font_name: Optional[str] = None) -> None

    #
    def get_text_size_with_font(self, txt: str, font_size: int, font_name: Optional[str] = None) -> ND_Point

    #
    def get_count_of_renderable_chars_fitting_given_width(self, txt: str, given_width: int, font_size: int, font_name: Optional[str] = None) -> tuple[int, int]

    #
    def draw_pixel(self, x: int, y: int, color: ND_Color) -> None

    #
    def draw_hline(self, x1: int, x2: int, y: int, color: ND_Color) -> None

    #
    def draw_vline(self, x: int, y1: int, y2: int, color: ND_Color) -> None

    #
    def draw_line(self, x1: int, x2: int, y1: int, y2: int, color: ND_Color) -> None

    #
    def draw_thick_line(self, x1: int, x2: int, y1: int, y2: int, line_thickness: int, color: ND_Color) -> None

    #
    def draw_rounded_rect(self, x: int, y: int, width: int, height: int, radius: int, fill_color: ND_Color, border_color: ND_Color, border_size: int = 1) -> None

    #
    def draw_unfilled_rect(self, x: int, y: int, width: int, height: int, outline_color: ND_Color) -> None

    #
    def draw_filled_rect(self, x: int, y: int, width: int, height: int, fill_color: ND_Color) -> None

    #
    def draw_unfilled_circle(self, x: int, y: int, radius: int, outline_color: ND_Color) -> None

    #
    def draw_filled_circle(self, x: int, y: int, radius: int, fill_color: ND_Color) -> None

    #
    def draw_unfilled_ellipse(self, x: int, y: int, rx: int, ry: int, outline_color: ND_Color) -> None

    #
    def draw_filled_ellipse(self, x: int, y: int, rx: int, ry: int, fill_color: ND_Color) -> None

    #
    def draw_arc(self, x: int, y: int, radius: float, angle_start: float, angle_end: float, color: ND_Color) -> None

    #
    def draw_unfilled_pie(self, x: int, y: int, radius: float, angle_start: float, angle_end: float, outline_color: ND_Color) -> None

    #
    def draw_filled_pie(self, x: int, y: int, radius: float, angle_start: float, angle_end: float, fill_color: ND_Color) -> None

    #
    def draw_unfilled_triangle(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, outline_color: ND_Color) -> None

    #
    def draw_filled_triangle(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, fill_color: ND_Color) -> None

    #
    def draw_unfilled_polygon(self, x_coords: list[int], y_coords: list[int], outline_color: ND_Color) -> None

    #
    def draw_filled_polygon(self, x_coords: list[int], y_coords: list[int], fill_color: ND_Color) -> None

    #
    def draw_textured_triangle(self, x_triangle_coords: tuple[int, int, int], y_triangle_coords: tuple[int, int, int], texture_id: int, x_texture_wrap_coords: tuple[int, int, int], y_texture_wrap_coords: tuple[int, int, int]) -> None

    #
    def draw_textured_polygon(self, x_coords: list[int], y_coords: list[int], texture_id: int, texture_dx: int = 0, texture_dy: int = 0) -> None

    #
    def draw_bezier_curve(self, x_coords: list[int], y_coords: list[int], outline_color: ND_Color, nb_interpolations: int = 3) -> None

    #
    def enable_area_drawing_constraints(self, x: int, y: int, width: int, height: int) -> None

    #
    def disable_area_drawing_constraints(self) -> None

    #
    def update_display(self) -> None
```
