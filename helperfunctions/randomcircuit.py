from qiskit import QuantumCircuit, QuantumRegister
import random
import logging

logger = logging.getLogger(__name__)

def random_quantum_circuit(num_q:int, num_a:int, num_g:int=10) -> QuantumCircuit:
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
    return circuit

# def random_quantum_circuit(num_q:int, num_a:int, num_g:int=10) -> QuantumCircuit:
#     in_q = QuantumRegister(num_q, name='cq')
#     an_q = QuantumRegister(num_a, name='aq')
    
#     circuit = QuantumCircuit(num_q+num_a)
    
#     for i in range(num_g):
        
#         if random.random() < 0.75: # Input acts on Ancilla    
#             control_q = range(num_q)
#             target_q = range(num_q, num_q+num_a)

#         else: # Ancilla acts on input
#             control_q = range(num_q, num_q+num_a)
#             target_q = range(num_q)

#         num_controls = random.randint(1, len(control_q))
#         controls = random.sample(control_q, num_controls)  # Get control qubit/s
#         target = random.sample(target_q, 1) # Get target qubit
#         print(num_controls, controls, target)
#         circuit.mcx(controls, target[0]) 

#     logger.info(f'Built circuit with {num_q} input, {num_a} ancilla and {num_g} gates.')
#     return circuit