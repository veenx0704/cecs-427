import argparse
import networkx as nx
import matplotlib.pyplot as plt

def is_graph_balanced(graph):
    for cycle in nx.simple_cycles(graph):
        if len(cycle) % 2 == 1:  # Check for odd-length cycles
            negative_edges = sum(1 for u, v in zip(cycle, cycle[1:] + cycle[:1])
                                  if graph[u][v].get('sign', 1) == -1)
            if negative_edges % 2 == 1:
                return False
    return True

def is_graph_balanced_by_attributes(graph, attribute):

    for u, v, data in graph.edges(data=True):
        # Check if both nodes have the attribute
        if attribute in graph.nodes[u] and attribute in graph.nodes[v]:
            node_u_attr = graph.nodes[u][attribute]
            node_v_attr = graph.nodes[v][attribute]
            
            # If nodes have the same attribute, the edge should be positive
            if node_u_attr == node_v_attr:
                if data.get('sign', 1) != 1:
                    print(f"Unbalanced edge between nodes {u} and {v}: same attribute but negative sign")
                    return False
            
            # If nodes have different attributes, the edge should be negative
            else:
                if data.get('sign', 1) != -1:
                    print(f"Unbalanced edge between nodes {u} and {v}: different attributes but positive sign")
                    return False
        else:
            print(f"Nodes {u} or {v} are missing the attribute '{attribute}'")
            return False

    return True


