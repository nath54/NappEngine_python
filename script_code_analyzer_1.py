'''
Description: This script analyzes Python files in a directory,
and extracts the dependency graph of the classes between themselves,
and optionally visualizes the dependencies interactively using Plotly with improved layout and styled boxes.

There are three types of dependencies processed here:
- First, the direct inheritance Child Class --[depends on parent]--> Parent Class
- Second, the direct __init__ arguments types dependency
- Third, the indirect __init__ attribute types dependency that are not initialized directly from the __init__ arguments.

Interactive visualization uses different edge styles for each dependency type:
- dependency 1: solid black arrow edge
- dependency 2: dotted blue arrow edge
- dependency 3: dotted light blue arrow edge

Visualization improvements:
- Hierarchical layout based on inheritance depth: root classes at top, children below
- Even horizontal spacing per level
- Node labels rendered as boxed annotations with background and border

Author: Nathan Cerisara (https://github.com/nath54/)

License: MIT
'''

from typing import Optional, Any, Callable, List, Dict, Tuple
import argparse
import ast
import os
import sys
import time

# Optional imports for visualization
try:
    import networkx as nx
    import plotly.graph_objects as go
except ImportError:
    nx = None  # type: ignore
    go = None  # type: ignore

# Define PreProcessType as the AST Module
PreProcessType = ast.Module


