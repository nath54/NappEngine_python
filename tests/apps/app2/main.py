import sys
sys.path.insert(0, "../../../")

import lib_nadisplay as nd


#
DisplayClass, WindowClass, EventsManagerClass = nd.prepare_backend("sdl_sdlgfx")


if __name__ == "__main__":

    app = nd.ND_MainApp(
                DisplayClass=DisplayClass,
                WindowClass=WindowClass,
                EventsManagerClass=EventsManagerClass,
                global_vars_to_save=[],
                path_to_global_vars_save_file=""
        )

    app.run()
