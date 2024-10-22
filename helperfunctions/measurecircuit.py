import qiskit
from qiskit import QuantumCircuit, transpile
import qiskit_aer
from qiskit_aer import AerSimulator
from qiskit_aer.quantum_info import AerStatevector
import numpy as np

def get_statevector(circuit: QuantumCircuit):
    circuit_copy = circuit.copy()
    circuit_copy.save_statevector()
    
    simulator = AerSimulator(method='statevector')

    circ = transpile(circuit_copy, simulator)

    # Run and get statevector
    result = simulator.run(circ).result()
    statevector = result.get_statevector(circ)
    return statevector

def zero_ancillas_in_statevector(statevector: AerStatevector, num_a: int):
    zero_ancilla_statevec = np.zeros(int(len(statevector)/(2**num_a)))
    for i,x in enumerate(statevector):
        zero_ancilla_statevec[int(i/(2**num_a))] += x

    return zero_ancilla_statevec


