import qiskit
from qiskit import QuantumCircuit, transpile
import qiskit_aer
from qiskit_aer import AerSimulator
from qiskit_aer.quantum_info import AerStatevector
import numpy as np

def get_statevector(circuit: QuantumCircuit):
    circuit_copy = circuit.copy()
    circuit_copy.save_statevector()
    
    # This gives us the amplitudes
    simulator = AerSimulator(method='statevector')

    circ = transpile(circuit_copy, simulator)

    # Run and get statevector
    result = simulator.run(circ).result()
    statevector = result.get_statevector(circ)
    return statevector

def zero_ancillas_in_statevector(statevector: AerStatevector, num_a: int):
    zero_ancilla_statevec = np.zeros(int(len(statevector)/(2**num_a)), dtype='complex')
    for i,x in enumerate(statevector):
        # Since the last 'num_a' values are 
        idx = int(i/(2**num_a))
        zero_ancilla_statevec[idx] += x

    zero_ancilla_statevec[zero_ancilla_statevec < 10**(-8)] = 0
    return zero_ancilla_statevec


def print_statevector(statevector: AerStatevector):
    pad_len = int(len(statevector) ** 0.5)
    for i,x in enumerate(statevector):
        print(f'|{bin(i).split("b")[1].zfill(pad_len)}> : {x:.4f}', end=' , ')
        if i+1 % 4 == 0:
            print()

    print()
    print('----------------------------------------')