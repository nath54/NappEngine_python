"""
Author: CERISARA Nathan (https://github.com/nath54)

File Description:

Main file for lib_nadisplay, all front-end elements and abstract classes of front-end classes.

"""


from typing import Callable, Any, Optional, Type, cast

import time

from threading import Thread, Lock, Condition

import atexit

import os
import pickle

from lib_nadisplay_colors import ND_Color
from lib_nadisplay_point import ND_Point
from lib_nadisplay_rects import ND_Rect
from lib_nadisplay_position import ND_Position
from lib_nadisplay_transformation import ND_Transformation
from lib_nadisplay_quadtree import ND_Quadtree

import lib_nadisplay_events as nd_event


#
class ND_MainApp:
    #
    def __init__(self, DisplayClass: Type["ND_Display"], WindowClass: Type["ND_Window"], EventsManagerClass: Type["ND_EventsManager"], global_vars_to_save: list[str] = [], path_to_global_vars_save_file: str = "") -> None:
        #
        self.global_vars: dict[str, Any] = {}
        self.global_vars_muts: dict[str, Lock] = {}
        self.global_vars_creation_mut: Lock = Lock()
        #
        self.global_vars_to_save: list[str] = global_vars_to_save
        self.path_to_global_vars_save_file: str = path_to_global_vars_save_file
        #
        self.fps_display: int = 60
        self.fps_physics: int = 60
        self.fps_other_fns: int = 60
        self.frame_duration_display: float = 1000.0 / float(self.fps_display)
        self.frame_duration_physics: float = 1000.0 / float(self.fps_physics)
        self.frame_duration_other_fns: float = 1000.0 / float(self.fps_other_fns)
        #
        self.current_fps: int = 0
        #
        self.is_running: bool = False
        self.is_threading: bool = True
        #
        self.display: Optional[ND_Display] = DisplayClass(self, WindowClass=WindowClass)
        #
        self.display.init_display()
        #
        self.events_manager: ND_EventsManager = EventsManagerClass(self)
        #
        self.init_queue_functions: list[Callable[[ND_MainApp], None]] = []
        #
        self.mainloop_queue_functions: dict[str, list[Callable[[ND_MainApp, float], None]]] = {
            "physics": []
        }
        self.mainloop_queue_fns_mutex: Lock = Lock()
        #
        self.events_functions: dict[str, list[Callable[[ND_MainApp], None]]] = {}
        self.events_functions_mutex: Lock = Lock()
        #
        self.threads: list[Thread] = []
        self.threads_names: list[str] = []
        self.threads_ids_not_joined: set[int] = set()
        self.mutex_threads_creation: Lock = Lock()
        self.threads_condition: Condition = Condition()
        #
        #
        if self.path_to_global_vars_save_file != "" and os.path.exists(self.path_to_global_vars_save_file):
            #
            self.global_vars_load_from_path(self.path_to_global_vars_save_file)

    #
    def atexit(self) -> None:
        #
        print("At exit catched")
        #
        if self.global_vars_to_save and self.path_to_global_vars_save_file != "":
            self.global_vars_save_to_path(path=self.path_to_global_vars_save_file, vars_to_save=self.global_vars_to_save)
        #
        self.is_running = False
        #
        if self.is_threading:
            self.waiting_all_threads()

    #
    def get_time_msec(self) -> float:
        #
        if self.display is not None:
            return self.display.get_time_msec()
        #
        else:
            return time.time() * 1000.0

    #
    def wait_time_msec(self, delay_in_msec: float) -> None:
        #
        if self.display is not None:
            self.display.wait_time_msec(delay_in_msec)
        #
        time.sleep(delay_in_msec / 1000.0)

    #
    def global_vars_save_to_path(self, path: str, vars_to_save: list[str]) -> None:
        #
        data_to_save: dict[str, Any] = {}
        #
        for var in vars_to_save:
            if var in self.global_vars:
                #
                # print(f"DEBUG | global vars save {var}={self.global_vars[var]}")
                #
                data_to_save[var] = self.global_vars[var]
        #
        with open(path, "wb") as f:
            pickle.dump(data_to_save, f)
        #
        print(f"MainApp : saved global vars to {path}")
        #

    #
    def global_vars_load_from_path(self, path: str) -> None:
        #
        with open(path, "rb") as f:
            data_to_load: dict[str, Any] = pickle.load(f)
        #
        for key in data_to_load:
            #
            # print(f"DEBUG | global vars load {key}={data_to_load[key]}")
            #
            self.global_vars_set(key, data_to_load[key])
        #
        print(f"MainApp : loaded global vars from {path}")
        #

    #
    def global_vars_create(self, var_name: str, var_value: Any, if_exists: str = "ignore") -> None:
        #
        self.global_vars_creation_mut.acquire()
        #
        if var_name not in self.global_vars:
            #
            self.global_vars[var_name] = var_value
            self.global_vars_muts[var_name] = Lock()
            #
        else:
            #
            if if_exists == "override":
                self.global_vars[var_name] = var_value
            #
        #
        self.global_vars_creation_mut.release()

    #
    def global_vars_get_optional(self, var_name: str) -> Optional[Any]:
        #
        if var_name in self.global_vars:
            return self.global_vars[var_name]
        return None

    # If is in global vars, returns it, else return default_value, all the cases, that is not None
    def global_vars_get_default(self, var_name: str, default_value: Any) -> Any:
        #
        if var_name in self.global_vars:
            return self.global_vars[var_name]
        #
        return default_value

    # Get Not None
    def global_vars_get(self, var_name: str) -> Any:
        #
        if var_name in self.global_vars:
            return self.global_vars[var_name]
        #
        raise IndexError(f"CRITICAL ERROR !\nGlobal Vars Error: Index {var_name} not found in global variables !")

    #
    def global_vars_set(self, var_name: str, var_value: Any, if_not_exists: str = "create") -> None:
        #
        if var_name in self.global_vars:
            #
            with self.global_vars_muts[var_name]:
                #
                self.global_vars[var_name] = var_value
            #
        else:
            #
            if if_not_exists == "create":
                #
                with self.global_vars_creation_mut:
                    #
                    self.global_vars[var_name] = var_value
                    self.global_vars_muts[var_name] = Lock()

    #
    def global_vars_list_append(self, var_name: str, obj_value: Any, if_not_exists: str = "create") -> None:
        #
        if var_name in self.global_vars:
            #
            with self.global_vars_muts[var_name]:
                #
                self.global_vars[var_name].append(obj_value)
            #
        else:
            #
            if if_not_exists == "create":
                #
                with self.global_vars_creation_mut:
                    #
                    self.global_vars[var_name] = [obj_value]
                    self.global_vars_muts[var_name] = Lock()

    #
    def global_vars_list_remove(self, var_name: str, obj_value: Any, if_not_exists: str = "ignore") -> None:
        #
        if var_name in self.global_vars:
            #
            with self.global_vars_muts[var_name]:
                #
                self.global_vars[var_name].remove(obj_value)
            #
        else:
            #
            if not if_not_exists == "error":
                raise UserWarning("#TODO: complete error message")

    #
    def global_vars_list_del_at_idx(self, var_name: str, idx: int, if_not_exists: str = "ignore") -> None:
        #
        if var_name in self.global_vars:
            #
            with self.global_vars_muts[var_name]:
                #
                del self.global_vars[var_name][idx]
            #
        else:
            #
            if not if_not_exists == "error":
                raise UserWarning("#TODO: complete error message")

    #
    def global_vars_list_length(self, var_name: str) -> int:
        #
        if var_name in self.global_vars:
            #
            return len(self.global_vars[var_name])
            #
        else:
            #
            return 0

    #
    def global_vars_list_get_at_idx(self, var_name: str, idx: int) -> Optional[Any]:
        #
        if var_name in self.global_vars:
            #
            if idx < len(self.global_vars[var_name]):
                return self.global_vars[var_name][idx]
            #
            else:
                return None
            #
        else:
            #
            return None

    #
    def global_vars_list_set_at_idx(self, var_name: str, idx: int, obj_value: Any, if_not_exists: str = "error", if_idx_not_in_list_length: str = "error") -> None:
        #
        if var_name in self.global_vars:
            #
            with self.global_vars_muts[var_name]:
                #
                if idx < len(self.global_vars[var_name]):
                    self.global_vars[var_name][idx] = obj_value
                else:
                    #
                    if if_idx_not_in_list_length == "error":
                        #
                        raise UserWarning("Error, #TODO: complete error message")
            #
        else:
            #
            if if_not_exists == "error":
                #
                raise UserWarning("Error, #TODO: complete error message")

    #
    def global_vars_dict_set(self, var_name: str, dict_key: Any, obj_value: Any, if_not_exists: str = "ignore") -> None:
        #
        if var_name in self.global_vars:
            #
            with self.global_vars_muts[var_name]:
                #
                self.global_vars[var_name][dict_key] = obj_value
            #
        else:
            #
            if if_not_exists == "create":
                #
                with self.global_vars_creation_mut:
                    #
                    self.global_vars[var_name] = {
                        dict_key: obj_value
                    }
                    self.global_vars_muts[var_name] = Lock()

    #
    def global_vars_dict_get(self, var_name: str, dict_key: Any, if_not_exists: str = "none") -> Any:
        #
        if var_name in self.global_vars:
            #
            return self.global_vars[var_name][dict_key]
            #
        else:
            #
            if if_not_exists == "error":
                #
                raise UserWarning("Error, #TODO: complete error message")
            #
            elif if_not_exists == "none":
                #
                return None

    #
    def global_vars_dict_del(self, var_name: str, dict_key: Any, if_not_exists: str = "ignore") -> None:
        #
        if var_name in self.global_vars:
            #
            with self.global_vars_muts[var_name]:
                #
                del self.global_vars[var_name][dict_key]
            #
        else:
            #
            if not if_not_exists == "error":
                raise UserWarning("#TODO: complete error message")

    #
    def global_vars_exists(self, var_name: str) -> bool:
        return var_name in self.global_vars

    #
    def get_element(self, window_id: int, scene_id: str, elt_id: str) -> Optional["ND_Elt"]:
        #
        if not self.display:
            return None
        #
        if window_id not in self.display.windows:
            return None
        #
        win: Optional[ND_Window] = self.display.windows[window_id]
        #
        if not win:
            return None
        #
        if scene_id not in win.scenes:
            return None
        #
        if elt_id in win.scenes[scene_id].elements_by_id:
            return win.scenes[scene_id].elements_by_id[elt_id]
        #
        for elt in win.scenes[scene_id].elements_by_id.values():
            #
            r: Optional[ND_Elt] = elt.get_element_recursively_from_subchild(elt_id=elt_id)
            #
            if r is not None:
                return r
        #
        return None

    #
    def get_element_value(self, window_id: int, scene_id: str, elt_id: str) -> Optional[bool | int | float | str]:
        #
        elt: Optional[ND_Elt] = self.get_element(window_id, scene_id, elt_id)
        #
        if elt is None:
            return None
        #
        return elt.get_value()

    #
    def get_element_recursively_from_subchild(self, elt_cont: "ND_Elt", elt_id: str) -> Optional["ND_Elt"]:
        #
        return elt_cont.get_element_recursively_from_subchild(elt_id = elt_id)

    #
    def add_function_to_mainloop_fns_queue(self, mainloop_name: str, function: Callable[["ND_MainApp", float], None]) -> None:
        #
        with self.mainloop_queue_fns_mutex:
            #
            if mainloop_name not in self.mainloop_queue_functions:
                self.mainloop_queue_functions[mainloop_name] = []
            #
            self.mainloop_queue_functions[mainloop_name].append(function)

    #
    def add_functions_to_mainloop_fns_queue(self, mainloop_name: str, functions: list[Callable[["ND_MainApp", float], None]]) -> None:
        #
        with self.mainloop_queue_fns_mutex:
            #
            if mainloop_name not in self.mainloop_queue_functions:
                self.mainloop_queue_functions[mainloop_name] = []
            #
            self.mainloop_queue_functions[mainloop_name] += functions

    #
    def delete_mainloop_fns_queue(self, mainloop_name: str) -> None:
        #
        with self.mainloop_queue_fns_mutex:
            #
            if mainloop_name in self.mainloop_queue_functions:
                self.mainloop_queue_functions[mainloop_name] = []
                del self.mainloop_queue_functions[mainloop_name]

    #
    def get_mainloop_fns_queue(self, mainloop_name: str) -> list[Callable[["ND_MainApp", float], None]]:
        #
        if mainloop_name not in self.mainloop_queue_functions:
            return []
        #
        return self.mainloop_queue_functions[mainloop_name]

    #
    def add_function_to_event_fns_queue(self, event_name: str, fn: Callable[["ND_MainApp"], None]) -> None:
        #
        with self.events_functions_mutex:
            #
            if event_name not in self.events_functions:
                #
                self.events_functions[event_name] = []
            #
            self.events_functions[event_name].append( fn )
        #

    #
    def display_thread(self) -> None:

        start_time: float = 0.0
        elapsed_time: float = 0.0
        delay: float = 0.0  # Delay with first frame

        #
        while self.is_running:
            #
            elapsed_time = self.get_time_msec()
            if start_time != 0:
                delay = elapsed_time - start_time
                if delay != 0:
                    self.current_fps = int(1.0 / delay)
            #
            start_time = elapsed_time    # Start of the frame in milliseconds

            #
            if self.display is not None:
                #
                self.display.update_display()

            # Calculate the time taken for this frame
            elapsed_time = self.get_time_msec() - start_time

            # If the frame was rendered faster than the target duration, delay
            if elapsed_time < self.frame_duration_display:
                self.wait_time_msec(self.frame_duration_display - elapsed_time)

    #
    def handle_event_to_display_windows(self, event: nd_event.ND_Event) -> None:
        #
        if self.display is None:
            return
        #
        win: Optional[ND_Window]
        for win in list(self.display.windows.values()):
            #
            if win is None or not win.is_hovered_by_mouse():
                continue
            #
            scene: ND_Scene
            for scene in win.scenes.values():
                #
                scene.handle_event(event)  # Potentiel Blockage ici lors de la fermeture de l'application

    #
    def handle_windows_event(self, event: nd_event.ND_EventWindow) -> str:
        #
        if self.display is None:
            return ""

        #
        window: Optional[ND_Window] = self.display.get_window(event.window_id)

        #
        if window is None:
            return ""

        #
        if isinstance(event, nd_event.ND_EventWindowClose):
            #
            self.display.destroy_window(window.window_id)
            #
            return "window_close"
        #
        elif isinstance(event, nd_event.ND_EventWindowMoved):
            #
            window.update_position(event.x, event.y)
            #
            return "window_moved"
        #
        elif isinstance(event, nd_event.ND_EventWindowResized):
            #
            # print(f"DEBUG | ND_EventWindowResized = {event}")
            #
            window.update_size(event.w, event.h)
            #
            scene: ND_Scene
            for scene in window.scenes.values():
                #
                scene.handle_window_resize()
            #
            return "window_resized"

        #
        return ""

    #
    def manage_events(self) -> bool:
        #
        event: Optional[nd_event.ND_Event] = self.events_manager.poll_next_event()

        #
        if event is None:
            return False

        #
        event_name: str = ""

        #
        if isinstance(event, nd_event.ND_EventQuit):
            #
            self.quit()
            #
            return True

        #
        elif isinstance(event, nd_event.ND_EventKeyDown) and event.key != "":
            event_name = f"keydown_{event.key}"

        #
        elif isinstance(event, nd_event.ND_EventKeyUp) and event.key != "":
            event_name = f"keyup_{event.key}"

        #
        elif isinstance(event, nd_event.ND_EventWindow):
            #
            if isinstance(event, nd_event.ND_EventWindowShown) or isinstance(event, nd_event.ND_EventWindowHidden):
                return True
            #
            event_name = self.handle_windows_event(event)

        #
        self.handle_event_to_display_windows(event)

        #
        if False and event_name != "":
            print(f"EVENT NAME : {event_name}")

        #
        if event_name in self.events_functions:
            #
            for fn in self.events_functions[event_name]:
                fn(self)
        #
        return True

    #
    def events_thread(self) -> None:
        #
        while self.is_running:
            #
            self.manage_events()

    #
    def start_events_thread(self) -> None:
        #
        if not self.is_threading:
            return
        #
        if self.display is not None and not self.display.events_thread_in_main_thread:
            return
        #
        self.create_thread( self.events_thread, thread_name = "events_threads")
        print(f" - thread {self.threads[-1]} for events created")

    #
    def custom_function_queue_thread(self, thread_name: str) -> None:
        #
        start_time: float = 0.0
        elapsed_time: float = 0.0

        #
        while self.is_running:
            #
            start_time = self.get_time_msec()  # Start of the frame in milliseconds
            #
            for fn in self.mainloop_queue_functions[thread_name]:
                fn(self, elapsed_time)
            #

            # Calculate the time taken for this frame
            elapsed_time = self.get_time_msec() - start_time

            # If the frame was rendered faster than the target duration, delay
            if thread_name == "physics":
                if elapsed_time < self.frame_duration_physics:
                    self.wait_time_msec(self.frame_duration_physics - elapsed_time)
            else:
                if elapsed_time < self.frame_duration_other_fns:
                    self.wait_time_msec(self.frame_duration_other_fns - elapsed_time)

    #
    def start_init_queue_functions(self) -> None:
        #
        print("\nBegin to exec all init functions in order\n")

        # Init functions queue
        for fn in self.init_queue_functions:
            fn(self)
            print(f" - Init function called {fn}")

        print("\nAll Init functions called\n")

    #
    def create_all_threads(self) -> None:
        #
        if not self.is_threading:
            return
        #
        print("\nBegin to start threads\n")

        # Display thread
        if self.display is not None and not self.display.display_thread_in_main_thread:
            self.create_thread( self.display_thread, thread_name="display_thread")
            print(f" - thread {self.threads[-1]} for display created")

        # All the other functions thread
        thread_name: str
        for thread_name in self.mainloop_queue_functions:
            self.create_thread( self.custom_function_queue_thread, [thread_name], thread_name=thread_name )

        # Start threads
        for thread in self.threads:
            thread.start()
            print(f" - custom thread {thread} created")

        print("\nAll thread created\n")

    #
    def thread_wrap_fn(self, fn_to_call: Callable[..., Any], fn_to_call_args: list[Any]) -> None:

        #
        fn_to_call(*fn_to_call_args)

        #
        with self.threads_condition:
            self.threads_condition.notify_all()

    #
    def create_thread(self, fn_to_call: Callable[..., Any], fn_to_call_args: list[Any] = [], thread_name: str = "unknown thread") -> int:
        #
        if not self.is_threading:
            return -1
        #
        id_thread: int = -1

        #
        with self.mutex_threads_creation:
            #
            id_thread = len(self.threads)
            self.threads_ids_not_joined.add( id_thread )

            #
            self.threads.append(
                Thread( target=self.thread_wrap_fn, args=[fn_to_call, fn_to_call_args] )
            )
            self.threads_names.append( thread_name )

        #
        return id_thread

    #
    def waiting_all_threads(self) -> None:
        #
        if not self.is_threading:
            return
        #
        print("\nWaiting for threads to finish...\n")

        # While not all threads are done
        while self.threads_ids_not_joined:
            #
            spc: str = "\n - "
            print(f"Threads to wait :\n  - {spc.join([str(self.threads_names[t]) for t in list(self.threads_ids_not_joined)])}")
            #
            with self.threads_condition:
                #
                self.threads_condition.wait()  # Will block here until notified
                #
                for thread_id in list(self.threads_ids_not_joined):
                    #
                    if not self.threads[thread_id].is_alive():  # Check if the thread has finished
                        #
                        print(f"  -> Waiting for thread {thread_id} ({self.threads[thread_id]}) to join...")
                        #
                        self.threads[thread_id].join()          # Join the thread if it's done
                        print(f" - thread {self.threads[thread_id]} joined")
                        self.threads_ids_not_joined.remove(thread_id)  # Remove it from the list
                    #
                    print("    * done.")

        #
        print("\nAll threads joined\n")

    #
    def mainloop_without_threads(self) -> None:
        #
        start_time: float = 0.0
        elapsed_time: float = 0.0
        delay: float = 0.0  # Delay with first frame

        #
        while self.is_running:
            #
            elapsed_time = self.get_time_msec()
            if start_time != 0:
                delay = elapsed_time - start_time
                if delay != 0:
                    self.current_fps = int(1.0 / delay)
            #
            start_time = elapsed_time    # Start of the frame in milliseconds

            # Manage events
            max_events_per_frame: int = 200
            current_events_per_frame: int = 0
            while self.manage_events() and current_events_per_frame < max_events_per_frame:
                current_events_per_frame += 1

            # Manage all the other mainloop runs
            queue_name: str
            fn: Callable[[ND_MainApp, float], None]
            for queue_name in self.mainloop_queue_functions:
                for fn in self.mainloop_queue_functions[queue_name]:
                    fn(self, elapsed_time)

            #
            if self.display is not None:
                #
                self.display.update_display()

            # Calculate the time taken for this frame
            elapsed_time = self.get_time_msec() - start_time

            # If the frame was rendered faster than the target duration, delay
            if elapsed_time < self.frame_duration_display:
                self.wait_time_msec(self.frame_duration_display - elapsed_time)

    #
    def mainloop_threads_display_and_events(self) -> None:
        #
        start_time: float = 0.0
        elapsed_time: float = 0.0
        delay: float = 0.0  # Delay with first frame

        #
        while self.is_running:
            #
            elapsed_time = self.get_time_msec()
            if start_time != 0:
                delay = elapsed_time - start_time
                if delay != 0:
                    self.current_fps = int(1.0 / delay)
                print(f"Fps : {self.current_fps}")
            #
            start_time = elapsed_time    # Start of the frame in milliseconds

            # Manage events
            max_events_per_frame: int = 200
            current_events_per_frame: int = 0
            while self.manage_events() and current_events_per_frame < max_events_per_frame:
                current_events_per_frame += 1

            #
            if self.display is not None:
                #
                self.display.update_display()

            # Calculate the time taken for this frame
            elapsed_time = self.get_time_msec() - start_time

            # If the frame was rendered faster than the target duration, delay
            if elapsed_time < self.frame_duration_display:
                self.wait_time_msec(self.frame_duration_display - elapsed_time)

    #
    def run(self) -> None:
        #
        atexit.register(self.atexit)
        #
        self.is_running = True
        #
        print("\nBeginning of the app...\n")
        #
        self.start_init_queue_functions()
        #
        if self.display is not None and not self.display.main_not_threading:
            self.is_threading = False
        self.is_threading = False
        #
        if self.is_threading:
            self.create_all_threads()
        #
        if self.display is not None:
            if not self.display.main_not_threading:
                if self.display.display_thread_in_main_thread and not self.display.events_thread_in_main_thread:
                    self.display_thread()
                elif not self.display.display_thread_in_main_thread and self.display.events_thread_in_main_thread:
                    self.events_thread()
                elif not self.display.display_thread_in_main_thread and self.display.events_thread_in_main_thread:
                    self.mainloop_threads_display_and_events()
            else:
                self.mainloop_without_threads()
        #
        if self.is_threading:
            self.waiting_all_threads()

    #
    def quit(self) -> None:
        #
        self.is_running = False
        #
        if self.display is not None:
            self.display.destroy_display()
        #
        exit(0)


