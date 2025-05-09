#
import sys
#
import ast
import networkx as nx  # type: ignore
import matplotlib.pyplot as plt # Keep matplotlib for the option, or remove if not needed
import plotly.graph_objects as go  # type: ignore


class CodeAnalyzer(ast.NodeVisitor):
    """
    Analyzes Python code to extract class attributes and dependencies,
    including inheritance relationships, and visualizes using Plotly.
    """
    def __init__(self):
        self.classes = {}  # Stores class attributes: {class_name: {attributes}}
        # Stores dependencies: class_a -> class_b. Edge attributes store the type ('instantiation' or 'inheritance')
        self.dependencies = nx.DiGraph()
        self.current_class = None # To keep track of the class being visited
        self.class_nodes_pos = {} # To store node positions for visualization

    def analyze(self, code):
        """
        Parses the code and starts the AST traversal.

        Args:
            code (str): The Python source code as a string.
        """
        try:
            tree = ast.parse(code)
            self.visit(tree)
            # Generate layout after parsing all classes
            self._generate_layout()
        except SyntaxError as e:
            print(f"Error parsing code: {e}")

    def _generate_layout(self):
        """Generates the layout for graph visualization."""
        if self.dependencies:
            # You can choose different layouts, e.g., nx.circular_layout, nx.shell_layout
            self.class_nodes_pos = nx.spring_layout(self.dependencies)


    def visit_ClassDef(self, node):
        """
        Visits a class definition node. Extracts class name, adds to graph,
        identifies base classes (inheritance dependencies), and visits contents.
        """
        class_name = node.name
        self.classes[class_name] = set()
        self.dependencies.add_node(class_name)

        # Process base classes for inheritance dependencies
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_class_name = base.id
                self.dependencies.add_edge(class_name, base_class_name, type='inheritance')
                # Ensure base class is also a node even if not defined in this code snippet
                if base_class_name not in self.dependencies:
                     self.dependencies.add_node(base_class_name)


        self.current_class = class_name
        self.generic_visit(node) # Continue visiting nodes within the class
        self.current_class = None # Reset current class after visiting


    def visit_Assign(self, node):
        """
        Visits an assignment node to find class and instance attributes.
        """
        if self.current_class:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # Possible class attribute assignment in the class body
                    # Basic check for simple constant assignments
                    if isinstance(node.value, (ast.Constant, ast.Str, ast.Num)):
                         self.classes[self.current_class].add(target.id)
                    # Also consider assignments of lists, dicts, sets, tuples as attributes
                    elif isinstance(node.value, (ast.List, ast.Dict, ast.Set, ast.Tuple)):
                         self.classes[self.current_class].add(target.id)

                elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                    # Instance attribute assignment in a method (e.g., self.attribute = value)
                    self.classes[self.current_class].add(target.attr)

        self.generic_visit(node) # Continue visiting other parts of the assignment

    def visit_Call(self, node):
        """
        Visits a function call node to identify potential dependencies
        (specifically instantiation dependencies in this basic implementation).
        """
        if self.current_class:
            # Check if the call is a method call on an attribute (potential instance interaction)
            if isinstance(node.func, ast.Attribute):
                attribute_name = node.func.attr
                # This is a simplified dependency detection. A more robust
                # analysis would require tracking variable types.
                # Here, we assume if an attribute of 'self' is called,
                # it might be an instance of another class.
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                     # This is a method call on an instance attribute.
                     # We can't definitively know the type of the attribute statically
                     # without more advanced analysis (like type inference).
                     # For a basic graph, we could potentially look for
                     # assignments to this attribute name elsewhere.
                     pass # More advanced dependency detection needed here

            # Check for calls that look like constructor calls (Class()).
            # Again, this is a heuristic and might not be entirely accurate.
            elif isinstance(node.func, ast.Name):
                called_name = node.func.id
                # If the called name is a known class (or likely a class based on naming convention),
                # and it's not the current class, add an instantiation dependency.
                # A more robust check might involve checking if 'called_name' was defined as a class.
                if called_name in self.classes and called_name != self.current_class:
                     self.dependencies.add_edge(self.current_class, called_name, type='instantiation')
                # Basic attempt to detect instantiation of a base class within __init__
                elif isinstance(node.func, ast.Call) and isinstance(node.func.func, ast.Name) and node.func.func.id == 'super':
                     # 'super()' call, implies dependency on parent classes, already covered by inheritance edge.
                     pass # Already handled by inheritance edge


        self.generic_visit(node) # Continue visiting arguments and other parts of the call

    def visit_Attribute(self, node):
        """
        Visits an attribute access node (e.g., instance.attribute).
        More advanced analysis is needed here to determine the type of 'instance'
        and establish dependencies based on attribute access on instances of other classes.
        This basic implementation does not add dependencies solely based on attribute access.
        """
        # if self.current_class:
        #     # Check for attribute access on a name that might be an instance
        #     if isinstance(node.value, ast.Name):
        #         instance_name = node.value.id
        #         accessed_attribute = node.attr
                # To add dependencies here, we'd need to know the type of 'instance_name'.
                # This requires type inference, which is beyond this basic AST traversal.
                # pass # More advanced dependency detection needed here

        self.generic_visit(node) # Continue visiting other parts of the attribute access

    def get_class_attributes(self):
        """
        Returns the extracted class attributes.

        Returns:
            dict: A dictionary where keys are class names and values are sets of attribute names.
        """
        return self.classes

    def get_dependency_graph(self):
        """
        Returns the dependency graph.

        Returns:
            nx.DiGraph: A directed graph representing class dependencies.
        """
        return self.dependencies

    def visualize_dependencies(self):
        """
        Visualizes the dependency graph using Plotly for interactivity.
        """
        if not self.dependencies.edges:
            print("No dependencies found to visualize.")
            return
        if not self.class_nodes_pos:
             print("No layout generated for visualization. Analyze code first.")
             return

        edge_x = []
        edge_y = []
        edge_colors = []
        edge_styles = [] # Plotly uses dash, dot, dashdot for styles
        edge_hover_text = []

        # Define colors and styles for edge types
        edge_style_map = {
            'instantiation': {'color': 'gray', 'dash': 'solid', 'text': 'instantiates'},
            'inheritance': {'color': 'darkgreen', 'dash': 'dot', 'text': ' inherits from'}
        }


        for edge in self.dependencies.edges(data=True):
            x0, y0 = self.class_nodes_pos[edge[0]]
            x1, y1 = self.class_nodes_pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None) # Separator for lines

            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None) # Separator for lines

            edge_type = edge[2].get('type', 'unknown')
            style_info = edge_style_map.get(edge_type, {'color': 'red', 'dash': 'solid', 'text': 'unknown dependency'})

            edge_colors.append(style_info['color'])
            edge_colors.append(style_info['color'])
            edge_colors.append(None)

            edge_styles.append(style_info['dash'])
            edge_styles.append(style_info['dash'])
            edge_styles.append(None)

            edge_hover_text.append(f"{edge[0]} {style_info['text']} {edge[1]}")
            edge_hover_text.append(f"{edge[0]} {style_info['text']} {edge[1]}")
            edge_hover_text.append(None)


        # Create edge trace
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color='gray'), # Default line style, will be overridden by segments
            hoverinfo='text',
            mode='lines')

        # Due to Plotly's handling of line segments and styles in a single trace,
        # creating separate traces for different styles is more reliable.
        edge_traces = []
        for edge_type, style_info in edge_style_map.items():
            type_edges = [(u, v) for u, v, d in self.dependencies.edges(data=True) if d.get('type') == edge_type]
            if not type_edges:
                continue

            type_edge_x = []
            type_edge_y = []
            type_edge_hover_text = []

            for u, v in type_edges:
                 x0, y0 = self.class_nodes_pos[u]
                 x1, y1 = self.class_nodes_pos[v]
                 type_edge_x.extend([x0, x1, None])
                 type_edge_y.extend([y0, y1, None])
                 type_edge_hover_text.extend([f"{u} {style_info['text']} {v}"] * 2 + [None])


            edge_traces.append(go.Scatter(
                x=type_edge_x,
                y=type_edge_y,
                line=dict(width=1.5, color=style_info['color'], dash=style_info['dash']),
                hoverinfo='text',
                mode='lines',
                name=style_info['text'].capitalize() # For legend
            ))


        node_x = []
        node_y = []
        node_text = [] # Text for hover
        node_size = [] # Node size based on attributes count?
        node_color = 'skyblue' # Default node color

        for node in self.dependencies.nodes():
            x, y = self.class_nodes_pos[node]
            node_x.append(x)
            node_y.append(y)
            attributes = self.classes.get(node, set())
            node_text.append(f"Class: {node}<br>Attributes: {', '.join(attributes)}")
            node_size.append(max(10, 5 + len(attributes) * 2)) # Simple sizing based on attribute count


        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                showscale=False,
                colorscale='Blues', # Color scale option
                reversescale=True,
                color=[], # Can color nodes based on some metric
                size=node_size,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    # titleside='right'
                ),
                line=dict(width=2, color='darkslategray')
            ),
            name='Classes'
        )

        fig = go.Figure(data=edge_traces + [node_trace],
                     layout=go.Layout(
                        title='Class Dependency Graph',
                        # titlefont_size=16,
                        showlegend=True, # Show legend for edge types
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[ dict(
                            text="This graph shows class dependencies:<br>- Solid lines: Instantiation<br>- Dotted lines: Inheritance",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002 ) ],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )

        fig.show()


if __name__ == "__main__":

    #
    if len(sys.argv) != 2:
        #
        print(f"Usage: python {sys.argv[0]} <python_file>")
        sys.exit(1)

    #
    try:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            #
            code: str = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {sys.argv[1]}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


    #
    analyzer = CodeAnalyzer()
    analyzer.analyze(code)

    attributes = analyzer.get_class_attributes()
    print("Class Attributes:")
    for class_name, attrs in attributes.items():
        print(f"  {class_name}: {attrs}")

    graph = analyzer.get_dependency_graph()
    print("\nDependency Graph Edges:")
    for u, v, data in graph.edges(data=True):
        print(f"  {u} -> {v} (type: {data.get('type', 'unknown')})")

    # Use Plotly visualization
    analyzer.visualize_dependencies()