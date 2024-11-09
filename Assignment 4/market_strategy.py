import networkx as nx
import matplotlib.pyplot as plt
import sys
import os


def load_graph(filename):
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist.")
        sys.exit(1)
    try:
        graph = nx.read_gml(filename)
    except Exception as e:
        print(f"Error loading graph: {e}")
        sys.exit(1)
    return graph

def plot_graph(graph, prices, buyer_labels, highlight_edges=None, tie_edges=None, round_number=None, title=None):
    plt.figure(figsize=(12, 8))
    
    # Separate the nodes into markets and buyers based on the bipartite attribute
    markets = [n for n, d in graph.nodes(data=True) if d['bipartite'] == 0]
    buyers = [n for n, d in graph.nodes(data=True) if d['bipartite'] == 1]
    
    # Create positions for markets (left side) and buyers (right side)
    pos = {**{node: (0, -i) for i, node in enumerate(markets)}, 
           **{node: (1, -i) for i, node in enumerate(buyers)}}
    
    # Draw market nodes with orange color
    nx.draw_networkx_nodes(graph, pos, nodelist=markets, node_color='orange', node_size=1500, node_shape='o')
    
    # Draw buyer nodes with light green color
    nx.draw_networkx_nodes(graph, pos, nodelist=buyers, node_color="#D4FF60", node_size=1500, node_shape='o')
    
    # Draw all edges in black
    nx.draw_networkx_edges(graph, pos, edge_color='black')
    
    # Highlight edges selected by each buyer in red
    if highlight_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=highlight_edges, edge_color='red', width=2)
    
    # Highlight tie edges in blue
    if tie_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=tie_edges, edge_color='blue', width=2, style='dashed')
    
    # Add labels to all nodes
    nx.draw_networkx_labels(graph, pos)
    
    # Show prices for market nodes
    for node, (x, y) in pos.items():
        if node in markets:
            price = prices.get(node, 0)
            plt.text(x, y - 0.1, f"Price: {price}", fontsize=10, ha='center')
    
    # Show valuations for buyer nodes
    for node, (x, y) in pos.items():
        if node in buyers:
            plt.text(x, y - 0.1, buyer_labels.get(node, "[]"), fontsize=10, ha='center')
    
    # Set plot title with the current round number or custom title
    if title:
        plt.title(title)
    elif round_number is not None:
        plt.title(f"Round {round_number}: Market vs Buyer")
    
    plt.xlim(-0.5, 1.5)
    plt.axis('off')
    plt.show()


def update_valuations(graph, prices):
    updated_valuations = {}
    for u, v, data in graph.edges(data=True):
        valuation = data['valuation'] - prices[u]
        updated_valuations[(u, v)] = valuation
    return updated_valuations


def highest_valuations(updated_valuations):
    connections = {}
    for (u, v), valuation in updated_valuations.items():
        if v not in connections or valuation > connections[v][1]:
            connections[v] = (u, valuation)
        elif valuation == connections[v][1]:  # Handle ties
            connections[v] = (u, valuation)  # Simplified handling; expand for more complex tie logic if needed
    return connections


def constricted_set(connections):
    counter = {}
    for u, v in connections.values():
        counter[u] = counter.get(u, 0) + 1
    return [u for u, count in counter.items() if count > 1]


def find_perfect_match_round(connections):
    matched_nodes = set()
    for node, (connected_node, _) in connections.items():
        if connected_node not in matched_nodes:
            matched_nodes.add(connected_node)
        else:
            return False
    return True

