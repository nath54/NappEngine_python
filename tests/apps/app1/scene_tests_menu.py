
from lib_nadisplay_colors import cl, ND_Color, ND_Transformations
from lib_nadisplay_rects import ND_Point, ND_Rect, ND_Position_Margins, ND_Position_Constraints

import lib_nadisplay as nd



#
def on_bt_click_quit(elt: nd.ND_Clickable) -> None:
    #
    win: nd.ND_Window = elt.window
    #
    win.main_app.quit()


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
    menu_title: nd.ND_Text = nd.ND_Text(
                            window=win,
                            elt_id="menu_title",
                            position=nd.ND_Position_Container(w="100%", h="20%", container=main_menu_container, position_margins=ND_Position_Margins(margin_top=25, margin_bottom=25)),
                            text="Test",
                            font_size=50,
                            font_color=cl("violet"),
    )
    main_menu_container.add_element(menu_title)

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
    bt_quit: nd.ND_Button = nd.ND_Button(
        window=win,
        elt_id="bt_quit",
        position=nd.ND_Position_Container(w=250, h=100, container=bts_container, position_margins=ND_Position_Margins(margin_left="50%", margin_top=25, margin_bottom=25)),
        onclick=on_bt_click_quit,
        text="Quit",
        font_size=35
    )
    bts_container.add_element(bt_quit)

    #
    win.add_scene( main_menu_scene )
