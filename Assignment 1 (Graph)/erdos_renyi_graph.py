import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import argparse

# Layout settings
DEFAULT_WIDTH = 1        # Default horizontal width of the layout
DEFAULT_VERT_GAP = 1     # Default vertical gap between levels
FIGURE_SIZE = (10, 8)       # Default figure size for plotting
NODE_SIZE = 200            # Default node size
FONT_SIZE = 7               # Default font size for node labels
TITLE_COLOR = '#3b943a'     # Color for the plot title
NODE_COLOR = '#c5f542'      # Node color
EDGE_COLOR = '#000000'      # Edge color

# Make random graph based on equation and save it as gml
def create_random_graph_in_gml(n, c, my_gml):
    p = (c * np.log(n)) / n
    graph = nx.erdos_renyi_graph(n, p)
    if my_gml:
        nx.write_gml(graph, my_gml)
    print(f"Random graph with {n} nodes created and saved to {my_gml}.")

# Function for hierarchical layout positioning
def hierarchy_pos(G, root=None, width=DEFAULT_WIDTH, vert_gap=DEFAULT_VERT_GAP, vert_loc=0, xcenter=0.5):
    pos = _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)
    return pos

def _hierarchy_pos(G, root, width=DEFAULT_WIDTH, vert_gap=DEFAULT_VERT_GAP, vert_loc=0, xcenter=1, pos=None, parent=None):
    if pos is None:
        pos = {root: (xcenter, vert_loc)}
    else:
        pos[root] = (xcenter, vert_loc)
    
    children = list(G.neighbors(root))
    if not isinstance(G, nx.DiGraph) and parent is not None:
        children.remove(parent)  
    
    if len(children) != 0:
        dx = width / len(children) 
        nextx = xcenter - width/2 - dx/2
        for child in children:
            nextx += dx
            pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap, vert_loc=vert_loc-vert_gap, xcenter=nextx, pos=pos, parent=root)
    
    return pos

# Read gml then make BFS then save it as a png
def perform_bfs_with_hierarchy_layout(gml_filename, start_node):
    try:
        graph = nx.read_gml(gml_filename)
    except Exception as e:
        print(f"Error reading GML file: {e}")
        return

    if start_node not in graph.nodes:
        print(f"Start node {start_node} is not in the graph.")
        return

    bfs_tree = nx.bfs_tree(graph, source=start_node)
    num_nodes = len(bfs_tree.nodes)
    vert_gap = max(0.05, 0.5 / (num_nodes ** 0.5))
    width = max(4, num_nodes ** 0.5)

    pos = hierarchy_pos(bfs_tree, root=start_node, vert_gap=vert_gap, width=width)

    plt.figure(figsize=FIGURE_SIZE)
    plt.title('BFS Tree by Taiki Tsukahara', color=TITLE_COLOR)
    nx.draw(
        bfs_tree, pos, with_labels=True, node_size=NODE_SIZE, font_size=FONT_SIZE, font_weight='bold',
        node_color=NODE_COLOR, edge_color=EDGE_COLOR, arrows=True, alpha=0.9
    )
    plt.show()

# Takes command argument to run the application
def main():
    print("\nHello and welcome to BFS Maker....!\n")

    parser = argparse.ArgumentParser(description="For Assignment 1")
    parser.add_argument('--input', type=str, help="Loads GML file for BFS")
    parser.add_argument('--create_random_graph', action='store_true', help="To make random gml graph")
    parser.add_argument('--nodes', type=int, help="Number of nodes for the random graph")
    parser.add_argument('--constant', type=float, help="Constant to determine edge probability for the random graph")
    parser.add_argument('--BFS', type=str, help="Start node for BFS")
    parser.add_argument('--plot', action='store_true', help="To make the BFS graph")
    parser.add_argument('--output', type=str, help="Setting GML file name for the random graph")

    args = parser.parse_args()

    if args.create_random_graph:
        if args.nodes and args.constant and args.output:
            create_random_graph_in_gml(args.nodes, args.constant, args.output)
        else:
            print("Please provide --nodes, --constant, and --output arguments for creating a random graph.")
    
    if args.input and args.BFS and args.plot:
        perform_bfs_with_hierarchy_layout(args.input, args.BFS)
    else:
        return

if __name__ == "__main__":
    main()