#
class ND_Display:
    #
    def __init__(self, main_app: ND_MainApp, WindowClass: Type["ND_Window"]) -> None:
        #
        self.main_not_threading: bool = False
        self.events_thread_in_main_thread: bool = False
        self.display_thread_in_main_thread: bool = False
        #
        self.WindowClass: Type[ND_Window] = WindowClass
        #
        self.main_app: ND_MainApp = main_app
        #
        self.font_names: dict[str, str] = {}
        self.default_font: str = "FreeSans"
        #
        self.windows: dict[int, Optional[ND_Window]] = {}
        self.thread_create_window: Lock = Lock()
        #
        self.vulkan_instance: Optional[object] = None
        #
        self.shader_program: int = -1
        self.shader_program_textures: int = -1
        #
        self.mutex_display: Lock = Lock()
        #
        self.initialized: bool = False

    #
    def get_time_msec(self) -> float:
            return time.time() * 1000.0

    #
    def wait_time_msec(self, delay_in_msec: float) -> None:
        time.sleep(delay_in_msec / 1000.0)

    #
    def load_system_fonts(self) -> None:
        """Scans system directories for fonts and adds them to the font_names dictionary."""

        #
        font_dirs: list[str] = []

        #
        if os.name == "nt":  # Windows
            font_dirs.append("C:/Windows/Fonts/")
        elif os.name == "posix":  # macOS, Linux
            if "darwin" in os.uname().sysname.lower():  # macOS
                font_dirs.extend([
                    "/Library/Fonts/",
                    "/System/Library/Fonts/",
                    os.path.expanduser("~/Library/Fonts/")
                ])
            else:  # Linux
                font_dirs.extend([
                    "/usr/share/fonts/",
                    "/usr/local/share/fonts/",
                    os.path.expanduser("~/.fonts/")
                ])

        # Scan directories for .ttf and .otf files
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                for root, _, files in os.walk(font_dir):
                    for file in files:
                        if file.endswith((".ttf", ".otf")):
                            font_path = os.path.join(root, file)
                            font_name = os.path.splitext(file)[0]  # Use file name without extension as font name
                            self.font_names[font_name] = font_path

    #
    def init_display(self) -> None:
        #
        return

    #
    def destroy_display(self) -> None:
        #
        return

    #
    def add_font(self, font_path: str, font_name: str) -> None:
        #
        self.font_names[font_name] = font_path

    #
    def get_font(self, font: str, font_size: int) -> Optional[object]:
        #
        return None

    #
    def get_all_loaded_fonts(self) -> list[Any]:
        #
        return []

    #
    def update_display(self) -> None:
        #
        for window in self.windows.values():
            #
            if window is not None:
                window.update_display()

    #
    def get_focused_window_id(self) -> int:
        return -1

    #
    def create_window(self, window_params: dict[str, Any], error_if_win_id_not_available: bool = False) -> int:
        #
        return -1

    #
    def get_window(self, window_id: int) -> Optional["ND_Window"]:
        #
        if window_id not in self.windows:
            #
            return None
        #
        return self.windows[window_id]

    #
    def destroy_window(self, win_id: int) -> None:
        #
        return


