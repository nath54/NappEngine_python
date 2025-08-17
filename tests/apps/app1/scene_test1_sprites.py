
from lib_nadisplay_point import ND_Point
from lib_nadisplay_core import ND_EventsHandler_Elts

import lib_nadisplay as nd

#
grid_camera: nd.ND_Elt_CameraGrid
window: nd.ND_Window


#
def create_test1_scene(win: nd.ND_Window) -> None:
    global grid_camera, window

    #
    window = win

    #
    ###
    #
    test_scene_id: str = "test1_sprites"

    #
    ### Useful margin center item ! ###
    #
    margin_center: nd.ND_Position_Margins = nd.ND_Position_Margins(
        margin_left="50%", margin_right="50%", margin_top="50%", margin_bottom="50%",
        min_margin_bottom=10, min_margin_top=10, min_margin_left=10, min_margin_right=10
    )

    #
    ### Test menu scene. ###
    #
    tests_scene: nd.ND_Scene = nd.ND_Scene(
        window=win,
        scene_id=test_scene_id,
        origin=ND_Point(0, 0),
        elements_layers = {},
        on_window_state=test_scene_id
    )

    #
    ### Main Scene Container. ###
    #
    test_container: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="test_container",
        position=nd.ND_Position_FullWindow(win),
        element_alignment="col"
    )
    tests_scene.add_element(0, test_container)

    #
    ### HEADER: title + bt go back ###
    #

    #
    header: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="header",
        position=nd.ND_Position_Container(w="100%", h="10%", container=test_container),
        element_alignment="row"
    )
    test_container.add_element(header)

    #
    bt_back: nd.ND_Elt_Button = nd.ND_Elt_Button(
        window=win,
        elt_id="bt_back",
        position=nd.ND_Position_Container(w=150, h=40, container=header, position_margins=nd.ND_Position_Margins(margin=15, margin_bottom="50%", margin_top="50%")),
        text="Back",
        events_handler=ND_EventsHandler_Elts(fn_on_click=lambda _: win.set_state("tests_menu"))
    )
    header.add_element(bt_back)


    #
    page_title: nd.ND_Elt_Text = nd.ND_Elt_Text(
        window=win,
        elt_id="page_title",
        position=nd.ND_Position_Container(w=250, h=40, container=header, position_margins=margin_center),
        text="Test 1 - Sprites"
    )
    header.add_element(page_title)

    #
    ### BODY: column of buttons to go to different test scenes.  ###
    #

    #
    body: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="body",
        position=nd.ND_Position_Container(w="100%", h="90%", container=test_container),
        element_alignment="col"
    )
    test_container.add_element(body)

    #
    tiles_atlas: nd.ND_AtlasTexture = nd.ND_AtlasTexture(
        window=win,
        texture_atlas_path="res/basictiles_2.png",
        tiles_size=nd.ND_Point(x=16, y=16)
    )

    #
    multilayer: nd.ND_Elt_MultiLayer = nd.ND_Elt_MultiLayer(
        window=win,
        elt_id="layers",
        position=nd.ND_Position_Container(w="100%", h="100%", container=body)
    )
    #
    body.add_element(multilayer)

    #
    grid: nd.ND_Elt_RectGrid = nd.ND_Elt_RectGrid(
        window=win,
        elt_id="grid",
        position=nd.ND_Position_MultiLayer(w="100%", h="100%", multilayer=multilayer),
        grid_tx=16,
        grid_ty=16,
        grid_lines_width=1,
        grid_lines_color=nd.ND_Color(50, 50, 50)
    )
    #
    multilayer.add_element(layer_id=1, elt=grid)

    #
    # grid_camera: nd.ND_Elt_CameraGrid = nd.ND_Elt_CameraGrid(
    grid_camera = nd.ND_Elt_CameraGrid(
        window=win,
        elt_id="grid_camera",
        position=nd.ND_Position_MultiLayer(w="100%", h="100%", multilayer=multilayer),
        grids_to_render=[grid],
    )
    #
    multilayer.add_element(layer_id=0, elt=grid_camera)

    #
    win.main_app.add_function_to_mainloop_fns_queue(mainloop_name="scene_test1", function=mainloop_scene_test1)

    #
    win.add_scene( tests_scene )


#
def mainloop_scene_test1(main_app: nd.ND_MainApp, delta_time: float):
    global grid_camera, window

    #
    if window.state != "test1_sprites":
        #
        return

    #
    speed: float = 0.001 * delta_time

    #
    print(f"DEBUG | origin : {grid_camera.origin} | zoom = {grid_camera.zoom_x}")

    #
    if main_app.events_manager.is_key_pressed("up arrow"):
        #
        grid_camera.origin.y -= int(speed)
    #
    if main_app.events_manager.is_key_pressed("down arrow"):
        #
        grid_camera.origin.y += int(speed)
    #
    if main_app.events_manager.is_key_pressed("left arrow"):
        #
        grid_camera.origin.x -= int(speed)
    #
    if main_app.events_manager.is_key_pressed("right arrow"):
        #
        grid_camera.origin.x += int(speed)
    #
    if main_app.events_manager.is_key_pressed("a"):
        #
        grid_camera.zoom_x *= 0.99
        grid_camera.zoom_y *= 0.99
        #
        if grid_camera.zoom_y < grid_camera.min_zoom:
            #
            grid_camera.zoom_y = grid_camera.min_zoom
        #
        if grid_camera.zoom_x < grid_camera.min_zoom:
            #
            grid_camera.zoom_x = grid_camera.min_zoom
    #
    if main_app.events_manager.is_key_pressed("e"):
        #
        grid_camera.zoom_x *= 1.01
        grid_camera.zoom_y *= 1.01
        #
        if grid_camera.zoom_y > grid_camera.max_zoom:
            #
            grid_camera.zoom_y = grid_camera.max_zoom
        #
        if grid_camera.zoom_x > grid_camera.max_zoom:
            #
            grid_camera.zoom_x = grid_camera.max_zoom

