from qiskit import QuantumCircuit, QuantumRegister
import random
import logging
from numpy import pi

from tqdm import tqdm

logger = logging.getLogger(__name__)

# Random quantum circuits generated that only allow for 
# - Input - Ancilla gates
# - Ancilla - Input gates
# Results of Greedy and Greedy Partial are the same for this. 
def random_quantum_circuit_basic() -> tuple[QuantumCircuit,int,int,int]:
    num_q = random.randint(3,10)
    num_a = random.randint(3,10)
    num_g = random.randint(10,25)
    
    in_q = QuantumRegister(num_q, name='cq')
    an_q = QuantumRegister(num_a, name='aq')
    
    circuit = QuantumCircuit(in_q, an_q)
    
    for i in range(num_g):
        
        if random.random() < 0.75: # Input acts on Ancilla    
            control_q = in_q
            target_q = an_q

        else: # Ancilla acts on input
            control_q = an_q
            target_q = in_q

        num_controls = random.randint(1, control_q.size)
        controls = random.sample(range(control_q.size), num_controls)  # Get control qubit/s
        target = random.randrange(target_q.size) # Get target qubit
        print(num_controls, controls, target)
        circuit.mcx([control_q[cq] for cq in controls],target_q[target]) 

    logger.info(f'Built circuit with {num_q} input, {num_a} ancilla and {num_g} gates.')
    return circuit, num_q, num_a, num_g

def random_quantum_circuit_for_partial() -> tuple[QuantumCircuit,int,int,int]:
    num_q = random.randint(3,10)
    num_a = random.randint(3,10)
    num_g = random.randint(10,25)
    
    in_q = QuantumRegister(num_q, name='cq')
    an_q = QuantumRegister(num_a, name='aq')
    
    circuit = QuantumCircuit(in_q, an_q)

    # Add random inputs
    for i in num_q:
        # circuit.rx(pi/4)
        # circuit.ry(pi/4)
        # circuit.rz(pi/4)
        circuit.h(in_q[i])
    
    for i in range(num_g):
        
        # if random.random() < 0.75: # Input acts on Ancilla    
        #     control_q = in_q
        #     target_q = an_q

        # else: # Ancilla acts on input
        #     control_q = an_q
        #     target_q = in_q
        total_q = num_q+num_a
        num_controls = random.randint(1, total_q-1)
        available_qubits = list(range(total_q))

        target = random.choice(available_qubits) # Get target qubit
        available_qubits.remove(target)
        controls = random.sample(available_qubits, num_controls)  # Get control qubit/s
        print(num_controls, controls, target)
        circuit.mcx(controls, target) 

    logger.info(f'Built circuit with {num_q} input, {num_a} ancilla and {num_g} gates.')
    return circuit, num_q, num_a, num_g

def random_quantum_circuit_large() -> tuple[QuantumCircuit,int,int,int]:
    
    num_q = random.randint(3,10)
    num_a = random.randint(3,10)
    num_g = random.randint(50, 100)
    # num_g = random.randint(10,50)
    # num_g = 75

    cc_gates = 0
    ca_gates = 0
    ac_gates = 0
    aa_gates = 0
    
    in_q = QuantumRegister(num_q, name='cq')
    an_q = QuantumRegister(num_a, name='aq')
    
    circuit = QuantumCircuit(in_q, an_q)

    for q in in_q:
        circuit.x(q)
        circuit.h(q)
    
    for i in tqdm(range(num_g), desc=f'Building Random Quantum Circuit with {num_q}q, {num_a}a, {num_g}g'):

        control_q = in_q
        target_q = in_q

        change_target_controls = random.random()

        if change_target_controls > 0.9: # Input acts on Input only    
            control_q = an_q
            target_q = an_q
            aa_gates += 1

        elif change_target_controls > 0.8: 
            # control_q = in_q
            if random.random() > 0.7:
                target_q = an_q
                ca_gates += 1
            else:
                control_q = an_q
                ac_gates += 1

        else:
            cc_gates += 1 
            

        num_controls = random.randrange(1, control_q.size)
        target = random.randrange(target_q.size) # Get target qubit
        controls = random.sample(range(control_q.size), num_controls)  # Get control qubit/s
        # target = random.randrange(target_q.size) # Get target qubit
        if control_q == target_q:
            target = random.randrange(target_q.size) # Get target qubit
            valid_controls = list(range(control_q.size))
            valid_controls.remove(target)
            controls = random.sample(valid_controls, num_controls)  # Get control qubit/s
        else:
            target = random.randrange(target_q.size) # Get target qubit
            controls = random.sample(range(control_q.size), num_controls)  # Get control qubit/s
        
        # print(num_controls, controls, target)
        circuit.mcx([control_q[cq] for cq in controls],target_q[target]) 

    logger.info(f'Built circuit with {num_q} input, {num_a} ancilla and {num_g} gates.')
    logger.info(f'There are {cc_gates} gates acting between control qubits, {ca_gates} gates acting between control and ancilla, {ac_gates} gates acting between ancilla and control and {aa_gates} gates acting between just the ancillas.')
    
    return circuit, num_q, num_a, num_g