#
class ND_Window:
    #
    def __init__(
            self,
            display: ND_Display,
            window_id: int,
            init_state: Optional[str] = None
        ):

        #
        self.window_id: int = window_id

        #
        self.display: ND_Display = display

        #
        self.main_app: ND_MainApp = self.display.main_app

        # Global Window Position in Global Desktop Space
        self.x: int = 0
        self.y: int = 0
        self.width: int = 640
        self.height: int = 480

        # Warning: This has to be updated at each change !
        self.rect: ND_Rect = ND_Rect(self.x, self.y, self.width, self.height)

        #
        self.sdl_or_glfw_window_id: int = -1

        #
        self.display_states: dict[str, Optional[Callable[[], None]]] = {}
        #
        self.state: Optional[str] = init_state

        #
        self.clip_rect_stack: list[ND_Rect] = []
        #
        self.scenes: dict[str, ND_Scene] = {}

        #
        self.next_texture_id: int = 0

    #
    def push_to_clip_rect_stack(self, x: int, y: int, w: int, h: int) -> None:
        #
        self.clip_rect_stack.append(ND_Rect(x, y, w, y))

    #
    def get_top_of_clip_rect_stack(self) -> Optional[ND_Rect]:
        #
        if self.clip_rect_stack:
            return self.clip_rect_stack[-1]
        #
        return None

    #
    def remove_top_of_clip_rect_stack(self) -> None:
        #
        if self.clip_rect_stack:
            self.clip_rect_stack.pop(-1)

    #
    def destroy_window(self) -> None:
        #
        return

    #
    def set_title(self, new_title: str) -> None:
        #
        return

    #
    def set_position(self, new_x: int, new_y: int) -> None:
        #
        return

    #
    def update_position(self, new_x: int, new_y: int) -> None:
        #
        self.x, self.y = new_x, new_y
        #
        self.rect = ND_Rect(self.x, self.y, self.width, self.height)

    #
    def update_size(self, new_w: int, new_h: int) -> None:
        #
        self.width, self.height = new_w, new_h
        #
        self.rect = ND_Rect(self.x, self.y, self.width, self.height)

    #
    def set_fullscreen(self, mode: int) -> None:
        #
        return

    #
    def set_size(self, new_width: int, new_height: int) -> None:
        #
        return

    #
    def add_scene(self, scene: "ND_Scene") -> None:
        #
        self.scenes[scene.scene_id] = scene

    #
    def update_scene_sizes(self) -> None:
        #
        scene: ND_Scene
        for scene in self.scenes.values():
            #
            scene.handle_window_resize()

    #
    def set_state(self, state: str) -> None:
        #
        self.state = state

    #
    def is_hovered_by_mouse(self) -> bool:
        #
        rect_window: ND_Rect = ND_Rect(self.x, self.y, self.width, self.height)
        pt_mouse: ND_Point = self.display.main_app.events_manager.get_global_mouse_position()
        #
        return rect_window.contains_point( pt_mouse )

    #
    def blit_texture(self, texture: Any, dst_rect: ND_Rect) -> None:
        #
        return

    #
    def prepare_text_to_render(self, text: str, color: ND_Color, font_size: int, font_name: Optional[str] = None) -> int:
        #
        return -1

    #
    def prepare_image_to_render(self, img_path: str) -> int:
        #
        return -1

    #
    def render_prepared_texture(self, texture_id: int, x: int, y: int, width: int, height: int, transformations: ND_Transformation = ND_Transformation()) -> None:
        #
        return

    #
    def render_part_of_prepared_texture(self, texture_id: int, x: int, y: int, w: int, h: int, src_x: int, src_y: int, src_w: int, src_h: int, transformations: ND_Transformation = ND_Transformation()) -> None:
        #
        return

    #
    def get_prepared_texture_size(self, texture_id: int) -> ND_Point:
        #
        return ND_Point(0, 0)

    #
    def destroy_prepared_texture(self, texture_id: int) -> None:
        #
        return

    #
    def draw_text(self, txt: str, x: int, y: int, font_size: int, font_color: ND_Color, font_name: Optional[str] = None) -> None:
        #
        return

    #
    def get_text_size_with_font(self, txt: str, font_size: int, font_name: Optional[str] = None) -> ND_Point:
        #
        return ND_Point(0, 0)

    #
    def get_count_of_renderable_chars_fitting_given_width(self, txt: str, given_width: int, font_size: int, font_name: Optional[str] = None) -> tuple[int, int]:
        #
        return 0, 0

    #
    def draw_pixel(self, x: int, y: int, color: ND_Color) -> None:
        #
        return

    #
    def draw_hline(self, x1: int, x2: int, y: int, color: ND_Color) -> None:
        #
        return

    #
    def draw_vline(self, x: int, y1: int, y2: int, color: ND_Color) -> None:
        #
        return

    #
    def draw_line(self, x1: int, x2: int, y1: int, y2: int, color: ND_Color) -> None:
        #
        return

    #
    def draw_thick_line(self, x1: int, x2: int, y1: int, y2: int, line_thickness: int, color: ND_Color) -> None:
        #
        return

    #
    def draw_rounded_rect(self, x: int, y: int, width: int, height: int, radius: int, fill_color: ND_Color, border_color: ND_Color) -> None:
        #
        return

    #
    def draw_unfilled_rect(self, x: int, y: int, width: int, height: int, outline_color: ND_Color) -> None:
        #
        return

    #
    def draw_filled_rect(self, x: int, y: int, width: int, height: int, fill_color: ND_Color) -> None:
        #
        return

    #
    def draw_unfilled_circle(self, x: int, y: int, radius: int, outline_color: ND_Color) -> None:
        #
        return

    #
    def draw_filled_circle(self, x: int, y: int, radius: int, fill_color: ND_Color) -> None:
        #
        return

    #
    def draw_unfilled_ellipse(self, x: int, y: int, rx: int, ry: int, outline_color: ND_Color) -> None:
        #
        return

    #
    def draw_filled_ellipse(self, x: int, y: int, rx: int, ry: int, fill_color: ND_Color) -> None:
        #
        return

    #
    def draw_arc(self, x: int, y: int, radius: float, angle_start: float, angle_end: float, color: ND_Color) -> None:
        #
        return

    #
    def draw_unfilled_pie(self, x: int, y: int, radius: float, angle_start: float, angle_end: float, outline_color: ND_Color) -> None:
        #
        return

    #
    def draw_filled_pie(self, x: int, y: int, radius: float, angle_start: float, angle_end: float, fill_color: ND_Color) -> None:
        #
        return

    #
    def draw_unfilled_triangle(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, outline_color: ND_Color) -> None:
        #
        return

    #
    def draw_filled_triangle(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, fill_color: ND_Color) -> None:
        #
        return

    #
    def draw_unfilled_polygon(self, x_coords: list[int], y_coords: list[int], outline_color: ND_Color) -> None:
        #
        return

    #
    def draw_filled_polygon(self, x_coords: list[int], y_coords: list[int], fill_color: ND_Color) -> None:
        #
        return

    #
    def draw_textured_polygon(self, x_coords: list[int], y_coords: list[int], texture_id: int, texture_dx: int = 0, texture_dy: int = 0) -> None:
        #
        return

    #
    def draw_bezier_curve(self, x_coords: list[int], y_coords: list[int], line_color: ND_Color, nb_interpolations: int = 3) -> None:
        #
        return

    #
    def enable_area_drawing_constraints(self, x: int, y: int, width: int, height: int) -> None:
        #
        return

    #
    def disable_area_drawing_constraints(self) -> None:
        #
        return

    #
    def update_display(self) -> None:
        #
        return