def main():
    parser = argparse.ArgumentParser(description='Graph Analysis Tool')
    parser.add_argument('input_graph_file', help='Input graph file in GML format')
    parser.add_argument('--components', type=int, help='Number of components to partition the graph')
    parser.add_argument('--plot', choices=['C', 'N', 'P'],
                        help='Plot type (C: clustering, N: neighborhood, P: attributes)')
    parser.add_argument('--verify_homophily', action='store_true', help='Verify homophily in the graph')
    parser.add_argument('--verify_balanced_graph', action='store_true', help='python3 ./graph_analysis.py homophily.gml --verify_homophily --plot N if the graph is balanced')
    parser.add_argument('--verify_balanced_by_attributes', action='store_true',
                        help='Check if the graph is balanced based on edge signs and node attributes')
    parser.add_argument('--attribute', help='Node attribute to check for balance (e.g., color)')
    parser.add_argument('--output', help='Output graph file in GML format')

    args = parser.parse_args()

    graph = nx.read_gml(args.input_graph_file)
    print(f"Graph loaded with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")

    # Assign signs to edges based on 'color' attribute
    for u, v, data in graph.edges(data=True):
        data['sign'] = -1 if data.get('color') == 'r' else 1

    if args.verify_homophily:
        """Tests for homophily in the graph based on the assigned node colors."""
        homophily_graph = nx.read_gml('homophily.gml')
        color_map = {node: data['color'] for node, data in homophily_graph.nodes(data=True)}

        same_color_edges = 0
        different_color_edges = 0

        for u, v in graph.edges():
            if color_map[u] == color_map[v]:
                same_color_edges += 1
            else:
                different_color_edges += 1

        total_edges = same_color_edges + different_color_edges
        print(
            f"Same-color edges: {same_color_edges}, Different-color edges: {different_color_edges}, Total edges: {total_edges}")

        if total_edges > 0:
            proportion_same_color = same_color_edges / total_edges
            print(f"Proportion of same-color edges: {proportion_same_color:.2f}")

            # Count the number of nodes for each color
            color_count = {}
            for color in color_map.values():
                color_count[color] = color_count.get(color, 0) + 1

            # Calculate the expected number of same-color edges
            expected_same_color = 0
            for count in color_count.values():
                expected_same_color += count * (count - 1) / 2  # Combination of choosing 2 nodes from `count`

            expected_same_color /= (total_edges if total_edges > 0 else 1)  # Normalize by total edges if necessary
            print(f"Expected same-color edges if random: {expected_same_color:.2f}")

            # Compare the observed with the expected
            if same_color_edges > expected_same_color:
                print("There is a significant homophily effect.")
            else:
                print("No significant homophily effect found.")
        else:
            print("No edges in the graph; cannot determine homophily.")
            
    if args.verify_balanced_graph:
        """Verify if the graph is balanced"""
        is_balanced = is_graph_balanced(graph)
        if is_balanced:
            print("The graph is balanced.")
        else:
            print("The graph is not balanced.")

    if args.verify_balanced_by_attributes:
        """Verify if the graph is balanced based on node attributes and edge signs"""
        if args.attribute:
            is_balanced_by_attributes = is_graph_balanced_by_attributes(graph, args.attribute)
            if is_balanced_by_attributes:
                print(f"The graph is balanced based on the attribute '{args.attribute}'.")
            else:
                print(f"The graph is not balanced based on the attribute '{args.attribute}'.")
        else:
            print("Please specify the node attribute to check for balance using --attribute.")

    if args.components:
        """Graph should be partitioned into n components.
         Divides the graph into n subgraphs"""
        while True:
            # Compute edge betweenness centrality
            edge_betweenness = nx.edge_betweenness_centrality(graph)
            # Identify the edge with the highest betweenness centrality
            highest_edge = max(edge_betweenness, key=edge_betweenness.get)

            # Remove the edge from the graph
            graph.remove_edge(*highest_edge)
            print(f"Removed edge: {highest_edge} with betweenness {edge_betweenness[highest_edge]}")

            # Check the number of components
            components = list(nx.connected_components(graph))
            num_components = len(components)

            print(f"Current number of components: {num_components}")

            # If the desired number of components is reached, break
            if num_components >= args.components:
                break

    if args.plot == 'C':
        """Cluster Coefficient is proportional to its size
            cluster_min = min, cluster_max = max coefficients, c_v = (c_v - cluster_min) / (cluster_max - cluster_min) of node v"""
        clusterCoefficients = nx.clustering(graph)
        cluster_min = min(clusterCoefficients.values())
        cluster_max = max(clusterCoefficients.values())

        min_pixel = 200
        max_pixel = 2000
        sizes = []
        colors = []

        # Maximum degree for color calculation:
        degrees = dict(graph.degree())
        max_degree = max(degrees.values())

        for node in graph.nodes():
            cv = clusterCoefficients[node]
            pv = (cv - cluster_min) / (cluster_max - cluster_min) if cluster_max != cluster_min else 0
            node_size = min_pixel + pv * (max_pixel - min_pixel)
            sizes.append((node_size))

            # Calculate color based on the degree
            dv = degrees[node]
            sv = dv / max_degree if max_degree > 0 else 0
            color = (254 * sv / 255, 0, 254 / 255)
            colors.append(color)

        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, node_size=sizes, node_color=colors, with_labels=True)
        plt.title('Graph with Clustering Coefficients')
        plt.show()

    if args.plot == 'N':
        """Plot the graph highlighting neighborhood overlap"""
        # Calculate neighborhood overlap
        neighborhood_overlap = {}
        for node in graph.nodes():
            neighbors = set(graph.neighbors(node))
            overlap_values = []
            for neighbor in neighbors:
                neighbor_neighbors = set(graph.neighbors(neighbor))
                # Calculate overlap
                overlap = len(neighbors.intersection(neighbor_neighbors))
                total_neighbors = len(neighbors.union(neighbor_neighbors))
                if total_neighbors > 0:
                    overlap_values.append(overlap / total_neighbors)  # Normalize overlap
            neighborhood_overlap[node] = sum(overlap_values) / len(overlap_values) if overlap_values else 0

        # Calculate min and max values for normalization
        overlap_min = min(neighborhood_overlap.values())
        overlap_max = max(neighborhood_overlap.values())
        min_pixel = 200  # Minimum size of nodes
        max_pixel = 2000  # Maximum size of nodes
        sizes = []
        colors = []

        # Determine maximum degree for color calculation
        degrees = dict(graph.degree())
        max_degree = max(degrees.values())

        for node in graph.nodes():
            # Calculate size based on neighborhood overlap
            nv = neighborhood_overlap[node]
            pv = (nv - overlap_min) / (overlap_max - overlap_min) if overlap_max != overlap_min else 0
            node_size = min_pixel + pv * (max_pixel - min_pixel)
            sizes.append(node_size)

            # Calculate color based on degree
            dv = degrees[node]
            sv = dv / max_degree if max_degree > 0 else 0
            color = (254 * sv / 255, 0, 254 / 255)  # Normalize RGB values to [0, 1]
            colors.append(color)

        # Draw the graph with specified sizes and colors
        pos = nx.spring_layout(graph)  # Layout for positioning nodes
        nx.draw(graph, pos, node_size=sizes, node_color=colors, with_labels=True)
        plt.title('Graph with Neighborhood Overlap Highlighted')
        plt.show()

    if args.plot == 'P':
        """Color the node according to the attribute if it's assigned, or a default color if not"""
        # Default color if no attribute is assigned
        default_color = (0.5, 0.5, 0.5)  # Grey

        # List to hold sizes and colors for the nodes
        sizes = []
        colors = []

        # Determine maximum degree for color calculation
        degrees = dict(graph.degree())
        max_degree = max(degrees.values())

        for node in graph.nodes():
            # Determine size based on degree
            node_size = degrees[node] * 100  # Scale size based on degree
            sizes.append(node_size)

            # Determine color based on attribute
            if args.attribute and args.attribute in graph.nodes[node]:
                attr_value = graph.nodes[node][args.attribute]
                color = (attr_value / 255, 0, 1 - (attr_value / 255))  # Normalizing for color range
            else:
                color = default_color  # Assign default color if no attribute
            
            colors.append(color)

        # Draw the graph
        pos = nx.spring_layout(graph)  # Layout for positioning nodes
        nx.draw(graph, pos, node_size=sizes, node_color=colors, with_labels=True)
        plt.title(f'Graph Colored by Attribute: {args.attribute}' if args.attribute else 'Graph with Default Color')
        plt.show()

    # Save the output graph if specified
    if args.output:
        nx.write_gml(graph, args.output)
        print(f"Graph saved to {args.output}.")

if __name__ == '__main__':
    main()
