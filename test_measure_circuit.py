from qiskit import QuantumCircuit
from helperfunctions.measurecircuit import get_statevector, zero_ancillas_in_statevector, print_statevector

def h_2_circuit():
    circuit = QuantumCircuit(4)
    circuit.h(0)
    circuit.h(1)
    circuit.cx(0,2)
    circuit.cx(1,3)

    circuit.h(0)
    circuit.h(1)


    return circuit, 2, 2, 6

def h_2_circuit_all_uncomp():
    circuit = QuantumCircuit(4)
    circuit.h(0)
    circuit.h(1)
    circuit.cx(0,2)
    circuit.cx(1,3)

    # Uncomp all
    circuit.cx(0,2)
    circuit.cx(1,3)

    circuit.h(0)
    circuit.h(1)


    return circuit, 2, 2, 6

def h_2_circuit_one_uncomp_done():
    circuit = QuantumCircuit(4)
    circuit.h(0)
    circuit.h(1)
    circuit.cx(0,2)
    circuit.cx(1,3)

    # Making a1 (from q1) uncomputable
    circuit.cx(3,1)
    # Uncomp q0,a0
    circuit.cx(0,2)

    circuit.h(0)
    circuit.h(1)


    return circuit, 2, 2, 7

def h_2_circuit_one_uncomp():
    circuit = QuantumCircuit(4)
    circuit.h(0)
    circuit.h(1)
    circuit.cx(0,2)
    circuit.cx(1,3)

    # Making a1 (from q1) uncomputable
    circuit.cx(3,1)
    # # Uncomp q0,a0
    circuit.cx(0,2)

    circuit.h(0)
    circuit.h(1)


    return circuit, 2, 2, 7

def main():
    circuit, num_q, num_a, num_g = h_2_circuit()
    circuit_all_uncomp, num_q, num_ua, num_g = h_2_circuit_all_uncomp()
    circuit_one_uncomp, num_q, num_oa, num_g = h_2_circuit_one_uncomp()
    circuit_red_uncomp, num_q, num_ra, num_g = h_2_circuit_one_uncomp_done()
    
    circ_statevec = get_statevector(circuit)
    circ_all_uncomp_statevec = get_statevector(circuit_all_uncomp)
    circ_one_uncomp_statevec = get_statevector(circuit_one_uncomp)
    circ_red_uncomp_statevec = get_statevector(circuit_red_uncomp)
    
    print(f'Circuit StateVector: \n{circ_statevec}')
    print(f'All Uncomp Circuit StateVector: \n {circ_all_uncomp_statevec}')
    print(f'One Uncomp Circuit StateVector: \n {circ_one_uncomp_statevec}')
    print(f'One Uncomp Done Circuit StateVector: \n {circ_red_uncomp_statevec}')

    zero_ancilla_circ_statevec = zero_ancillas_in_statevector(circ_statevec, num_a)
    zero_ancilla_circ_all_uncomp_statevec = zero_ancillas_in_statevector(circ_all_uncomp_statevec, num_ua)
    zero_ancilla_circ_one_uncomp_statevec = zero_ancillas_in_statevector(circ_one_uncomp_statevec, num_oa)
    zero_ancilla_circ_red_uncomp_statevec = zero_ancillas_in_statevector(circ_red_uncomp_statevec, num_ra)

    print('----------------------------------------------------------')

    print(zero_ancilla_circ_statevec)
    print(zero_ancilla_circ_all_uncomp_statevec)
    print(zero_ancilla_circ_one_uncomp_statevec)
    print(zero_ancilla_circ_red_uncomp_statevec)
    print('----------------------------------------------------------')

    print_statevector(zero_ancilla_circ_statevec)
    print_statevector(zero_ancilla_circ_all_uncomp_statevec)
    print_statevector(zero_ancilla_circ_one_uncomp_statevec)
    print_statevector(zero_ancilla_circ_red_uncomp_statevec)


if __name__=='__main__':
    main()