#
class ND_EventsManager:
    #
    def __init__(self, main_app: ND_MainApp) -> None:
        #
        self.main_app: ND_MainApp = main_app
        #
        self.keys_pressed: set[str] = set()
        #
        self.events_waiting_too_poll: list[nd_event.ND_Event] = []
        #
        self.mouse_buttons_pressed: set[int] = set()

    #
    def is_shift_pressed(self) -> bool:
        #
        return "left shift" in self.keys_pressed or "right shift" in self.keys_pressed

    #
    def is_ctrl_pressed(self) -> bool:
        #
        return "left ctrl" in self.keys_pressed or "right ctrl" in self.keys_pressed

    #
    def is_alt_pressed(self) -> bool:
        #
        return "left alt" in self.keys_pressed

    #
    def is_alt_gr_pressed(self) -> bool:
        #
        return "right alt" in self.keys_pressed

    #
    def is_key_pressed(self, key_name: str) -> bool:
        return key_name in self.keys_pressed

    #
    def poll_next_event(self) -> Optional[nd_event.ND_Event]:
        return None

    #
    def get_mouse_position(self) -> ND_Point:
        #
        return ND_Point(0, 0)

    #
    def get_global_mouse_position(self) -> ND_Point:
        #
        return ND_Point(0, 0)


