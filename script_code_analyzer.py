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
from typing import Any, Callable
#
import argparse
import ast
import os
import sys
import time


### Decorator to analyze time of function when called. ###
#
def decorator_timer(fn_wrapped: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to measure execution time of a function.

    Args:
        fn_wrapped (Callable[..., Any]): Function to wrap and analyze time.

    Returns:
        Callable[..., Any]: Returns the wrapped function with the decorator.
    """

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
    parser.add_argument('--allow_duplicate_class_names', action="store_true", help="Allow duplicate class names instead of raising an error. But display a warning nevertheless.")
    #
    ### Return parsed arguments ###
    #
    return parser.parse_args()


#
### Function to get the list of file paths to analyze. ###
#
@decorator_timer
def get_all_files_to_analyze(args: argparse.Namespace) -> list[str]:
    """
    Get all Python file paths under the given path, optionally recursively, ignoring specified prefixes and this script file.

    Args:
        args (argparse.Namespace): Arguments given by the user to the program.

    Raises:
        FileNotFoundError: Error if the given path to list the files at doesn't exists.

    Returns:
        list[str]: The list of all the files to analyze (with their absolute full path each).
    """

    #
    ### Initialize empty container for all the files to analyze result. ###
    #
    files_to_analyze: list[str] = []

    #
    ### Calculate the absolute path from the arguments path of the folder to explore. ###
    #
    base_path: str = os.path.abspath(args.path)

    #
    ### Determine the script's own filename to skip. ###
    #
    try:
        #
        script_filename = os.path.basename(__file__)
    #
    except NameError:
        #
        script_filename = os.path.basename(sys.argv[0])

    #
    ### Prepare function to filter file names to ignore. ###
    #
    def should_ignore(name: str) -> bool:
        #
        return any(name.startswith(prefix) for prefix in args.ignore)

    #
    ### If recursive exploration. ###
    #
    if args.recursive:

        #
        ###
        #
        for root, dirs, files in os.walk(base_path):

            #
            ### Filter directories to ignore. ###
            #
            dirs[:] = [d for d in dirs if not should_ignore(d)]

            #
            ### Explore all the files. ###
            #
            for file in files:

                #
                ### Filter files that are not python files. ###
                #
                if not file.endswith('.py'):
                    #
                    continue

                #
                ### Filter files that asked to avoid. ###
                #
                if should_ignore(file):
                    #
                    continue

                #
                ### Filter this script file. ###
                #
                if file == script_filename:
                    #
                    continue

                #
                ### Add the file to the result list if it passed the filters. ###
                #
                files_to_analyze.append(os.path.join(root, file))

    #
    ### Non recursive file listing. ###
    #
    else:

        #
        try:

            #
            ### For all the files in the asked folded. ###
            #
            for entry in os.listdir(base_path):

                #
                ### Create the full path by joining the folder with the file name. ###
                #
                fullpath = os.path.join(base_path, entry)

                #
                ### Filter with files, and ensure they are python files. ###
                #
                if os.path.isfile(fullpath) and entry.endswith('.py'):

                    #
                    ### Filter files that asked to avoid. ###
                    #
                    if should_ignore(entry):
                        #
                        continue

                    #
                    ### Filter this script file. ###
                    #
                    if entry == script_filename:
                        #
                        continue

                    #
                    ### Add the file to the result list if it passed the filters. ###
                    #
                    files_to_analyze.append(fullpath)

        #
        ### Raise error if path doesn't exists. ###
        #
        except FileNotFoundError:
            #
            raise FileNotFoundError(f"Path '{base_path}' does not exist.")

    #
    ### Return the final results of all the files that will be analyzed. ###
    #
    return files_to_analyze


#
### Function that pre-process the file content to analyze. ###
#
def pre_process_file_content(content: str) -> ast.Module:
    """
    Pre-process file content by parsing into an AST.

    Args:
        content (str): Python text code content to analyze.

    Raises:
        SyntaxError: If the python code has a syntax error, raise it.

    Returns:
        ast.Module: Returns the Abstract Syntax Tree.
    """

    #
    try:

        #
        ### Parse the python file content and extract its Abstract Syntax Tree. ###
        #
        tree: ast.Module = ast.parse(content)

        #
        ### Return the final parsed Abstract Syntax Tree. ###
        #
        return tree

    #
    ### Raise error if there was an error during parsing. ###
    #
    except SyntaxError as e:
        #
        raise SyntaxError(f"Error parsing content to AST: {e}")


#
### Function that extract all the class name from pre-processed content. ###
#
def get_file_class_names(pre_process: ast.Module) -> list[str]:
    """
    Extract all class names defined in the AST.

    Args:
        pre_process (ast.Module): The pre-processed Astract Syntax Tree.

    Returns:
        list[str]: The list of all the classes that were defined in this file python code.
    """

    #
    ### Init file classes names. ###
    #
    class_names_in_file: list[str] = []

    #
    ### Explore all the nodes in the AST. ###
    #
    for node in ast.walk(pre_process):
        #
        ### If the node is a class definition. ###
        #
        if isinstance(node, ast.ClassDef):
            #
            ### Extract the node name. ###
            #
            class_names_in_file.append(node.name)

    #
    ### Return file class names. ###
    #
    return class_names_in_file


#
### Helper function to extract recursively the type names from AST Annotations. ###
#
def _extract_annotation_names(node: ast.AST) -> list[str]:
    """
    Helper to extract type names from annotation AST nodes.

    Args:
        node (ast.AST): annotation ast node to extract types from.

    Returns:
        list[str]: List of classes from given annotation ast node.
    """

    #
    ### Initialize the list of all the type names from this annotation. ###
    #
    names: list[str] = []

    #
    ### If it is directly a non recursive type name. ###
    #
    if isinstance(node, ast.Name):
        names.append(node.id)

    #
    ### If it is directly another non recursive type name. ###
    #
    elif isinstance(node, ast.Attribute):
        #
        ### For attribute like module.ClassName, take ClassName. ###
        #
        names.append(node.attr)

    #
    ### If it is a recursive type name. ###
    #
    elif isinstance(node, ast.Subscript):
        #
        ### e.g., Optional[Type], List[Type], ... ###
        #
        value: ast.expr = node.value
        slice_node: ast.expr = node.slice
        #
        names.extend(_extract_annotation_names(value))

        #
        ### For Python 3.9+, slice can be ast.Constant or ast.Index ###
        #
        if hasattr(ast, 'Index') and isinstance(slice_node, ast.Index):  # type: ignore
            #
            sub: ast.AST = slice_node.value  # type: ignore
            #
            names.extend(_extract_annotation_names(sub))  # type: ignore
        #
        else:
            #
            names.extend(_extract_annotation_names(slice_node))

    #
    ### If it is an iterable of types names. ###
    #
    elif isinstance(node, (ast.Tuple, ast.List)):
        #
        for elt in node.elts:
            #
            names.extend(_extract_annotation_names(elt))

    #
    ### Return the final types from this type annotation node. ###
    #
    return names


#
### Function that extract all the depencies of rank 1 from pre-processed content. ###
#
def get_file_dependency_1(pre_process: ast.Module) -> dict[str, list[str]]:
    """
    Extract inheritance dependencies: child class -> list of parent class names.

    Args:
        pre_process (ast.Module): The pre-processed Astract Syntax Tree.

    Returns:
        dict[str, list[str]]: Dependency of rank 1 graph.
    """

    #
    ### Init file dependencies of rank 1. ###
    #
    dependency_1_in_file: dict[str, list[str]] = {}

    #
    ### Explore all the nodes of the AST. ###
    #
    for node in ast.walk(pre_process):

        #
        ### If the node is a Class Definition. ###
        #
        if isinstance(node, ast.ClassDef):

            #
            ### Get the defined child class name. ###
            #
            child = node.name

            #
            ### Initialize the list of all the parent class this child inherits from. ###
            #
            parents: list[str] = []

            #
            ### Explore all the class names betweens the parenthesis of class def. ###
            #
            for base in node.bases:

                #
                if isinstance(base, ast.Name):
                    #
                    parents.append(base.id)
                #
                elif isinstance(base, ast.Attribute):
                    #
                    parents.append(base.attr)

                # Other base types (e.g., Subscript) are less common for inheritance

            #
            if parents:
                #
                dependency_1_in_file[child] = parents

    #
    ### Return file dependencies of rank 1. ###
    #
    return dependency_1_in_file


#
### Function that extract all the depencies of rank 2 from pre-processed content. ###
#
def get_file_dependency_2(pre_process: ast.Module) -> dict[str, list[str]]:
    """
    Extract direct class functions argument type dependencies: class -> list of annotated type names in functions parameters.

    Args:
        pre_process (ast.Module): The pre-processed Astract Syntax Tree.

    Returns:
        dict[str, list[str]]: Dependency of rank 2 graph.
    """

    #
    ### Init file dependencies of rank 2. ###
    #
    dependency_2_in_file: dict[str, list[str]] = {}

    #
    ### Explore all the nodes of the AST. ###
    #
    for node in ast.walk(pre_process):

        #
        ### If the node is a class definition. ###
        #
        if isinstance(node, ast.ClassDef):

            #
            ### Get the name of the class. ###
            #
            class_name = node.name

            #
            ### Explore all the elements of the class. ###
            #
            for item in node.body:

                #
                ### Explore only the functions. ###
                #
                if isinstance(item, ast.FunctionDef):

                    #
                    ### Initialize the type names list. ###
                    #
                    type_names: list[str] = []

                    #
                    ### Skip 'self', and process function arguments. ###
                    #
                    for arg in item.args.args[1:]:

                        #
                        ### Check if argument has type hint. ###
                        #
                        if arg.annotation:
                            #
                            extracted = _extract_annotation_names(arg.annotation)
                            #
                            type_names.extend(extracted)

                    #
                    ### If type names where found, add them to the dependency list. ###
                    #
                    if type_names:
                        #
                        if class_name not in dependency_2_in_file:
                            #
                            dependency_2_in_file[class_name] = []
                        #
                        dependency_2_in_file[class_name].extend( type_names )
                        #
                        dependency_2_in_file[class_name] = list( set(dependency_2_in_file[class_name]) )

    #
    ### Return file dependencies of rank 2. ###
    #
    return dependency_2_in_file


#
### Function that extract all the depencies of rank 3 from pre-processed content. ###
#
def get_file_dependency_3(pre_process: ast.Module) -> dict[str, list[str]]:
    """
    Extract indirect class functions attribute type dependencies: class -> list of instantiated class names in function body, excluding direct assignments from arguments.

    Args:
        pre_process (ast.Module): The pre-processed Astract Syntax Tree.

    Returns:
        dict[str, list[str]]: Dependency of rank 3 graph.
    """

    #
    ### Init file dependencies of rank 3. ###
    #
    dependency_3_in_file: dict[str, list[str]] = {}

    #
    ### Process all the nodes of the AST. ###
    #
    for node in ast.walk(pre_process):

        #
        ### If the node is a class definition. ###
        #
        if isinstance(node, ast.ClassDef):

            #
            ### Get the class name. ###
            #
            class_name = node.name

            #
            ### Explore all the elements of the class. ###
            #
            for item in node.body:

                #
                ### If the element is a function definition. ###
                #
                if isinstance(item, ast.FunctionDef):

                    #
                    ### Get all the function arguments. ###
                    #
                    init_args = {arg.arg for arg in item.args.args[1:]}  # skip self

                    #
                    ### Initialize the list of all the instiantiated variables that are not from function arguments. ###
                    #
                    instantiated: list[str] = []

                    #
                    ### Explore all the elements of the function. ###
                    #
                    for stmt in item.body:

                        #
                        ### Look for assignments ###
                        #
                        if isinstance(stmt, ast.Assign):

                            #
                            ### Explore all the targets of the assignment. ###
                            #
                            for target in stmt.targets:

                                #
                                ### Skip direct assignment from init args: self.attr = arg. ###
                                #
                                if isinstance(stmt.value, ast.Name) and stmt.value.id in init_args:
                                    #
                                    continue

                                #
                                ### For instantiation: self.attr = SomeClass(...) ###
                                #
                                if isinstance(stmt.value, ast.Call):
                                    #
                                    func = stmt.value.func
                                    #
                                    if isinstance(func, ast.Name):
                                        #
                                        instantiated.append(func.id)
                                    #
                                    elif isinstance(func, ast.Attribute):
                                        #
                                        instantiated.append(func.attr)

                        # Could also handle annotated assignment: self.attr: Type = ... but skipping here

                    #
                    ### Add all the types found to the final dictionary result. ###
                    #
                    if instantiated:
                        #
                        if class_name not in dependency_3_in_file:
                            #
                            dependency_3_in_file[class_name] = []
                        #
                        dependency_3_in_file[class_name].extend( instantiated )
                        #
                        dependency_3_in_file[class_name] = list( set(dependency_3_in_file[class_name]) )

    #
    ### Return file dependencies of rank 3. ###
    #
    return dependency_3_in_file


#
### Main Function. ###
#
@decorator_timer
def main(args: argparse.Namespace) -> None:
    """
    Main function to orchestrate analysis, display results, and optionally visualize.

    Args:
        args (argparse.Namespace): Parsed command lines arguments of this script.

    Raises:
        UserWarning: Error if duplicate class names.
    """

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
                if args.allow_duplicate_class_names:
                    #
                    print(f"\nWARNING: Duplicate class name detected: `{new_class_name}` !")
                #
                else:
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
    ### Creating inverse class names dictionary. ###
    #
    inverse_class_dict: dict[str, list[str]] = {}
    #
    class_name: str
    file_name: str
    #
    for class_name, file_name in all_class_names.items():
        #
        if file_name not in inverse_class_dict:
            #
            inverse_class_dict[file_name] = []
        #
        inverse_class_dict[file_name].append( class_name )

    #
    ### Filtering everything here. ###
    #
    for class_name in dependency_1_direct_child:
        #
        dependency_1_direct_child[class_name] = [t for t in dependency_1_direct_child[class_name] if t in all_class_names]
    #
    for class_name in dependency_2_argument_type:
        #
        dependency_2_argument_type[class_name] = [t for t in dependency_2_argument_type[class_name] if t in all_class_names]
    #
    for class_name in dependency_3_attribute_type:
        #
        dependency_3_attribute_type[class_name] = [t for t in dependency_3_attribute_type[class_name] if t in all_class_names]

    #
    dependency_1_direct_child = {k: v for k, v in dependency_1_direct_child.items() if v}
    dependency_2_argument_type = {k: v for k, v in dependency_2_argument_type.items() if v}
    dependency_3_attribute_type = {k: v for k, v in dependency_3_attribute_type.items() if v}

    #
    ### End of analyzis, display the results. ###
    #
    res_txt: str = ""

    #
    ### Prepare result text. ###
    #
    lines: list[str] = []

    #
    lines.append("\nClasses found and their file locations:")
    #
    for fn, cls in inverse_class_dict.items():
        #
        lines.append(f"\n- {fn}:\n\t * {'\n\t * '.join(cls)}\n")

    #
    lines.append("\nInheritance dependencies (Child -> Parents):")
    #
    if dependency_1_direct_child:
        #
        for child, parents in dependency_1_direct_child.items():
            #
            lines.append(f"\n- {child}:\n\t * {'\n\t * '.join(parents)}\n")
    #
    else:
        #
        lines.append("- None detected.")

    #
    lines.append("\nDirect __init__ argument type dependencies (Class -> Types):")
    #
    if dependency_2_argument_type:
        #
        for cls, types in dependency_2_argument_type.items():
            #
            lines.append(f"\n- {cls}:\n\t * {'\n\t * '.join(types)}\n")
    #
    else:
        #
        lines.append("- None detected.")

    #
    lines.append("\nIndirect __init__ attribute instantiation dependencies (Class -> Types):")
    #
    if dependency_3_attribute_type:
        #
        for cls, types in dependency_3_attribute_type.items():
            #
            lines.append(f"\n- {cls}:\n\t * {'\n\t * '.join(types)}\n")
    #
    else:
        #
        lines.append("- None detected.")

    #
    res_txt = "\n".join(lines)

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
