from qiskit import QuantumCircuit
import rustworkx
from helperfunctions.uncompfunctions import greedy_uncomputation_full
from helperfunctions.circuitgraphfunctions import get_computation_graph, get_uncomp_circuit

from helperfunctions.graphhelper import edge_attr, node_attr
from rustworkx.visualization import graphviz_draw

def simple_circuit_with_a2_uncomputable():
    circuit = QuantumCircuit(6)

    for i in range(3):
        circuit.cx(i,i+3)

    circuit.cx(4,1)

    return circuit

def complex_circuit_failing_greedy_uncomp():
    circuit = QuantumCircuit(8)
    circuit.mcx([5,6,7], 0)
    circuit.mcx([0,2], 6)
    circuit.mcx([5,7], 1)
    circuit.mcx([0],6)
    circuit.mcx([0,3],6)
    circuit.mcx([5,6,7], 3)
    circuit.mcx([5,6], 4)
    circuit.mcx([0,2,3,4], 7)
    circuit.mcx([5,6,7], 0)
    circuit.mcx([5,6], 3)
    circuit.mcx([2,3,4], 6)
    circuit.mcx([1,2], 5)
    circuit.mcx([7],4)
    circuit.mcx([1,2,3], 6)    
    circuit.mcx([6],0)
    circuit.mcx([0,1,2,3], 5)
    circuit.mcx([0,1,2,3], 5)
    circuit.mcx([5,6,7], 2)

    return circuit    

circuit = complex_circuit_failing_greedy_uncomp()
comp_graph = get_computation_graph(circuit, 5)
graphviz_draw(comp_graph, filename='test_figures/GreedyCircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')

if rustworkx.digraph_find_cycle(comp_graph):
    print(f'Computation Graph has cycles !!!!')
    for cycle in rustworkx.simple_cycles(comp_graph):
        print(cycle)
    
uncomp_graph = greedy_uncomputation_full(comp_graph, 5,3)


graphviz_draw(uncomp_graph, filename='test_figures/GreedyUncomputationCircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')
uncomp_circuit = get_uncomp_circuit(uncomp_graph)

uncomp_circuit.draw("mpl", filename='test_figures/GreedyUncomputationCircuit.png')