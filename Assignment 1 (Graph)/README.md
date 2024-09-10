# Assignment 1 (Due Sept 12th)

Note: I am on **Mac OS** so please adjust your commands accordingly.
## Locate the .py file:

Use your local terminal and locate .py directories.
\
I put mine in my Documents/427/prog1/erdos_renyi_graph.py

```bash
cd Documents
cd 427
cd prog1
```

## Sample Commands:

To create Erdős-Rényi graph in .gml file with 10 nodes and an edge probability of (1.1 ln 100) / 10:
```python
python3 ./erdos_renyi_graph.py --create_random_graph --nodes 100 --constant 1.1 --output graph_file.gml
```

To read .gml file and make a BFS graph starting with 1:
```python
python3 ./erdos_renyi_graph.py --input graph_file.gml --BFS 1 --plot 
```

## Command-Line Arguments:

Here's the description of each command line arguments:

`--input` to load the .gml\
`--create_random_graph` to make random graph\
`--nodes` to set the amount of nodes\
`--constant` to set constant number\
`--BFS` to set the starting node for BFS\
`--plot` to plot a graph\
`--output` to set the name of the .gml file

