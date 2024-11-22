import os
import sys
import yaml
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
from helperfunctions.evaluation import ProbDiffResults, get_difference_in_prob, plot_results, plot_results_bar

def generate_circuits(num_q, num_a, num_g):
    circuit = random_quantum_circuit_large_with_params(
        num_q=num_q, num_a=num_a, num_g=num_g,
        add_random_h=True
    )

    
    cg = get_computation_graph(circuit)

