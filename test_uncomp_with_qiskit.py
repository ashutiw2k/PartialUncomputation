import random
from qiskit import QuantumCircuit

from helperfunctions.circuitgraphfunctions import get_computation_graph, get_uncomp_circuit
from helperfunctions.graphhelper import edge_attr, node_attr

from rustworkx.visualization import graphviz_draw

from helperfunctions.uncompfunctions import add_uncomputation

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
    nq=3
    na=1
    print('Creating Circuit:')
    # circuit = paper_adder_circuit()
    circuit = paper_adder_circuit()
    circuit.draw(output='mpl', filename="ComputationCircuit.png")

    print('Building Circuit Graph:')
    circuit_graph = get_computation_graph(circuit, nq)
    graphviz_draw(circuit_graph, filename='ComputationCircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')
    
    print('Adding Uncomputation:')
    uncomp_circuit_graph = add_uncomputation(circuit_graph, range(nq,nq+na))
    graphviz_draw(uncomp_circuit_graph, filename='UncomputationCircuitGraph.png', node_attr_fn=node_attr, edge_attr_fn=edge_attr, method='dot')

    print('Building Uncomp Circuit from Uncomp Graph:')
    uncomp_circuit = get_uncomp_circuit(uncomp_circuit_graph)
    uncomp_circuit.draw(output='mpl', filename='UncomputationCircuit.png')
if __name__ == '__main__':
    main()
