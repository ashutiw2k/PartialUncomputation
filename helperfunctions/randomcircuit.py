from qiskit import QuantumCircuit, QuantumRegister
import random

def random_quantum_circuit(num_q:int, num_a:int, num_g:int=10) -> QuantumCircuit:
    in_q = QuantumRegister(num_q, name='cq')
    an_q = QuantumRegister(num_a, name='aq')
    
    circuit = QuantumCircuit(in_q, an_q)

    for i in range(num_g):
        cq = random.randrange(num_q) # Get input qubit
        aq = random.randrange(num_a) # Get ancilla qubit
        
        if random.random() < 0.75: # Input acts on Ancilla
            circuit.cx(in_q[cq],an_q[aq])
        else: # Ancilla acts on input
            circuit.cx(an_q[aq],in_q[cq])

    return circuit