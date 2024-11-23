import os
import sys
from qiskit import QuantumCircuit, QuantumRegister
import numpy
import gc

import rustworkx

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not '../helperfunctions' in sys.path:
    sys.path.insert(1, '../helperfunctions')
print(sys.path)

from helperfunctions.graphhelper import breakdown_qubit, edge_matcher, node_matcher
from helperfunctions.randomcircuit import random_quantum_circuit_large_with_params
from helperfunctions.uncompfunctions import add_uncomputation, exhaustive_uncomputation_adding, greedy_uncomputation_full, greedy_uncomputation_partial
from helperfunctions.circuitgraphfunctions import get_computation_graph, get_uncomp_circuit
from helperfunctions.evaluation import ProbDiffResults, get_difference_in_prob, plot_results_angles

def static_circuit_1(theta):
    circuit = QuantumCircuit(QuantumRegister(3, name='cq'), QuantumRegister(3, name='aq'))
    
    for i in range(3):
        circuit.ry(theta*numpy.pi, i)
        # circuit.h(i)
        # circuit.rx(theta*numpy.pi, i)
        # circuit.ry(theta*numpy.pi, i)
        # circuit.rx(theta*numpy.pi/2, i)
    
    circuit.cx(0,3)
    circuit.cx(1,3)
    
    circuit.cz(3,0)
    
    circuit.cx(0,5)
    
    circuit.cx(4,3)
    circuit.cx(3,4)
    
    circuit.cx(1,5)
    circuit.cx(2,3)
    
    circuit.cx(3,4)
    circuit.cx(4,3)
    circuit.cx(5,2)

    for i in range(3):
        circuit.h(i)


    return circuit, 3, 3, 11

def static_circuit_2(theta):
    
    circuit = QuantumCircuit(QuantumRegister(5, name='cq'), QuantumRegister(5, name='aq'))
    
    for i in range(5):
        # circuit.rx(theta*numpy.pi, i)
        circuit.h(i)
        if i < 4:
            circuit.ry(theta*numpy.pi*(i+1)/10, i)

    circuit.barrier()

    circuit.ccx(0,1,5)
    circuit.ccx(2,3,7)
    circuit.cx(4,6)
    
    circuit.barrier()

    circuit.ccx(5,6,8)
    circuit.ccx(6,7,9)

    circuit.barrier()

    circuit.ccx(0,2,8)
    circuit.ccx(1,3,9)

    circuit.cz(5,4)
    circuit.cz(7,4)
    
    circuit.barrier()
    
    circuit.ccx(8,9,6)
    circuit.cz(6,4)

    for i in range(5):
        circuit.h(i)

    return circuit, 5, 5, 11

def get_probability_metrics(_circuit:QuantumCircuit, num_q: int, num_a:int, 
                            results:ProbDiffResults, max_cycles=10**5,
                            distance='jensenshannon'):
    name_str='Circuit'
    idx = 0
    ancillas_list = [breakdown_qubit(q)['label'] for q in _circuit.qubits][-num_a:]
    _circuit_graph = get_computation_graph(_circuit, ancillas_list)
    _regular_uncomp_circuit_graph, has_cycle = add_uncomputation(_circuit_graph, ancillas_list)

    if has_cycle:
        largest_set = exhaustive_uncomputation_adding(_circuit_graph, ancillas_list)
        print(f'Largest Set of ancilla for {name_str} that can be uncomputed is {largest_set}')
        # results.add_exhaustive(largest_set)

        _exhaustive_uncomp_circuit_graph, has_cycle = add_uncomputation(_circuit_graph, list(largest_set))
        if has_cycle:
            print(f'Exhaustive Uncomp of {name_str} still has cycle')
        
        _exhaustive_uncomp_circuit = get_uncomp_circuit(_exhaustive_uncomp_circuit_graph)
        ex_vals = get_difference_in_prob(_circuit, _exhaustive_uncomp_circuit, num_q, num_a, distance=distance)
        results.add_to_exhaustive(*ex_vals, idx=idx)


# ***************************************************************************************************************#
        # logger.info(f'Attempting to run greedy uncomp on {name_str}')
        _greedy_uncomp_circuit_graph, gf_uncomp_ancillas = greedy_uncomputation_full(_circuit_graph, ancillas_list, 
                                                                    max_cycles=max_cycles, return_uncomputed_ancillas=True)
        
        _greedy_uncomp_circuit = get_uncomp_circuit(_greedy_uncomp_circuit_graph)
        gf_vals = get_difference_in_prob(_circuit, _greedy_uncomp_circuit, num_q, num_a, distance=distance)
        results.add_to_greedy_full(*gf_vals, idx=idx)

#**************************************************************************************************************#
        _greedy_partial_uncomp_circuit_graph, gp_uncomp_ancillas = greedy_uncomputation_partial(_circuit_graph, ancillas_list, 
                                                                            max_cycles=max_cycles, return_uncomputed_ancillas=True)
        
        _greedy_partial_uncomp_circuit = get_uncomp_circuit(_greedy_partial_uncomp_circuit_graph)
        gp_vals = get_difference_in_prob(_circuit, _greedy_partial_uncomp_circuit, num_q, num_a, distance=distance)
        results.add_to_greedy_partial(*gp_vals, idx=idx)

        # results.add_greedy_partial(gp_uncomp_ancillas)
        
#**************************************************************************************************************#
    else:
        _uncomp_circuit = get_uncomp_circuit(_regular_uncomp_circuit_graph)
        reg_vals = get_difference_in_prob(_circuit, _uncomp_circuit, num_q, num_a, distance=distance)
        results.add_to_regular(*reg_vals, idx=idx)

        # results.add_regular(ancillas_list)
        
    return results

def metrics_for_angles(circ_func):
    results_dict = {}
    circ_name= "circuit_1" if circ_func is static_circuit_1 else "circuit_2"
    for i in range(21):
        circ, a,q,g = circ_func(i/20)
        filled_results = get_probability_metrics(circ, q, a, ProbDiffResults(1))
        results_dict.update({i/20:filled_results})

    plot_results_angles(results_dict, figname=f'Plot_var_angles_{circ_name}',
                 image_write_path="final_eval_folder/specific_plots/plots_var_angles")
    

if __name__=="__main__":
    metrics_for_angles(static_circuit_1)
    metrics_for_angles(static_circuit_2)
    