#
class ND_Elt:
    #
    def __init__(self, window: ND_Window, elt_id: str, position: ND_Position):
        #
        self.window: ND_Window = window
        #
        self.elt_id: str = elt_id
        #
        self.position: ND_Position = position
        #
        self._visible: bool = True
        self.clickable: bool = True
        #
        self.transformations: ND_Transformation = ND_Transformation()

    #
    @property
    def visible(self) -> bool:
        #
        return self._visible and self.position.visible

    #
    @visible.setter
    def visible(self, new_visible: bool) -> None:
        self._visible = new_visible

    #
    def get_value(self) -> Any:
        #
        return None

    #
    def set_value(self, new_value: Any) -> None:
        #
        pass

    #
    def get_element_recursively_from_subchild(self, elt_id: str) -> Optional["ND_Elt"]:
        #
        return None

    #
    def render(self) -> None:
        # Abstract class, so do nothing
        return

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        # Abstract class, so do nothing
        return

    #
    @property
    def x(self) -> int:
        #
        if not self.position:
            return 0
        #
        return self.position.x

    #
    @property
    def y(self) -> int:
        #
        if not self.position:
            return 0
        #
        return self.position.y

    #
    @property
    def w(self) -> int:
        #
        if not self.position:
            return 0
        #
        if self.min_w > 0 and self.position.w < self.min_w:
            return self.min_w
        #
        if self.max_w > 0 and self.position.w > self.max_w:
            return self.max_w
        #
        return self.position.w

    #
    @property
    def h(self) -> int:
        #
        if not self.position:
            return 0
        #
        if self.min_h > 0 and self.position.h < self.min_h:
            return self.min_h
        #
        if self.max_h > 0 and self.position.h > self.max_h:
            return self.max_h
        #
        return self.position.h

    #
    @property
    def min_w(self) -> int:
        #
        if not self.position:
            return 0
        #
        return self.position.get_min_width()

    #
    @property
    def max_w(self) -> int:
        #
        if not self.position:
            return 0
        #
        return self.position.get_max_width()

    #
    @property
    def min_h(self) -> int:
        #
        if not self.position:
            return 0
        #
        return self.position.get_max_height()

    #
    @property
    def max_h(self) -> int:
        #
        if not self.position:
            return 0
        #
        return self.position.get_max_height()

    #
    def get_margin_left(self, space_left: int = -1) -> int:
        #
        if not self.position:
            return 0
        #
        return self.position.get_margin_left(space_left)

    #
    def get_margin_right(self, space_left: int = -1) -> int:
        #
        if not self.position:
            return 0
        #
        return self.position.get_margin_right(space_left)

    #
    def get_margin_top(self, space_left: int = -1) -> int:
        #
        if not self.position:
            return 0
        #
        return self.position.get_margin_top(space_left)

    #
    def get_margin_bottom(self, space_left: int = -1) -> int:
        #
        if not self.position:
            return 0
        #
        return self.position.get_margin_bottom(space_left)

    #
    def get_width_stretch_ratio(self) -> float:
        #
        if not self.position:
            return 0
        #
        return self.position.get_width_stretch_ratio()

    #
    def get_height_stretch_ratio(self) -> float:
        #
        if not self.position:
            return 0
        #
        return self.position.get_height_stretch_ratio()

    #
    def update_layout(self) -> None:
        #
        pass



