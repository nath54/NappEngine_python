
from lib_nadisplay_point import ND_Point
from lib_nadisplay_core import ND_EventsHandler_Elts

import lib_nadisplay as nd


#
test_scenes: dict[str, str] = {

    "Test 0 - GUI Elements": "test0_gui_elements",

    "Test 1 - Sprites": "test1_sprites",

    "Test 2 - Rect Grid": "test2_rect_grid",

    "Test 3 - 3d shapes": "test3_3d_shapes"

}


#
def create_tests_menu_scene(win: nd.ND_Window) -> None:

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
    tests_menu_scene: nd.ND_Scene = nd.ND_Scene(
        window=win,
        scene_id="tests_menu",
        origin=ND_Point(0, 0),
        elements_layers = {},
        on_window_state="tests_menu"
    )

    #
    ### Main Scene Container. ###
    #
    tests_menu_container: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="tests_menu_container",
        position=nd.ND_Position_FullWindow(win),
        element_alignment="col"
    )
    tests_menu_scene.add_element(0, tests_menu_container)

    #
    ### HEADER: title + bt go back ###
    #

    #
    header: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="header",
        position=nd.ND_Position_Container(w="100%", h="10%", container=tests_menu_container),
        element_alignment="row"
    )
    tests_menu_container.add_element(header)

    #
    bt_back: nd.ND_Elt_Button = nd.ND_Elt_Button(
        window=win,
        elt_id="bt_back",
        position=nd.ND_Position_Container(w=150, h=40, container=header, position_margins=nd.ND_Position_Margins(margin=15, margin_bottom="50%", margin_top="50%")),
        text="Back",
        events_handler=ND_EventsHandler_Elts(fn_on_click=lambda _: win.set_state("main_menu"))
    )
    header.add_element(bt_back)


    #
    page_title: nd.ND_Elt_Text = nd.ND_Elt_Text(
        window=win,
        elt_id="page_title",
        position=nd.ND_Position_Container(w=250, h=40, container=header, position_margins=margin_center),
        text="Select a test scene"
    )
    header.add_element(page_title)

    #
    ### BODY: column of buttons to go to different test scenes.  ###
    #

    #
    body: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="body",
        position=nd.ND_Position_Container(w="100%", h="90%", container=tests_menu_container),
        element_alignment="col"
    )
    tests_menu_container.add_element(body)

    #
    bt_tests_container: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="bt_tests_container",
        position=nd.ND_Position_Container(w="80%", h="80%", container=body, position_margins=margin_center),
        element_alignment="col",
        min_space_height_containing_elements=10,
        min_space_width_containing_elements=10,
        scroll_h=True
    )
    body.add_element(bt_tests_container)

    #
    for name, scene_id in test_scenes.items():

        #
        bt_testi: nd.ND_Elt_Button = nd.ND_Elt_Button(
            window=win,
            elt_id=f"bt_{scene_id}",
            position=nd.ND_Position_Container(w=250, h=70, container=bt_tests_container, position_margins=margin_center),
            text=name,
            events_handler=ND_EventsHandler_Elts(fn_on_click=lambda _, s_id=scene_id: win.set_state(s_id))
        )
        bt_tests_container.add_element(bt_testi)

    #
    win.add_scene( tests_menu_scene )
