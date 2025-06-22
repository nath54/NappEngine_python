
from lib_nadisplay_colors import cl, ND_Color  # type: ignore
from lib_nadisplay_transformation import ND_Transformation  # type: ignore
from lib_nadisplay_point import ND_Point
from lib_nadisplay_rects import ND_Rect  # type: ignore
from lib_nadisplay_position import ND_Position_Margins, ND_Position_Constraints  # type: ignore

import lib_nadisplay as nd


#
def create_main_menu_scene(win: nd.ND_Window) -> None:
    #
    main_menu_scene: nd.ND_Scene = nd.ND_Scene(
        window=win,
        scene_id="main_menu",
        origin=ND_Point(0, 0),
        elements_layers = {},
        on_window_state="main_menu"
    )

    #
    main_menu_container: nd.ND_Container = nd.ND_Container(
        window=win,
        elt_id="main_menu_container",
        position=nd.ND_Position_FullWindow(win),
        element_alignment="col"
    )
    main_menu_scene.add_element(0, main_menu_container)

    #
    game_title: nd.ND_Text = nd.ND_Text(
                            window=win,
                            elt_id="game_title",
                            position=nd.ND_Position_Container(w="100%", h="20%", container=main_menu_container, position_margins=ND_Position_Margins(margin_top=25, margin_bottom=25)),
                            text="Test",
                            font_size=50,
                            font_color=cl("violet"),
    )
    main_menu_container.add_element(game_title)

    #
    bottom_row_container: nd.ND_Container = nd.ND_Container(
        window=win,
        elt_id="bottom_row_container",
        position=nd.ND_Position_Container(w="100%", h="75%", container=main_menu_container),
        element_alignment="row"
    )
    main_menu_container.add_element(bottom_row_container)

    #
    bts_container: nd.ND_Container = nd.ND_Container(
        window=win,
        elt_id="bts_container",
        position=nd.ND_Position_Container(w="30%", h="100%", container=bottom_row_container),
        element_alignment="col"
    )
    bottom_row_container.add_element(bts_container)

    #
    win.main_app.global_vars_set("main_menu_title", game_title)

    #
    bt_tests: nd.ND_Button = nd.ND_Button(
        window=win,
        elt_id="bt_tests",
        position=nd.ND_Position_Container(w=250, h=100, container=bts_container, position_margins=ND_Position_Margins(margin_left="50%", margin_top=25, margin_bottom=25)),
        onclick=lambda _: win.set_state("tests_menu"),
        text="Tests",
        font_size=35
    )
    bts_container.add_element(bt_tests)

    #
    bt_quit: nd.ND_Button = nd.ND_Button(
        window=win,
        elt_id="bt_quit",
        position=nd.ND_Position_Container(w=250, h=100, container=bts_container, position_margins=ND_Position_Margins(margin_left="50%", margin_top=25, margin_bottom=25)),
        onclick=lambda _: win.main_app.quit(),
        text="Quit",
        font_size=35
    )
    bts_container.add_element(bt_quit)

    #
    win.add_scene( main_menu_scene )
