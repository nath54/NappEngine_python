
from lib_nadisplay_point import ND_Point
from lib_nadisplay_core import ND_EventsHandler_Elts

import lib_nadisplay as nd


#
def create_tests_menu_scene(win: nd.ND_Window) -> None:
    #
    margin_center: nd.ND_Position_Margins = nd.ND_Position_Margins(margin_left="50%", margin_right="50%", margin_top="50%", margin_bottom="50%")
    #
    tests_menu_scene: nd.ND_Scene = nd.ND_Scene(
        window=win,
        scene_id="tests_menu",
        origin=ND_Point(0, 0),
        elements_layers = {},
        on_window_state="tests_menu"
    )

    #
    tests_menu_container: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="tests_menu_container",
        position=nd.ND_Position_FullWindow(win),
        element_alignment="col"
    )
    tests_menu_scene.add_element(0, tests_menu_container)

    ### HEADER ###

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

    ### BODY ###

    #
    body: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="body",
        position=nd.ND_Position_Container(w="100%", h="90%", container=tests_menu_container),
        element_alignment="row"
    )
    tests_menu_container.add_element(body)

    #
    bt_tests_container: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="bt_tests_container",
        position=nd.ND_Position_Container(w="80%", h="80%", container=body, position_margins=margin_center),
        element_alignment="row_wrap"
    )
    body.add_element(bt_tests_container)

    #
    bt_test1: nd.ND_Elt_Button = nd.ND_Elt_Button(
        window=win,
        elt_id="bt_test1",
        position=nd.ND_Position_Container(w=150, h=30, container=bt_tests_container, position_margins=margin_center),
        text="test 1",
        events_handler=ND_EventsHandler_Elts(fn_on_click=lambda _: win.set_state("test_1"))
    )
    bt_tests_container.add_element(bt_test1)

    #
    win.add_scene( tests_menu_scene )
