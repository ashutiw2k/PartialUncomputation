from helperfunctions.graphhelper import edge_attr, node_attr
from helperfunctions.randomcircuit import random_quantum_circuit
from helperfunctions.circuitgraphfunctions import get_uncomp_circuit
from helperfunctions.circuitgraphfunctions import get_computation_graph

from rustworkx.visualization import graphviz_draw

import random

num_q = random.randint(3,5)
num_a = random.randint(3,5)
num_g = random.randint(5,10)

circuit = random_quantum_circuit(num_q, num_a, num_g)
circuit.draw('mpl', filename='test_figures/random_circuit_gen/test_circuit.png')

comp_graph = get_computation_graph(circuit, num_q)
graphviz_draw(comp_graph, filename='test_figures/random_circuit_gen/comp_graph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')

new_circuit = get_uncomp_circuit(comp_graph)
new_circuit.draw('mpl', filename='test_figures/random_circuit_gen/test_output_circuit.png')