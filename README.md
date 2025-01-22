# NappEngine Python

## Description

The goal of this project is to create a full python library to help people to easily create apps or games directly with Python, and to prepare the C++ implementation of this project that will aim to better performances and the ability to export any app / or game created with it into the most device / platform possible (Linux computer, windows computer, MAC computers, Android mobiles, IOS mobiles, Android VR headsets, ...).

## Project Organisation

All the files in the root directory beginning with `lib_nadisplay_` are the core elements of this library.

The project is separated into 2 large layers:

- **The backend layer:** Its role is to use correctly the sub systems rendering engines like (`SDL`, `GLFW`, `Pygame`) for windows management and (`OpenGL`, `Vulkan`) for rendering. The main classes for backend are:

    - `ND_Display`: Global display management and font gestion
    - `ND_Window`: Window specific management and core rendering functions
    - `ND_EventsManager`: Event manager system

    For each possible combination (like `Pygame`,  `SDL + SDLttf`, `SDL + OpenGL`, `GLFW + OpenGL`, `GLFW + Vulkan`), there are scripts where thoses specific classes are implemented.

- **The frontend layer:** Its role is to propose an abstraction layer on common rendering functionnalities and to help design apps or games

The tests are separated into 2 subdirectories, the `tests/apps/` tests and the `tests/scripts/` tests. While the *script tests* are smaller tests that helped to create the backend layers libs (you can see that no `lib_nadisplay_...` files are used for the script tests), the *app tests* are bigger tests that use directly the `lib_nadisplay_...` library to test it like a real project would use it.

Some OpenGL shaders are stored in the folder `gl_shaders/`, the vulkan shaders will be store in the folder `vk_shaders/`.

The full python pip requirements required to run any python file in the project are stored in the file `requirements.txt`, you can install them in any python environments with `pip install -r requirements`.

