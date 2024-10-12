from qiskit import QuantumCircuit
from helperfunctions.uncompfunctions import greedy_uncomputation
from helperfunctions.circuitgraphfunctions import get_computation_graph, get_uncomp_circuit

from helperfunctions.graphhelper import edge_attr, node_attr
from rustworkx.visualization import graphviz_draw

def simple_circuit_with_a2_uncomputable():
    circuit = QuantumCircuit(6)

    for i in range(3):
        circuit.cx(i,i+3)

    circuit.cx(4,1)

    return circuit

circuit = simple_circuit_with_a2_uncomputable()
comp_graph = get_computation_graph(circuit, 3)
uncomp_graph = greedy_uncomputation(comp_graph, 3,3)


graphviz_draw(uncomp_graph, filename='GreedyUncomputationCircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')
uncomp_circuit = get_uncomp_circuit(uncomp_graph)

uncomp_circuit.draw("mpl", filename='GreedyUncomputationCircuitGraph.png')