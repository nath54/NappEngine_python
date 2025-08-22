
from lib_nadisplay_point import ND_Point
from lib_nadisplay_core import ND_EventsHandler_Elts

import lib_nadisplay as nd



#
def create_3d_scene(win: nd.ND_Window, container: nd.ND_Elt_Container) -> None:

    #
    camera: nd.




#
def create_test2_scene(win: nd.ND_Window) -> None:

    #
    ###
    #
    test_scene_id: str = "test2_3d_shapes"

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
        text="Test 3 - 3D Shapes"
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
    create_3d_scene(win=win, container=body)

    #
    win.add_scene( tests_scene )