def detailed_valuations(graph, updated_valuations, prices):
    detailed_list = []
    # Iterate over all buyers (nodes with bipartite=1)
    for v in [n for n, d in graph.nodes(data=True) if d['bipartite'] == 1]:
        adjusted_vals = []
        
        # Calculate the adjusted valuations for each market
        for u in [n for n, d in graph.nodes(data=True) if d['bipartite'] == 0]:
            if (u, v) in updated_valuations:
                valuation = updated_valuations[(u, v)]
                adjusted_vals.append((u, valuation))
            else:
                # If no edge exists, set valuation to 0
                adjusted_vals.append((u, 0))

        # Sort adjusted values by market node for consistent display order
        adjusted_vals.sort(key=lambda x: x[0])
        
        # Find the highest valuation
        highest_market, highest_value = max(adjusted_vals, key=lambda x: x[1])
        detailed_list.append((v, highest_market, highest_value, adjusted_vals))
    
    return detailed_list

def main(filename, plot=False, interactive=False):
    # Load the graph from the provided file
    graph = load_graph(filename)

    # Extract initial prices and buyer labels for the graph
    prices = {node: graph.nodes[node].get('price', 0) for node in graph if graph.nodes[node]['bipartite'] == 0}
    buyer_labels = {
        v: f"[{', '.join(str(graph.edges[(u, v)]['valuation'] - prices[u]) for u, v_ in graph.edges if v_ == v)}]"
        for v in graph if graph.nodes[v]['bipartite'] == 1
    }

    # If only the plot flag is provided, just display the initial graph and exit
    if plot and not interactive:
        plot_graph(graph, prices, buyer_labels, title="Initial Graph")
        return  # Exit after plotting

    round_num = 1
    perfect_match = False

    while not perfect_match:
        print(f"\n---- Round {round_num} ----")

        # Display current prices for nodes in set A
        print("\nCurrent Prices:")
        for node, price in prices.items():
            print(f"Node {node} = {price}")

        # Update valuations
        updated_valuations = update_valuations(graph, prices)

        # Calculate the highest valuations
        connections = highest_valuations(updated_valuations)

        # Extract highest valuation edges for this round
        highlighted_edges = [(str(u), str(v)) for v, (u, _) in connections.items()]

        # Improved Tie Detection
        tie_edges = []
        for buyer in [n for n, d in graph.nodes(data=True) if d['bipartite'] == 1]:
            highest_value = max(
                updated_valuations[(u, buyer)] 
                for u, v in updated_valuations if v == buyer
            )
            for (u, v), valuation in updated_valuations.items():
                if v == buyer and valuation == highest_value and (str(u), str(v)) not in highlighted_edges:
                    tie_edges.append((str(u), str(v)))

        # Prepare buyer labels for the plot
        buyer_labels = {
            v: f"[{', '.join(str(graph.edges[(u, v)]['valuation'] - prices[u]) for u, v_ in graph.edges if v_ == v)}]"
            for v in graph if graph.nodes[v]['bipartite'] == 1
        }

        # Plot during interactive mode only for each round
        if interactive:
            plot_graph(graph, prices, buyer_labels, highlight_edges=highlighted_edges, tie_edges=tie_edges, round_number=round_num)

        # Check for perfect match
        if find_perfect_match_round(connections):
            perfect_match = True
            break  # Exit the loop immediately

        # Identify constricted set and update prices
        nodes_to_increment = constricted_set(connections)
        for node in nodes_to_increment:
            prices[node] += 1

        round_num += 1

    # Print the perfect match results after exiting the loop
    print("\nPerfect match found:")
    final_matching_edges = [(str(u), str(v)) for v, (u, _) in connections.items()]
    for v, (u, _) in connections.items():
        print(f"Node {u} is matched with Node {v}")

    # Plot the final perfect match if in interactive mode only once
    if interactive:
        plot_graph(graph, prices, buyer_labels, highlight_edges=final_matching_edges, 
                   title=f"★★★Perfect Match Found at Round {round_num}★★★")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python market_strategy.py <filename> [--plot] [--interactive]")
        sys.exit(1)

    filename = sys.argv[1]
    plot = "--plot" in sys.argv
    interactive = "--interactive" in sys.argv

    # Ensure that --plot and --interactive do not trigger both behaviors at the same time
    if plot and interactive:
        interactive = True
        plot = False

    main(filename, plot=plot, interactive=interactive)
