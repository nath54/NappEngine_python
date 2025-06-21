"""
Description: This script analyze python files in a directory,
and extract the depency graph of the classes between themselves.

There are three type of dependencies processed here :
- First, the direct inheritance Child Class --[depend of parent]--> Parent Class
- Second, the direct __init__ arguments types dependency
- Third, the indirect __init__ attributes types dependency that are not initialized directly from the __init__ arguments.

Author: Nathan Cerisara (https://github.com/nath54/)

License: MIT
"""

#
### Import modules ###
#
from typing import Optional, Any, Callable
#
import argparse
import ast
import os
import sys
import time
import copy


# TODO: The type of the pre-processed data, set here at Any, but you will have to precise it with what you needed.
PreProcessType = Any


# TODO: clean code AST analyzer class with full typing and commenting.


#
### Decorator to analyze time of function when called. ###
#
def decorator_timer(fn_wrapped: Callable[..., Any]) -> Callable[..., Any]:

    #
    def wrapper(*args: list[Any], **kwargs: dict[str, Any]) -> Any:

        #
        ### Init time of the function. ###
        #
        start_time: float = time.time()

        #
        ### Call the contained function. ###
        #
        result: Any = fn_wrapped(*args, **kwargs)

        #
        ### Calculate & display the execution time of the wrapped function. ###
        #
        tot_time: float = time.time() - start_time
        #
        name_of_wrapped_function: str = fn_wrapped.__name__
        #
        print(f"Function {name_of_wrapped_function} with the arguments (args={args}, kwargs={kwargs}) took {tot_time} to execute.")

        #
        ### Returns the original return value of the wrapped function. ###
        #
        return result

    #
    ### Return the wrapped function. ###
    #
    return wrapper


#
### Function to parse arguments for script. ###
#
def parse_args() -> argparse.Namespace:
    """
    Function to parse arguments for script.

    Returns:
        argparse.Namespace: parsed arguments with default values.
    """

    #
    ### Initialize parser ###
    #
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    #
    parser.add_argument('--path', type=str, default="./", help='Path to the folder with all the python files.')
    parser.add_argument('--recursive', type=int, default=0, help='Path to the folder with all the python files.')
    parser.add_argument('--ignore', type=list[str], default=[], nargs="+", help="List of Files & folder to ignore if they starts like this.")
    #
    ### Return parsed arguments ###
    #
    return parser.parse_args()


#
### Function to get the list of file paths to analyze. ###
#
@decorator_timer
def get_all_files_to_analyze(args: argparse.Namespace) -> list[str]:

    #
    files_to_analyze: list[str] = []

    # TODO: get all the python files paths to analyze from arguments parameters
    # TODO: avoid all the python files with the same name of this script python file. We don't want to analyze THIS file.
    pass

    #
    return files_to_analyze


#
### Function that pre-process the file content to analyze. ###
#
@decorator_timer
def pre_process_file_content(content: str) -> PreProcessType:

    # TODO: do the pre-processing analyzis you want here, maybe use AST here.
    pass


#
### Function that extract all the class name from pre-processed content. ###
#
def get_file_class_names(pre_process: PreProcessType) -> list[str]:

    #
    ### Init file classes names. ###
    #
    class_names_in_file: list[str] = []

    # TODO
    pass

    #
    ### Return file class names. ###
    #
    return class_names_in_file


#
### Function that extract all the depencies of rank 1 from pre-processed content. ###
#
def get_file_dependency_1(pre_process: PreProcessType) -> dict[str, list[str]]:

    #
    ### Init file dependencies of rank 1. ###
    #
    dependency_1_in_file: dict[str, list[str]] = {}

    # TODO
    pass

    #
    ### Return file dependencies of rank 1. ###
    #
    return dependency_1_in_file


#
### Function that extract all the depencies of rank 2 from pre-processed content. ###
#
def get_file_dependency_2(pre_process: PreProcessType) -> dict[str, list[str]]:

    #
    ### Init file dependencies of rank 2. ###
    #
    dependency_2_in_file: dict[str, list[str]] = {}

    # TODO
    pass

    #
    ### Return file dependencies of rank 2. ###
    #
    return dependency_2_in_file


