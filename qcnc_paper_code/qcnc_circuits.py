import os, sys
import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

from qiskit.providers.basic_provider import BasicSimulator
from qiskit.visualization import plot_histogram

def run_measurements(args):
    backend = BasicSimulator()
    circuit, filename = args
    job = backend.run(circuit)
    result = job.result()
    counts = result.get_counts()
    plot_histogram(counts, filename=filename+'_plot')
    print(counts)

def basic_circuit(dir='qcnc_paper_code/'):
    input_q = QuantumRegister(2, 'q')
    input_c = ClassicalRegister(2, 'qc')
    ancilla_q = QuantumRegister(2, 'a')
    ancilla_c = ClassicalRegister(2, 'ac')

    circuit = QuantumCircuit(input_q, input_c, ancilla_q, ancilla_c)
    circuit.h(input_q[0])
    circuit.h(input_q[1])

    circuit.barrier(range(4))
    circuit.cx(input_q[0], ancilla_q[0])
    circuit.cx(input_q[1], ancilla_q[1])

    # circuit.cx(ancilla_q[0], input_q[0])


    # circuit.cx(inpput_q[0], ancilla_q[0])
    # circuit.cx(input_q[1], ancilla_q[1])

    circuit.barrier(range(4))
    circuit.h(input_q[0])
    circuit.h(input_q[1])

    circuit.barrier(range(4))
    circuit.measure(qubit=input_q[0], cbit=input_c[0])
    circuit.measure(qubit=input_q[1], cbit=input_c[1])
    circuit.measure(qubit=ancilla_q[0], cbit=ancilla_c[0])
    circuit.measure(qubit=ancilla_q[1], cbit=ancilla_c[1])
    circuit.draw('mpl', initial_state=True, plot_barriers=False, filename=dir+'qcnc_paper_figures/basic_circuit')

    return circuit, dir+'qcnc_paper_figures/basic_circuit'

def basic_circuit_with_uncomp(dir='qcnc_paper_code/'):
    input_q = QuantumRegister(2, 'q')
    input_c = ClassicalRegister(2, 'qc')
    ancilla_q = QuantumRegister(2, 'a')
    ancilla_c = ClassicalRegister(2, 'ac')

    circuit = QuantumCircuit(input_q, input_c, ancilla_q, ancilla_c)
    circuit.h(input_q[0])
    circuit.h(input_q[1])

    # This is to group the gates in the drawing better
    circuit.barrier(range(4))
    
    circuit.cx(input_q[0], ancilla_q[0])
    circuit.cx(input_q[1], ancilla_q[1])


    circuit.barrier(range(4))
    # circuit.cx(ancilla_q[0], input_q[0])


    circuit.cx(input_q[0], ancilla_q[0])
    circuit.cx(input_q[1], ancilla_q[1])

    circuit.barrier(range(4))

    circuit.h(input_q[0])
    circuit.h(input_q[1])

    circuit.barrier(range(4))

    circuit.measure(qubit=input_q[0], cbit=input_c[0])
    circuit.measure(qubit=input_q[1], cbit=input_c[1])
    circuit.measure(qubit=ancilla_q[0], cbit=ancilla_c[0])
    circuit.measure(qubit=ancilla_q[1], cbit=ancilla_c[1])
    circuit.draw('mpl', initial_state=True, plot_barriers=False, filename=dir+'qcnc_paper_figures/basic_circuit_with_uncomp')

    return circuit, dir+'qcnc_paper_figures/basic_circuit_with_uncomp'

# print(os.)
run_measurements(basic_circuit())
run_measurements(basic_circuit_with_uncomp())
