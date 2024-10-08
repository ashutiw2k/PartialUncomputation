import os, sys
import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit.providers.basic_provider import BasicSimulator
from qiskit.visualization import plot_histogram

def run_measurements(args):
    backend = BasicSimulator()
    circ, filename = args
    # For MCX and other complex gates
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    circuit = pm.run(circ)
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

    circuit.draw('mpl', initial_state=True, plot_barriers=False, idle_wires=False, filename=dir+'qcnc_paper_figures/basic_circuit')

    circuit.measure(qubit=input_q[0], cbit=input_c[0])
    circuit.measure(qubit=input_q[1], cbit=input_c[1])
    circuit.measure(qubit=ancilla_q[0], cbit=ancilla_c[0])
    circuit.measure(qubit=ancilla_q[1], cbit=ancilla_c[1])

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

    circuit.draw('mpl', initial_state=True, plot_barriers=False, idle_wires=False, filename=dir+'qcnc_paper_figures/basic_circuit_with_uncomp')

    circuit.measure(qubit=input_q[0], cbit=input_c[0])
    circuit.measure(qubit=input_q[1], cbit=input_c[1])
    circuit.measure(qubit=ancilla_q[0], cbit=ancilla_c[0])
    circuit.measure(qubit=ancilla_q[1], cbit=ancilla_c[1])

    return circuit, dir+'qcnc_paper_figures/basic_circuit_with_uncomp'

def basic_circuit_with_sub_uncomp(dir='qcnc_paper_code/'):
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
    # circuit.cx(input_q[1], ancilla_q[1])

    circuit.barrier(range(4))

    circuit.h(input_q[0])
    circuit.h(input_q[1])

    circuit.barrier(range(4))
    
    circuit.draw('mpl', initial_state=True, plot_barriers=False, idle_wires=False, filename=dir+'qcnc_paper_figures/basic_circuit_with_sub_uncomp')

    circuit.measure(qubit=input_q[0], cbit=input_c[0])
    circuit.measure(qubit=input_q[1], cbit=input_c[1])
    circuit.measure(qubit=ancilla_q[0], cbit=ancilla_c[0])
    circuit.measure(qubit=ancilla_q[1], cbit=ancilla_c[1])
    
    return circuit, dir+'qcnc_paper_figures/basic_circuit_with_sub_uncomp'

def multi_cnot_simple(dir='qcnc_paper_code/'):
    circuit = QuantumCircuit(4)
    circuit.x(range(3))
    circuit.mcx([0,1,2], 3)
    circuit.draw('mpl', initial_state=True, plot_barriers=False, idle_wires=False, filename=dir+'qcnc_paper_figures/multi_cnot_simple')
    circuit.measure_all()

    return circuit, dir+'qcnc_paper_figures/multi_cnot_simple'

def multi_cnot_with_ancilla(dir='qcnc_paper_code/'):
    input_q = QuantumRegister(4, 'q')
    # input_c = ClassicalRegister(4, 'qc')
    ancilla_q = QuantumRegister(1, 'a')
    # ancilla_c = ClassicalRegister(1, 'ac')

    circuit = QuantumCircuit(input_q, ancilla_q)

    circuit.x(range(3))
    circuit.ccx(0,1,4)
    circuit.ccx(2,4,3)
    circuit.ccx(0,1,4)
    
    # Drawing before measurement to not have the measurement features show up
    circuit.draw('mpl', initial_state=True, plot_barriers=False, idle_wires=False, filename=dir+'qcnc_paper_figures/multi_cnot_with_ancilla')
    
    circuit.measure_all()

    return circuit, dir+'qcnc_paper_figures/multi_cnot_with_ancilla'

# print(os.)
run_measurements(basic_circuit())
run_measurements(basic_circuit_with_uncomp())
run_measurements(basic_circuit_with_sub_uncomp())
run_measurements(multi_cnot_simple())
run_measurements(multi_cnot_with_ancilla())
