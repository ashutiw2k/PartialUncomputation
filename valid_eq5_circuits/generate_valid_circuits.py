import os
import sys
import time
import yaml
import gc
import numpy as np
import rustworkx
from qiskit.quantum_info import Statevector, partial_trace
from qiskit import QuantumCircuit, qpy

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not '../helperfunctions' in sys.path:
    sys.path.insert(1, '../helperfunctions')
print(sys.path)

from helperfunctions.graphhelper import breakdown_qubit, edge_matcher, node_matcher
from helperfunctions.randomcircuit import random_quantum_circuit_varied_percentages, get_ancillas_of_circuit
from helperfunctions.uncompfunctions import add_uncomputation, exhaustive_uncomputation_adding, greedy_uncomputation_full, greedy_uncomputation_partial
from helperfunctions.circuitgraphfunctions import get_computation_graph, get_uncomp_circuit
from helperfunctions.evaluation import ProbDiffResults, get_difference_in_prob, plot_results, plot_results_bar
from helperfunctions.measurecircuit import get_statevector, zero_ancillas_in_statevector

def test_circuit():
    valid_circuitq = QuantumCircuit(9)
    for i in range(3):
        valid_circuitq.h(i)
        # valid_circuitq.ry(theta*i/3, i)
        valid_circuitq.cx(i,i+3)
    valid_circuitq.ccx(0,1,6)

    for i in range(3):
        valid_circuitq.cx(i+3,i)
    
    valid_circuitq.ccx(2,3,7)
    
    valid_circuitq.cx(3,1)
    valid_circuitq.cx(4,2)
    valid_circuitq.cx(5,0)

    
    valid_circuitq.ccx(6,7,8)

    return valid_circuitq, 3,6,12

def generate_valid_circuits(num_circuits=10, write_path = 'valid_eq5_circuits/circuit_qpys'):
    i = 0
    ctr=0
    while i < num_circuits:
        circuit, q,a,g = random_quantum_circuit_varied_percentages(
            add_random_h=True,
            percent_cc_gates=0.6,
            percent_aa_gates=0.2,
            percent_ac_gates=0.1,
            percent_ca_gates=0.1
        )
        # circuit, q,a,g = test_circuit()
        
        print(f'Iteration Number {ctr}')
        ctr +=1
        ancillas = get_ancillas_of_circuit(circuit, a)
        circuit_graph = get_computation_graph(circuit, ancillas)

        uncomp_graph, has_cycle = add_uncomputation(circuit_graph, ancillas)

        if has_cycle:
            circuit_sv = Statevector(get_statevector(circuit))
            computation_probs_circ = circuit_sv.probabilities(range(q))
            zero_ancillas = zero_ancillas_in_statevector(circuit_sv, a)
            zero_ancillas_prob = Statevector(zero_ancillas).probabilities(range(q))

            if 1.0 - zero_ancillas_prob.sum() < 10**(-3):
                timefrac, timestamp = np.modf(time.time())
                timestring = time.strftime("%m-%d-%Y_%H:%M:%S", time.localtime(timestamp))
                print(f'Found Valid Circuit at {timestring}({time.time_ns()})')
                with open(f'{write_path}/{timestring}_{timefrac}.qpy', 'wb') as file:
                    qpy.dump(circuit, file)
                    i += 1


if __name__ == '__main__':
    num_circuits = 5
    if len(sys.argv) == 2:
        num_circuits = int(sys.argv[1])
    generate_valid_circuits(num_circuits)


