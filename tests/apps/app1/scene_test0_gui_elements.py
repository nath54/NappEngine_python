
from lib_nadisplay_point import ND_Point
from lib_nadisplay_core import ND_EventsHandler_Elts

import lib_nadisplay as nd


#
def create_test0_scene(win: nd.ND_Window) -> None:

    #
    ###
    #
    test_scene_id: str = "test0_gui_elements"

    #
    ### Useful margin center item ! ###
    #
    margin_center: nd.ND_Position_Margins = nd.ND_Position_Margins(
        margin_left="50%", margin_right="50%", margin_top=10, margin_bottom=10,
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
        text="Test 0 - GUI Elements"
    )
    header.add_element(page_title)

    #
    ### BODY: column of buttons to go to different test scenes.  ###
    #

    #
    body: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="body",
        position=nd.ND_Position_Container(w="100%", h="100%", container=test_container),
        element_alignment="col"
    )
    test_container.add_element(body)

    #
    button_to_test: nd.ND_Elt_Button = nd.ND_Elt_Button(
        window=win,
        elt_id="button_to_test",
        position=nd.ND_Position_Container(w=250, h=50, container=body, position_margins=margin_center),
        text="0",
        events_handler=nd.ND_EventsHandler_Elts(
            fn_on_click=lambda bt_elt: setattr(bt_elt, "text", str( int( getattr(bt_elt, "text") ) + 1 ) )
        )
    )
    #
    body.add_element(button_to_test)

    #
    row_checkbox: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="row_checkbox",
        position=nd.ND_Position_Container(w="60%", h=60, container=body, position_margins=margin_center),
        overflow_hidden=False
    )
    #
    body.add_element(row_checkbox)

    #
    txt_checkbox: nd.ND_Elt_Text = nd.ND_Elt_Text(
        window=win,
        elt_id="text_checkbox_to_test",
        position=nd.ND_Position_Container(w=150, h=50, container=row_checkbox, position_margins=nd.ND_Position_Margins(margin=10, margin_right="100%", min_margin_left=10, margin_top="50%", margin_bottom="50%")),
        text="Not pressed",
        styles_override={
            "font_color": nd.cl("white")
        },
        text_h_align="left"
    )

    #
    checkbox_to_test: nd.ND_Elt_Checkbox = nd.ND_Elt_Checkbox(
        window=win,
        elt_id="checkbox_to_test",
        position=nd.ND_Position_Container(w=40, h=40, container=row_checkbox, position_margins=nd.ND_Position_Margins(margin=10, margin_left="100%", min_margin_right=10, margin_top="50%", margin_bottom="50%")),
        events_handler=nd.ND_EventsHandler_Elts(
            fn_on_click=lambda cb_elt: setattr(txt_checkbox, "text", "Pressed" if cb_elt.get_value() else "Not pressed")
        )
    )
    #
    row_checkbox.add_element(checkbox_to_test)
    row_checkbox.add_element(txt_checkbox)

    #
    line_edit_to_test: nd.ND_Elt_LineEdit = nd.ND_Elt_LineEdit(
        window=win,
        elt_id="line_edit_to_test",
        position=nd.ND_Position_Container(w=400, h=60, container=body, position_margins=margin_center),
        place_holder="edit me !"
    )
    #
    body.add_element(line_edit_to_test)

    #
    select_option_to_test: nd.ND_Elt_SelectOptions = nd.ND_Elt_SelectOptions(
        window=win,
        elt_id="select_option_to_test",
        position=nd.ND_Position_Container(w=400, h=60, container=body, position_margins=margin_center),
        value="option A",
        options=set(["option A", "option B", "option C"]),
        option_list_buttons_height=180,
    )
    #
    body.add_element(select_option_to_test)

    #
    number_input_to_test: nd.ND_Elt_NumberInput = nd.ND_Elt_NumberInput(
        window=win,
        elt_id="number_input_to_test",
        position=nd.ND_Position_Container(w=400, h=60, container=body, position_margins=margin_center),
        value=42,
        min_value=0,
        max_value=50
    )
    #
    body.add_element(number_input_to_test)

    #
    row_cols: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="row_cols",
        position=nd.ND_Position_Container(w="50%", h=250, container=body, position_margins=margin_center),
        element_alignment="row"
    )
    #
    body.add_element(row_cols)

    #
    col1: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="col1",
        position=nd.ND_Position_Container(w=100, h=250, container=row_cols, position_margins=margin_center),
        element_alignment="col"
    )
    #
    row_cols.add_element(col1)

    #
    col2: nd.ND_Elt_Container = nd.ND_Elt_Container(
        window=win,
        elt_id="col2",
        position=nd.ND_Position_Container(w=250, h=250, container=row_cols, position_margins=margin_center),
        element_alignment="col"
    )
    #
    row_cols.add_element(col2)

    #
    txt_scr1: nd.ND_Elt_Text = nd.ND_Elt_Text(
        window=win,
        elt_id="txt_scr1",
        position=nd.ND_Position_Container(w=150, h=50, container=col2, position_margins=margin_center),
        text="Scrollbar value = 1 / 500",
        styles_override={
            "font_color": nd.ND_Color(255, 255, 255)
        }
    )

    #
    txt_scr2: nd.ND_Elt_Text = nd.ND_Elt_Text(
        window=win,
        elt_id="txt_scr2",
        position=nd.ND_Position_Container(w=150, h=50, container=col2, position_margins=margin_center),
        text="Scrollbar value = 1 / 500",
        styles_override={
            "font_color": nd.ND_Color(255, 255, 255)
        }
    )

    #
    v_scroll_to_test: nd.ND_Elt_V_ScrollBar = nd.ND_Elt_V_ScrollBar(
        window=win,
        elt_id="v_scrollbar_to_test",
        position=nd.ND_Position_Container(w=30, h=200, container=col1),
        content_height=500,
        scroll_position=1,
        on_value_changed=lambda elt, nv: setattr(txt_scr1, "text", f"Scrollbar value = {nv} / 500")
    )
    #
    col1.add_element(v_scroll_to_test)

    #
    h_scroll_to_test: nd.ND_Elt_H_ScrollBar = nd.ND_Elt_H_ScrollBar(
        window=win,
        elt_id="h_scrollbar_to_test",
        position=nd.ND_Position_Container(w=200, h=30, container=col2),
        content_width=500,
        scroll_position=1,
        on_value_changed=lambda elt, nv: setattr(txt_scr2, "text", f"Scrollbar value = {nv} / 500")
    )
    #
    col2.add_element(h_scroll_to_test)
    #
    col2.add_element(txt_scr1)
    #
    col2.add_element(txt_scr2)

    #
    win.add_scene( tests_scene )