def decorator_timer(fn_wrapped: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to measure execution time of a function."""
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time: float = time.time()
        result: Any = fn_wrapped(*args, **kwargs)
        tot_time: float = time.time() - start_time
        name_of_wrapped_function: str = fn_wrapped.__name__
        print(f"Function {name_of_wrapped_function} with the arguments (args={args}, kwargs={kwargs}) took {tot_time:.4f}s to execute.")
        return result
    return wrapper


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Analyze Python files for class dependency graphs.")
    parser.add_argument('--path', type=str, default="./", help='Path to the folder with all the python files.')
    parser.add_argument('--recursive', type=int, choices=[0,1], default=0, help='Whether to search subdirectories recursively (1) or only top-level (0).')
    parser.add_argument('--ignore', type=str, nargs='+', default=[], help="List of file or folder name prefixes to ignore.")
    parser.add_argument('--visualize', action='store_true', help='Whether to show an interactive Plotly graph of dependencies.')
    parser.add_argument('--allow_duplicate_class_names', action='store_true', help='Whether to show an interactive Plotly graph of dependencies.')
    return parser.parse_args()


def get_all_files_to_analyze(args: argparse.Namespace) -> List[str]:
    """Get all Python file paths under the given path, optionally recursively, ignoring specified prefixes and this script file."""
    files_to_analyze: List[str] = []
    base_path: str = os.path.abspath(args.path)
    # Determine the script's own filename to skip
    try:
        script_filename = os.path.basename(__file__)
    except NameError:
        script_filename = os.path.basename(sys.argv[0])

    def should_ignore(name: str) -> bool:
        return any(name.startswith(prefix) for prefix in args.ignore)

    if args.recursive:
        for root, dirs, files in os.walk(base_path):
            # Filter directories to ignore
            dirs[:] = [d for d in dirs if not should_ignore(d)]
            for file in files:
                if not file.endswith('.py'):
                    continue
                if should_ignore(file):
                    continue
                if file == script_filename:
                    continue
                files_to_analyze.append(os.path.join(root, file))
    else:
        try:
            for entry in os.listdir(base_path):
                fullpath = os.path.join(base_path, entry)
                if os.path.isfile(fullpath) and entry.endswith('.py'):
                    if should_ignore(entry):
                        continue
                    if entry == script_filename:
                        continue
                    files_to_analyze.append(fullpath)
        except FileNotFoundError:
            raise FileNotFoundError(f"Path '{base_path}' does not exist.")
    return files_to_analyze


def pre_process_file_content(content: str) -> PreProcessType:
    """Pre-process file content by parsing into an AST."""
    try:
        tree: ast.Module = ast.parse(content)
        return tree
    except SyntaxError as e:
        raise SyntaxError(f"Error parsing content to AST: {e}")


def get_file_class_names(pre_process: PreProcessType) -> List[str]:
    """Extract all class names defined in the AST."""
    class_names: List[str] = []
    for node in ast.walk(pre_process):
        if isinstance(node, ast.ClassDef):
            class_names.append(node.name)
    return class_names


def _extract_annotation_names(node: ast.AST) -> List[str]:
    """Helper to extract type names from annotation AST nodes."""
    names: List[str] = []
    if isinstance(node, ast.Name):
        names.append(node.id)
    elif isinstance(node, ast.Attribute):
        # For attribute like module.ClassName, take ClassName
        names.append(node.attr)
    elif isinstance(node, ast.Subscript):
        # e.g., Optional[Type], List[Type]
        value = node.value
        slice_node = node.slice
        names.extend(_extract_annotation_names(value))
        # For Python 3.9+, slice can be ast.Constant or ast.Index
        if hasattr(ast, 'Index') and isinstance(slice_node, ast.Index):
            sub = slice_node.value
            names.extend(_extract_annotation_names(sub))
        else:
            names.extend(_extract_annotation_names(slice_node))
    elif isinstance(node, (ast.Tuple, ast.List)):
        for elt in node.elts:
            names.extend(_extract_annotation_names(elt))
    return names


def get_file_dependency_1(pre_process: PreProcessType) -> Dict[str, List[str]]:
    """Extract inheritance dependencies: child class -> list of parent class names."""
    dep: Dict[str, List[str]] = {}
    for node in ast.walk(pre_process):
        if isinstance(node, ast.ClassDef):
            child = node.name
            parents: List[str] = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    parents.append(base.id)
                elif isinstance(base, ast.Attribute):
                    parents.append(base.attr)
                # Other base types (e.g., Subscript) are less common for inheritance
            if parents:
                dep[child] = parents
    return dep


def get_file_dependency_2(pre_process: PreProcessType) -> Dict[str, List[str]]:
    """Extract direct __init__ argument type dependencies: class -> list of annotated type names in __init__ parameters."""
    dep: Dict[str, List[str]] = {}
    for node in ast.walk(pre_process):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                    type_names: List[str] = []
                    # Skip 'self', process annotated args
                    for arg in item.args.args[1:]:  # skip self
                        if arg.annotation:
                            extracted = _extract_annotation_names(arg.annotation)
                            type_names.extend(extracted)
                    if type_names:
                        dep[class_name] = list(set(type_names))
    return dep


def get_file_dependency_3(pre_process: PreProcessType) -> Dict[str, List[str]]:
    """Extract indirect __init__ attribute type dependencies: class -> list of instantiated class names in __init__ body, excluding direct assignments from arguments."""
    dep: Dict[str, List[str]] = {}
    for node in ast.walk(pre_process):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                    init_args = {arg.arg for arg in item.args.args[1:]}  # skip self
                    instantiated: List[str] = []
                    for stmt in item.body:
                        # Look for assignments to self attributes
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                    # Skip direct assignment from init args: self.attr = arg
                                    if isinstance(stmt.value, ast.Name) and stmt.value.id in init_args:
                                        continue
                                    # For instantiation: self.attr = SomeClass(...)
                                    if isinstance(stmt.value, ast.Call):
                                        func = stmt.value.func
                                        if isinstance(func, ast.Name):
                                            instantiated.append(func.id)
                                        elif isinstance(func, ast.Attribute):
                                            instantiated.append(func.attr)
                        # Could also handle annotated assignment: self.attr: Type = ... but skipping here
                    if instantiated:
                        dep[class_name] = list(set(instantiated))
    return dep


def _compute_inheritance_levels(dependency_1: Dict[str, List[str]], all_nodes: List[str]) -> Dict[str, int]:
    """Compute inheritance depth levels for each class: roots (no parents in graph) at level 0."""
    # Build parent->children map
    children_map: Dict[str, List[str]] = {}
    parents_map: Dict[str, List[str]] = {}
    for child, parents in dependency_1.items():
        for parent in parents:
            parents_map.setdefault(child, []).append(parent)
            children_map.setdefault(parent, []).append(child)
    # Identify roots: nodes with no parents in inheritance
    levels: Dict[str, int] = {}
    # Classes not in parents_map or with empty parents list
    for node in all_nodes:
        if node not in parents_map:
            levels[node] = 0
    # BFS to assign levels
    queue: List[Tuple[str, int]] = [(node, 0) for node, lvl in levels.items()]
    while queue:
        current, lvl = queue.pop(0)
        # Process children
        for child in children_map.get(current, []):
            new_lvl = lvl + 1
            if child not in levels or new_lvl > levels[child]:
                levels[child] = new_lvl
                queue.append((child, new_lvl))
    # Any nodes not reached (e.g., cycles) assign level 0
    for node in all_nodes:
        levels.setdefault(node, 0)
    return levels


def visualize_dependencies(
    dependency_1: Dict[str, List[str]],
    dependency_2: Dict[str, List[str]],
    dependency_3: Dict[str, List[str]],
    all_class_names: List[str]
) -> None:
    """Visualize class dependencies interactively using Plotly with hierarchical layout and boxed nodes."""
    if nx is None or go is None:
        print("Visualization libraries not installed. Please install networkx and plotly to use visualization.")
        return
    # Create directed graph for dependency edges
    G = nx.DiGraph()
    for cls in all_class_names:
        G.add_node(cls)
    for child, parents in dependency_1.items():
        for parent in parents:
            if parent in G:
                G.add_edge(child, parent, type=1)
    for cls, types in dependency_2.items():
        for t in types:
            if t in G:
                G.add_edge(cls, t, type=2)
    for cls, types in dependency_3.items():
        for t in types:
            if t in G:
                G.add_edge(cls, t, type=3)
    # Compute hierarchical levels based on inheritance only
    levels = _compute_inheritance_levels(dependency_1, all_class_names)
    # Group nodes by level
    level_groups: Dict[int, List[str]] = {}
    for node, lvl in levels.items():
        level_groups.setdefault(lvl, []).append(node)
    # Assign positions: for each level, spread nodes horizontally
    pos: Dict[str, Tuple[float, float]] = {}
    max_width = 1.0
    # Determine y spacing: level 0 at y=0, level increases downward
    for lvl, nodes in sorted(level_groups.items()):
        count = len(nodes)
        if count == 0:
            continue
        # Evenly spaced x positions between 0 and max_width
        for idx, node in enumerate(sorted(nodes)):
            x = (idx + 1) / (count + 1)
            y = -lvl  # downward
            pos[node] = (x, y)
    # Prepare Plotly figure
    fig = go.Figure()
    # Draw edges: lines and arrows
    style_map = {
        1: {'color': 'black', 'dash': 'solid'},
        2: {'color': 'blue', 'dash': 'dot'},
        3: {'color': 'lightblue', 'dash': 'dot'}
    }
    # For each edge, draw line and arrow
    for u, v, data in G.edges(data=True):
        if u in pos and v in pos:
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            style = style_map.get(data.get('type'), {'color': 'gray', 'dash': 'dash'})
            # Line segment
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode='lines',
                line=dict(color=style['color'], width=1.5, dash=style['dash']),
                hoverinfo='none',
                showlegend=False
            ))
            # Arrow annotation
            fig.add_annotation(
                x=x1, y=y1, ax=x0, ay=y0,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowcolor=style['color'],
                standoff=4
            )
    # Draw nodes as boxed annotations
    for node, (x, y) in pos.items():
        fig.add_annotation(
            x=x, y=y,
            text=node,
            showarrow=False,
            font=dict(color='black'),
            bgcolor='lightgrey',
            bordercolor='black',
            borderwidth=1,
            align='center',
            xanchor='center',
            yanchor='middle'
        )
    # Layout adjustments
    fig.update_layout(
        title='Class Dependency Graph',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='white',
        hovermode='closest'
    )
    fig.show(renderer="browser")

@decorator_timer
def main(args: argparse.Namespace) -> None:
    """Main function to orchestrate analysis, display results, and optionally visualize."""
    files_to_analyze = get_all_files_to_analyze(args=args)
    all_class_names_map: Dict[str, str] = {}
    dependency_1_direct_child: Dict[str, List[str]] = {}
    dependency_2_argument_type: Dict[str, List[str]] = {}
    dependency_3_attribute_type: Dict[str, List[str]] = {}

    for file_to_analyze in files_to_analyze:
        with open(file=file_to_analyze, mode="r", encoding="utf-8") as f:
            content: str = f.read()
        pre_process = pre_process_file_content(content=content)
        class_names_in_file = get_file_class_names(pre_process=pre_process)
        dependency_1_in_file = get_file_dependency_1(pre_process=pre_process)
        dependency_2_in_file = get_file_dependency_2(pre_process=pre_process)
        dependency_3_in_file = get_file_dependency_3(pre_process=pre_process)
        for new_class_name in class_names_in_file:
            if new_class_name in all_class_names_map and not args.allow_duplicate_class_names:
                raise UserWarning(f"Error: detected duplicate class names: `{new_class_name}` in {file_to_analyze} and {all_class_names_map[new_class_name]}!")
            all_class_names_map[new_class_name] = file_to_analyze
        # Merge dependencies
        for k, v in dependency_1_in_file.items():
            dependency_1_direct_child.setdefault(k, []).extend(v)
        for k, v in dependency_2_in_file.items():
            dependency_2_argument_type.setdefault(k, []).extend(v)
        for k, v in dependency_3_in_file.items():
            dependency_3_attribute_type.setdefault(k, []).extend(v)

    # Deduplicate dependency lists
    for dep_dict in (dependency_1_direct_child, dependency_2_argument_type, dependency_3_attribute_type):
        for cls, lst in dep_dict.items():
            dep_dict[cls] = list(set(lst))

    # Prepare result text
    lines: List[str] = []
    lines.append("Classes found and their file locations:")
    for cls, filepath in all_class_names_map.items():
        lines.append(f"- {cls}: {filepath}")
    lines.append("\nInheritance dependencies (Child -> Parents):")
    if dependency_1_direct_child:
        for child, parents in dependency_1_direct_child.items():
            lines.append(f"- {child} -> {', '.join(parents)}")
    else:
        lines.append("- None detected.")
    lines.append("\nDirect __init__ argument type dependencies (Class -> Types):")
    if dependency_2_argument_type:
        for cls, types in dependency_2_argument_type.items():
            lines.append(f"- {cls} -> {', '.join(types)}")
    else:
        lines.append("- None detected.")
    lines.append("\nIndirect __init__ attribute instantiation dependencies (Class -> Types):")
    if dependency_3_attribute_type:
        for cls, types in dependency_3_attribute_type.items():
            lines.append(f"- {cls} -> {', '.join(types)}")
    else:
        lines.append("- None detected.")
    res_txt = "\n".join(lines)
    print(res_txt)

    # Visualization if requested
    if args.visualize:
        all_classes_list = sorted(all_class_names_map.keys())
        visualize_dependencies(
            dependency_1=dependency_1_direct_child,
            dependency_2=dependency_2_argument_type,
            dependency_3=dependency_3_attribute_type,
            all_class_names=all_classes_list
        )

if __name__ == "__main__":
    args = parse_args()
    main(args=args)
    print("\nEnd of program.\n")
