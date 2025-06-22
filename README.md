# NappEngine Python

## Description

The goal of this project is to create a full python app engine/library to help people to easily create apps or games directly with Python, and to prepare the C++ implementation of this app engine/library that will aim to better performances and the ability to export any app / or game created with it into the most device / platform possible (Linux computer, windows computer, MAC computers, Android mobiles, IOS mobiles, Android VR headsets, ...).

## Project Organisation

All the files in the root directory beginning with `lib_nadisplay_` are the core elements of this library.

The project is separated into 2 large layers:

- **The backend layer:** Its role is to use correctly the sub systems rendering engines like (`SDL`, `GLFW`, `Pygame`) for windows management and (`OpenGL`, `Vulkan`) for rendering. The main classes for backend are:

- `ND_Display`: Global display management and font gestion
- `ND_Window`: Window specific management and core rendering functions
- `ND_EventsManager`: Event manager system

    For each possible combination (like `Pygame`,  `SDL + SDLGFX`, `SDL + OpenGL`, `GLFW + OpenGL`, `GLFW + Vulkan`), there are scripts where thoses specific classes are implemented.

- **The frontend layer:** Its role is to propose an abstraction layer on common rendering functionnalities and to help design apps or games. The main classes for frontend are:

- `ND_MainApp`
- and the `ND_+Element_Name+` for each element given to use with the library, like `ND_Elt_TextInput` or `ND_Elt_Sprite` or `ND_Elt_Button`.

The main classes are organized in the `lib_nadisplay_core.py`, and all the other classes are organized each in their `lib_nadisplay_???.py` file.

Some OpenGL shaders are stored in the folder `gl_shaders/`, the vulkan shaders will be store in the folder `vk_shaders/`.

The tests are separated into 2 subdirectories, the `tests/apps/` tests and the `tests/scripts/` tests. While the *script tests* are smaller tests that helped to create the backend layers libs (you can see that no `lib_nadisplay_...` files are used for the script tests), the *app tests* are bigger tests that use directly the `lib_nadisplay_...` library to test it like a real project would use it.

- To execute the script tests, you must place your terminal to the subdirectory `tests/scripts/` and launch them with `python test_file.py`.

- To execute the app tests, you must place your terminal to the subdirectory `tests/apps/app_to_test/` and launch them with `python main.py`

- It is strongly recommanded to use a **python venv** for this project, you can create one with `python -m venv venv_dir/`, and activate with it `source venv_dir/bin/activate` (on linux) or `./venv_dir/bin/activate.bat` (on windows), and then deactivate it later with `deactivate`.

The full python pip requirements required to run any python file in the project are stored in the file `requirements.txt`, you can install them in any python environments with `pip install -r requirements`.

## Current state of the project

### Back-end

Currently the only backend working is `SDL + SDLGFX`, the backend `Pygame` is somewhat usable but with major bugs and no multi windowing.

There are some efforts to quickly get the backend `SDL + OpenGL`, then the others working, but for now, some *OpenGL Context Errors* can't be debugged.

Okay, finally, I successfully found the error: sdl2 + opengl on python doesn't work with Wayland ! Had to switch into x11 windows manager, but now got only a black screen.

I'm currently trying glfw + opengl to see what happens, currently developping it.

### Front-end

Currently, there are the following usable classes for creating apps and games with the lib_nadisplay :

- `ND_Elt_Text`
- `ND_Elt_Rectangle`
- `ND_Elt_Sprite`
- `ND_AtlasTexture`
- `ND_Elt_Sprite_of_AtlasTexture`
- `ND_Elt_AnimatedSprite`
- `ND_Elt_Button`
- `ND_Elt_H_ScrollBar`
- `ND_Elt_V_ScrollBar`
- `ND_Elt_LineEdit`
- `ND_Elt_Checkbox`
- `ND_Elt_NumberInput`
- `ND_Elt_SelectOptions`
- `ND_Elt_Container`
- `ND_Elt_MultiLayer`
- `ND_Elt_CameraGrid`
- `ND_Elt_RectGrid`

A lot of new element classes are planned to be added in the future.

### Documentation

The documentation hasn't been started yet, but there will be one well writen and easy to use when the project will be at a state where people can start to use it, that is not really currently the case.

## Example of projects using the NappEngine

- A snake game: [https://github.com/nath54/Snaky](https://github.com/nath54/Snaky)
