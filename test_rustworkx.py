import rustworkx as rx

def count_cycles_containing_node(graph, node):
    """
    Count the number of cycles in which a given node is involved.

    :param graph: A rustworkx PyGraph object
    :param node: The node for which to count cycles
    :return: The number of cycles containing the specified node
    """
    # Get all cycles in the graph
    cycles = rx.cycle_basis(graph)
    
    # Count the number of cycles that contain the given node
    count = sum(1 for cycle in cycles if node in cycle)
    
    return count

# Example usage:
# Create a graph with a few nodes and edges
graph = rx.PyGraph()
graph.add_nodes_from([0, 1, 2, 3])
graph.add_edges_from([(0, 1,'e'), (1, 2,'e'), (2, 0,'e'), (2, 3,'e'), (3, 0,'e')])

# Count the cycles containing node 0
node = 0
num_cycles = count_cycles_containing_node(graph, node)
print(f"Node {node} is part of {num_cycles} cycle(s).")