#
### Function that extract all the depencies of rank 3 from pre-processed content. ###
#
def get_file_dependency_3(pre_process: PreProcessType) -> dict[str, list[str]]:

    #
    ### Init file dependencies of rank 3. ###
    #
    dependency_3_in_file: dict[str, list[str]] = {}

    # TODO
    pass

    #
    ### Return file dependencies of rank 3. ###
    #
    return dependency_3_in_file


#
### Main Function. ###
#
@decorator_timer
def main(args: argparse.Namespace) -> None:

    #
    ### Get all the files to analyze. ###
    #
    files_to_analyze: list[str] = get_all_files_to_analyze(args=args)

    #
    ### All the analyzed classes names.
    #   Class names as keys, files where there are as value.
    #   Error if class name already exists. ###
    #
    all_class_names: dict[str, str] = {}

    #
    ### Init the first dependency Graph.
    #   Child class names as keys, Parent class names as values. ###
    #
    dependency_1_direct_child: dict[str, list[str]] = {}

    #
    ### Init the second dependency Graph.
    #   Class names that contains the attribute variable as keys,
    #   The Types class names as values. ###
    #
    dependency_2_argument_type: dict[str, list[str]] = {}

    #
    ### Init the third dependency Graph.
    #   Class names that contains the attribute variable as keys,
    #   The Types class names as values. ###
    #
    dependency_3_attribute_type: dict[str, list[str]] = {}

    #
    ### For all the file to analyze... ###
    #
    file_to_analyze: str
    #
    for file_to_analyze in files_to_analyze:

        #
        ### Read the file content. ###
        #
        with open(file=file_to_analyze, mode="r", encoding="utf-8") as f:
            #
            content: str = f.read()

        #
        ### Content Pre-Processing. ###
        #
        pre_process: Any = pre_process_file_content(content=content)

        #
        ### Extract all the class names. ###
        #
        class_names_in_file: list[str] = get_file_class_names(pre_process=pre_process)

        #
        ### Extract all the depencies of rank 1. ###
        #
        dependency_1_in_file: dict[str, list[str]] = get_file_dependency_1(pre_process=pre_process)

        #
        ### Extract all the depencies of rank 2. ###
        #
        dependency_2_in_file: dict[str, list[str]] = get_file_dependency_2(pre_process=pre_process)

        #
        ### Extract all the depencies of rank 3. ###
        #
        dependency_3_in_file: dict[str, list[str]] = get_file_dependency_3(pre_process=pre_process)

        #
        ### Merge the class names and dependencies. ###
        #
        new_class_name: str
        #
        for new_class_name in class_names_in_file:

            #
            ### Ensure class name doesn't exists. ###
            #
            if new_class_name in all_class_names:

                #
                raise UserWarning(f"Error: detected duplicate class names : `{new_class_name}` !")

            #
            ### Add the new class name to visited classes. ###
            #
            all_class_names[new_class_name] = file_to_analyze

            #
            ### Fusion the dictionnaries. ###
            #
            k: str
            v: list[str]
            #
            for k, v in dependency_1_in_file.items():
                #
                dependency_1_direct_child[k] = v
            #
            for k, v in dependency_2_in_file.items():
                #
                dependency_2_argument_type[k] = v
            #
            for k, v in dependency_3_in_file.items():
                #
                dependency_3_attribute_type[k] = v

    #
    ### End of analyzis, display the results. ###
    #
    res_txt: str = ""

    # TODO

    #
    print(res_txt)


#
### Main Entry Point of the Program. ###
#
if __name__ == "__main__":

    #
    ### Get the command line arguments for the script. ###
    #
    args: argparse.Namespace = parse_args()

    #
    ### Call the Main function. ###
    #
    main(args=args)

    #
    ### End of the program. ###
    #
    print(f"\nEnd of program.\n")
