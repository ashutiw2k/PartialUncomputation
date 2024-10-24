import random
from qiskit import QuantumCircuit, qpy

import rustworkx
from helperfunctions.randomcircuit import random_quantum_circuit_for_partial
from helperfunctions.uncompfunctions import greedy_uncomputation_partial, add_uncomputation, exhaustive_uncomputation_adding
from helperfunctions.circuitgraphfunctions import get_computation_graph, get_uncomp_circuit

from helperfunctions.graphhelper import breakdown_qubit, edge_attr, node_attr
from rustworkx.visualization import graphviz_draw

def test_circuit():
    circuit = QuantumCircuit(6)
    circuit.cx(0,3)
    circuit.cx(1,3)
    
    
    circuit.cx(3,0)
    
    circuit.cx(4,3)
    circuit.cx(3,4)
    
    circuit.cx(2,3)
    
    circuit.cx(3,4)
    circuit.cx(4,3)
    
    # circuit.cx(0,5)
    # circuit.cx(1,5)
    # circuit.cx(2,5)


    return circuit,3,3

def mcx_with_ancilla_test_circuit():
    circuit = QuantumCircuit(6)

'''
Uncomment this line to run the simple test circuit shown above. 
It's form is:
               ┌───┐                         
q_0: ──■───────┤ X ├─────────────────────────
       │       └─┬─┘                         
q_1: ──┼────■────┼───────────────────────────
       │    │    │                           
q_2: ──┼────┼────┼──────────────■────────────
     ┌─┴─┐┌─┴─┐  │  ┌───┐     ┌─┴─┐     ┌───┐
q_3: ┤ X ├┤ X ├──■──┤ X ├──■──┤ X ├──■──┤ X ├
     └───┘└───┘     └─┬─┘┌─┴─┐└───┘┌─┴─┐└─┬─┘
q_4: ─────────────────■──┤ X ├─────┤ X ├──■──
                         └───┘     └───┘     
q_5: ────────────────────────────────────────

'''
# circuit,num_q,num_a = test_circuit()

'''
Uncomment the below lines to generate a new random circuit and run the algorithm on it. 
You can also opt to store the random circuit as a qpy file in case the algorithm fails, and you'd
like to debug why. 
'''
# circuit, num_q, num_a, num_g = random_quantum_circuit_for_partial()
# with open('test_qasm/greedy_partial_bug.qpy', 'wb') as f, open('nums.txt', 'w') as f2:
#     qpy.dump(circuit, f)
#     print(num_q, num_a, num_g, file=f2, sep='\n')

'''
Uncomment lines below to read work with a saved random circuit. 
'''
with open('test_qasm/Circuit_5.qpy', 'rb') as f, open('nums.txt', 'r') as f2:
    circuit = qpy.load(f)[0]
    num_q = int(f2.readline())
    num_a = int(f2.readline())
    num_g = int(f2.readline())

circuit.draw("mpl", filename='test_figures/Greedy_Partial_Circuit.png')

ancillas_list = [breakdown_qubit(q)['label'] for q in circuit.qubits][-num_a:]
comp_graph = get_computation_graph(circuit, ancillas_list)
# graphviz_draw(comp_graph, filename='test_figures/Greedy_Partial_CircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')

if rustworkx.digraph_find_cycle(comp_graph):
    print(f'Computation Graph has cycles !!!!')
    for cycle in rustworkx.simple_cycles(comp_graph):
        print(cycle)

cyclic_uncomp_graph, has_cycle = add_uncomputation(comp_graph, ancillas_list, allow_cycle=True)
# graphviz_draw(cyclic_uncomp_graph, filename='test_figures/Cyclic_Partial_UncomputationCircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')

# removable_ancilla = exhaustive_uncomputation_adding(comp_graph, ancillas_list)
# print(f'Valid ancilla that can be uncomputed : {removable_ancilla}')
# uncomp_graph, has_cycle = add_uncomputation(comp_graph, removable_ancilla)
# if has_cycle:
#     print('Ancillas returned by exhaustive adding function still create cycle if uncomputed')

uncomp_graph = greedy_uncomputation_partial(comp_graph, ancillas_list, max_cycles=5*(10**5))

# graphviz_draw(uncomp_graph, filename='test_figures/Partial_UncomputationCircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')

uncomp_circuit = get_uncomp_circuit(uncomp_graph)

uncomp_circuit.draw("mpl", filename='test_figures/Greedy_Partial_UncomputationCircuit.png')