#
class ND_Scene:
    #
    def __init__(
                    self,
                    window: ND_Window,
                    scene_id: str,
                    origin: ND_Point,
                    elements_layers: dict[int, dict[str, ND_Elt]] = {},
                    on_window_state: Optional[str | set[str]] = None
    ) -> None:

        # id
        self.scene_id: str = scene_id

        # ND_Scene origin
        self.origin: ND_Point = origin

        #
        self.on_window_state: Optional[str | set[str]] = on_window_state
        self.window: ND_Window = window
        self.on_window_state_test: Optional[Callable[[Optional[str]], bool]] = None
        #
        if self.on_window_state is not None:
            if isinstance(self.on_window_state, set):
                self.on_window_state_test = self.test_window_state_set
            else:
                self.on_window_state_test = self.test_window_state_str


        # list of elements sorted by render importance with layers (ascending order)
        self.elements_layers: dict[int, dict[str, ND_Elt]] = elements_layers
        self.collisions_layers: dict[int, ND_Quadtree] = {}
        self.elements_by_id: dict[str, ND_Elt] = {}

        #
        for layer in self.elements_layers:
            #
            self.collisions_layers[layer] = ND_Quadtree()
            #
            for element_id in self.elements_layers[layer]:
                #
                if element_id in self.elements_by_id:
                    raise UserWarning(f"Error: at least two elements have the same id: {element_id}!")
                #
                elt: ND_Elt = self.elements_layers[layer][element_id]
                #
                self.elements_by_id[element_id] = elt
                #
                self.collisions_layers[layer].insert(elt.position.rect, element_id)

        #
        self.layers_keys: list[int] = sorted(list(self.elements_layers.keys()))

    #
    def test_window_state_str(self, win_state: Optional[str]) -> bool:
        #
        return win_state != self.on_window_state

    #
    def test_window_state_set(self, win_state: Optional[str]) -> bool:
        #
        return win_state not in cast(set[str], self.on_window_state)

    #
    def handle_event(self, event: nd_event.ND_Event) -> None:
        #
        if event.blocked:
            return
        #
        if self.on_window_state_test is not None and self.on_window_state_test(self.window.state):
            return

        #
        for elt in self.elements_by_id.values():

            #
            if hasattr(elt, "handle_event"):
                #
                elt.handle_event(event)

        # #
        # layer: int
        # for layer in self.layers_keys[::-1]:

        #     elt_list: list[str] = self.collisions_layers[layer].get_colliding_ids( (event.button.x, event.button.y) )

        #     for elt_id in elt_list:
        #         self.elements_by_id[elt_id].handle_event(event)

        #     if len(elt_list) > 0:
        #         return

    #
    def handle_window_resize(self) -> None:
        #
        if self.on_window_state_test is not None and self.on_window_state_test(self.window.state):
            # TODO: Optimisation
            pass

        #
        dict_elt: dict[str, ND_Elt]
        for dict_elt in self.elements_layers.values():
            #
            elt: ND_Elt
            for elt in dict_elt.values():
                if hasattr(elt, "update_layout"):
                    elt.update_layout()

    #
    def insert_to_layers_keys(self, layer_key: int) -> None:

        if ( len(self.layers_keys) == 0 ) or ( layer_key > self.layers_keys[-1] ):
            self.layers_keys.append(layer_key)
            return

        # Insertion inside a sorted list by ascendant
        i: int
        k: int
        for i, k in enumerate(self.layers_keys):
            if k > layer_key:
                self.layers_keys.insert(i, layer_key)
                return

    #
    def add_element(self, layer_id: int, elt: ND_Elt) -> None:
        #
        elt_id: str = elt.elt_id

        #
        if elt_id in self.elements_by_id:
            raise UserWarning(f"Error: at least two elements in the scene {self.scene_id} have the same id: {elt_id}!")

        #
        if layer_id not in self.elements_layers:
            self.elements_layers[layer_id] = {}
            self.collisions_layers[layer_id] = ND_Quadtree()
            self.insert_to_layers_keys(layer_id)

        #
        self.elements_layers[layer_id][elt_id] = elt
        self.elements_by_id[elt_id] = elt

        #
        self.collisions_layers[layer_id].insert(elt.position.rect, elt_id)

    #
    def render(self) -> None:
        #
        if self.on_window_state_test is not None and self.on_window_state_test(self.window.state):
            return
        #
        layer_key: int
        for layer_key in self.layers_keys:
            #
            element: ND_Elt
            for element in self.elements_layers[layer_key].values():
                element.render()

