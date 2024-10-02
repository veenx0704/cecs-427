# Assignment 2 (Due October 3th)

I am on **Mac OS** so please adjust your commands accordingly.

## 1. Locate the .py file:

Use your local terminal and locate .py directories.
\
I put mine in my Documents/427/prog2/graph_analysis.py:

```bash
cd Documents
cd 427
cd prog2
```

## 2. Sample Commands:

Read graph_file.gml and partition it into 3 connected components, plot the graph and highlight the clustering coefficient, and save the graph in out_graph_file.gml:
```python
python3 ./graph_analysis.py graph_file.gml --components 3 --plot C --output out_graph_file.gml
```

Read homophily.gml, plot the graph and verify if there is evidence of homophily in the graph:
```python
python3 ./graph_analysis.py homophily.gml --plot P --verify_homophily
```

Read balanced_graph.gml, plot the graph and verify if there is the graph is balanced:
```python
python3 ./graph_analysis.py balanced_graph.gml --plot P --verify_balanced_graph
```
## 3. Command-Line Arguments:

**`input_graph_file`**: (Required) Specifies the input graph file in GML format.
**`--components`**: Defines the number of components to partition the graph.

- **`--plot`**: Specifies the type of plot to generate:
  - `C`: Clustering plot
  - `N`: Neighborhood plot
  - `P`: Attribute-based plot

- **`--verify_homophily`**: Verifies if the graph exhibits homophily (the tendency of nodes with similar attributes to connect).

- **`--verify_balanced_graph`**: Checks if the graph is balanced based on edge signs.

- **`--verify_balanced_by_attributes`**: Verifies if the graph is balanced considering both edge signs and node attributes.

- **`--attribute`**: Specifies a node attribute (e.g., `color`) to check for balance when using the `--verify_balanced_by_attributes` option.

- **`--output`**: Specifies the filename to save the output graph in GML format.

## Note:
Please zoom in the graph, they may look overlapped but they are not:)
