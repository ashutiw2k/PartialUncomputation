import random
from qiskit import QuantumCircuit

from helperfunctions.circuitgraphfunctions import get_computation_graph, get_uncomp_circuit
from helperfunctions.graphhelper import edge_attr, node_attr

from rustworkx.visualization import graphviz_draw

from helperfunctions.uncompfunctions import add_uncomputation, exhaustive_uncomputation_adding, exhaustive_uncomputation_removing, remove_uncomputation

def paper_adder_circuit():
    adder_circuit = QuantumCircuit(4)

    adder_circuit.ccx(0,1, 3)
    adder_circuit.cx(0, 1)
    adder_circuit.cx(3, 2)
    # adder_circuit.x(3)
    # adder_circuit.z(3)

    return adder_circuit

def cyclic_circuit():
    circuit = QuantumCircuit(4)

    circuit.cx(0, 1)
    circuit.cx(1, 2)
    circuit.cx(2, 3)
    circuit.cx(3, 0)

    return circuit

def generate_cx_random_circuit(num_qubits, num_ancilla, num_gates):
    circuit = QuantumCircuit(num_qubits+num_ancilla)

    for i in range(num_gates):
        ctrl = random.randint(0, num_qubits-1)
        target = random.randint(num_ancilla, num_qubits+num_ancilla-1)
        if random.random() < 0.5:
            circuit.cx(ctrl, target)
        else:
            circuit.cx(target, ctrl)

    return circuit

def simple_circuit_with_a2_uncomputable():
    circuit = QuantumCircuit(6)

    for i in range(3):
        circuit.cx(i,i+3)

    circuit.cx(4,1)

    return circuit


def complex_circuit_with_ancilla_in_multi_states():
    circuit = QuantumCircuit(6)

    circuit.cx(0,4)
    circuit.cx(1,5)

    circuit.ccx(0,1,3)
    circuit.cx(3,5)
    circuit.cx(0,3)

    circuit.ccx(3,4,2)
    circuit.ccx(1,3,5)
    circuit.ccx(5,4,2)

    return circuit

def complex_circuit():
    circuit = QuantumCircuit(6)
    return circuit

def main():
    # circ_gen = False
    # while not circ_gen:
    #     nq = random.randint(1, 6)
    #     na = random.randint(1, 6)
    #     nd = random.randint(na+nq, 2*(na+nq))
    #     print(f'nq: {nq}, na: {na}, nd: {nd}')
    #     try:
    #         circuit = generate_cx_random_circuit(nq, na, nd)
    #     except:
    #         continue
    #     circ_gen = True
    print('Creating Circuit:')
    
    
    # nq=3
    # na=1
    # circuit = paper_adder_circuit()
    
    # nq=2
    # na=2
    # circuit = cyclic_circuit()

    nq=3
    na=3
    circuit = simple_circuit_with_a2_uncomputable()    
     
    # nq=3
    # na=3
    # circuit = complex_circuit_with_ancilla_in_multi_states()

    circuit.draw(output='mpl', filename="ComputationCircuit.png")

    print('Building Circuit Graph:')
    circuit_graph = get_computation_graph(circuit, nq)
    graphviz_draw(circuit_graph, filename='ComputationCircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')
    
    print('Adding Uncomputation:')
    uncomp_circuit_graph, has_cycle = add_uncomputation(circuit_graph, range(nq,nq+na))
    graphviz_draw(uncomp_circuit_graph, filename='UncomputationCircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')

    if not has_cycle:
        print('Building Uncomp Circuit from Uncomp Graph:')
        uncomp_circuit = get_uncomp_circuit(uncomp_circuit_graph)
        uncomp_circuit.draw(output='mpl', filename='UncomputationCircuit.png')
    else:
        print("=======================================================")
        print('Uncomp Circuit Graph has cycle, can not uncompute all')
        print('Trying Exhaustive Uncomp')
        largest_set = exhaustive_uncomputation_adding(circuit_graph, nq, na)
        print("=======================================================")
        print(F'Largest set of ancilla we can uncompute is {largest_set}')
        print("=======================================================")
        uncomp_circuit_graph, has_cycle = add_uncomputation(circuit_graph, list(largest_set))
        graphviz_draw(uncomp_circuit_graph, filename='UncomputationCircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')
        print('Building Uncomp Circuit from Uncomp Graph:')
        uncomp_circuit = get_uncomp_circuit(uncomp_circuit_graph)
        uncomp_circuit.draw(output='mpl', filename='UncomputationCircuit.png')

        print("=======================================================")
        
        print('Trying Exhaustive Removal Uncomp')
        smallest_set = exhaustive_uncomputation_removing(circuit_graph, nq, na)
        print("=======================================================")
        print(F'Smallest set of ancilla to remove is {smallest_set}')
        print("=======================================================")
        cyclic_uncomp_circuit_graph, has_cycle = add_uncomputation(circuit_graph, range(nq,na+nq), allow_cycle=True)
        
        graphviz_draw(cyclic_uncomp_circuit_graph, filename='CyclicUncomputationCircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')
        reduced_uncomp_circuit_graph = remove_uncomputation(cyclic_uncomp_circuit_graph, smallest_set)
        graphviz_draw(reduced_uncomp_circuit_graph, filename='ReducedUncomputationCircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')
        

        print('Building Uncomp Circuit from Uncomp Graph:')
        reduced_uncomp_circuit = get_uncomp_circuit(reduced_uncomp_circuit_graph)
        reduced_uncomp_circuit.draw(output='mpl', filename='ReducedUncomputationCircuit.png')

        print("=======================================================")

        # QuantumCircuit(nq+na).draw(output='mpl', filename='UncomputationCircuit.png')

if __name__ == '__main__':
    main()
