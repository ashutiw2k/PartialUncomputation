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

def get_probability_metrics(num_q, num_a, num_g, results=ProbDiffResults,
                            num_circuits=1, max_cycles=10**5, 
                            distance='manhattan'):
    for idx in range(num_circuits):
        name_str = f'Circuit_{idx}'
        print(f'***********************{name_str}***************************')

        _circuit, num_q, num_a, num_g = random_quantum_circuit_large_with_params(num_q, num_a, num_g, add_random_h=True, random_cz=0.5)
        ancillas_list = [breakdown_qubit(q)['label'] for q in _circuit.qubits][-num_a:]
        _circuit_graph = get_computation_graph(_circuit, ancillas_list)

        if rustworkx.digraph_find_cycle(_circuit_graph):
            print(f'Computation Circuit Graph for circuit {name_str} has cycles!!')
            break

        _regular_uncomp_circuit_graph, has_cycle = add_uncomputation(_circuit_graph, ancillas_list)

        if has_cycle:
            largest_set = exhaustive_uncomputation_adding(_circuit_graph, ancillas_list)
            print(f'Largest Set of ancilla for {name_str} that can be uncomputed is {largest_set}')
            # results.add_exhaustive(largest_set)

            _exhaustive_uncomp_circuit_graph, has_cycle = add_uncomputation(_circuit_graph, list(largest_set))
            if has_cycle:
                print(f'Exhaustive Uncomp of {name_str} still has cycle')
            
            _exhaustive_uncomp_circuit = get_uncomp_circuit(_exhaustive_uncomp_circuit_graph)
            ex_vals = get_difference_in_prob(_circuit, _exhaustive_uncomp_circuit,num_q, num_a, distance=distance)
            results.add_to_exhaustive(*ex_vals, idx=idx)


    # ***************************************************************************************************************#
            # logger.info(f'Attempting to run greedy uncomp on {name_str}')
            _greedy_uncomp_circuit_graph, gf_uncomp_ancillas = greedy_uncomputation_full(_circuit_graph, ancillas_list, 
                                                                     max_cycles=max_cycles, return_uncomputed_ancillas=True)
            
            _greedy_uncomp_circuit = get_uncomp_circuit(_greedy_uncomp_circuit_graph)
            gf_vals = get_difference_in_prob(_circuit, _greedy_uncomp_circuit, num_q, num_a, distance=distance)
            results.add_to_greedy_full(*gf_vals, idx=idx)

            # results.add_greedy_full(gf_uncomp_ancillas)

    #**************************************************************************************************************#
            # print(f'Comparing the uncomp circuit grapphs by greedy and exhaustive for {name_str}')
            # if rustworkx.is_isomorphic(_greedy_uncomp_circuit_graph, _exhaustive_uncomp_circuit_graph,
            #                             node_matcher=node_matcher, edge_matcher=edge_matcher):
            #     print(f'Both methods return the same circuit graphs')
            #     # metrics.greedy_and_exhaustive_return_same += 1
            # else:
            #     print(f'Both methods return different circuit graphs')

    #**************************************************************************************************************#
            # logger.info(f'Attempting to run greedy partial uncomp on {name_str}')
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

def metrics_for_ancillas(config):
    # Variable Number of Ancilla
    num_q = config['num_q']
    num_a_min = config['num_a_min']
    num_a_max = config['num_a_max']
    num_a_step = config['num_a_step']
    num_g = config['num_g']
    num_circuits = config['num_circuits']
    # global image_write_path
    image_write_path = config['paths']['image']
    # global image_write_path
    # global VALID_NUM_CIRCUITS

    distance=config['distance']

    results_dict = {}

    for var in range(num_a_min, num_a_max+num_a_step, num_a_step):
        filled_results = get_probability_metrics(num_q=num_q, num_g=num_g, num_a=var, 
                                             results=ProbDiffResults(num_circuits), num_circuits=num_circuits,
                                             distance=distance)
        results_dict.update({var:filled_results})  
        gc.collect()

    for a,r in results_dict.items():
        print(f'{a}:\n\t{r}')  

    # plot_results_bar(results_dict, figname=f'Plot_prob_dist_diff_{num_q}q_{num_g}g_{num_a_min}-{num_a_max}a_{distance}_bar',
    #              image_write_path=image_write_path, xlabel='Number of Ancillary Qubits')
    
    plot_results(results_dict, figname=f'Plot_prob_dist_diff_{num_q}q_{num_g}g_{num_a_min}-{num_a_max}a_{distance}',
                 image_write_path=image_write_path, xlabel='Number of Ancillary Qubits')
    
    
def metrics_for_inputs(config):
    # Variable Number of Ancilla
    num_a = config['num_a']
    num_q_min = config['num_q_min']
    num_q_max = config['num_q_max']
    num_q_step = config['num_q_step']
    num_g = config['num_g']
    num_circuits = config['num_circuits']
    # global image_write_path
    image_write_path = config['paths']['image']
    # global image_write_path
    # global VALID_NUM_CIRCUITS

    distance=config['distance']

    results_dict = {}

    for var in range(num_q_min, num_q_max+num_q_step, num_q_step):
        filled_results = get_probability_metrics(num_q=var, num_g=num_g, num_a=num_a, 
                                             results=ProbDiffResults(num_circuits), num_circuits=num_circuits,
                                             distance=distance)
        results_dict.update({var:filled_results})  
        gc.collect()

    for a,r in results_dict.items():
        print(f'{a}:\n\t{r}')  

    # plot_results_bar(results_dict, figname=f'Plot_prob_dist_diff_{num_q_min}-{num_q_max}q_{num_g}g_{num_a}a_{distance}_bar',
    #              image_write_path=image_write_path, xlabel='Number of Input Qubits')
    
    plot_results(results_dict, figname=f'Plot_prob_dist_diff_{num_q_min}-{num_q_max}q_{num_g}g_{num_a}a_{distance}',
                 image_write_path=image_write_path, xlabel='Number of Input Qubits')
    

def metrics_for_gates(config):
    # Variable Number of Ancilla
    num_q = config['num_q']
    num_g_min = config['num_g_min']
    num_g_max = config['num_g_max']
    num_g_step = config['num_g_step']
    num_a = config['num_a']
    num_circuits = config['num_circuits']
    # global image_write_path
    image_write_path = config['paths']['image']
    # global image_write_path
    # global VALID_NUM_CIRCUITS

    distance=config['distance']

    results_dict = {}

    for var in range(num_g_min, num_g_max+num_g_step, num_g_step):
        filled_results = get_probability_metrics(num_q=num_q, num_g=var, num_a=num_a, 
                                             results=ProbDiffResults(num_circuits), num_circuits=num_circuits, distance=distance)
        results_dict.update({var:filled_results}) 
        gc.collect() 

    for a,r in results_dict.items():
        print(f'{a}:\n\t{r}')  

    # plot_results_bar(results_dict, figname=f'Plot_prob_dist_diff_{num_q}q_{num_g_min}-{num_g_max}g_{num_a}a_{distance}_bar',
    #              image_write_path=image_write_path, xlabel='Number of (C-Not) Gates')

    plot_results(results_dict, figname=f'Plot_prob_dist_diff_{num_q}q_{num_g_min}-{num_g_max}g_{num_a}a_{distance}',
                 image_write_path=image_write_path, xlabel='Number of (C-Not) Gates')



if __name__ == '__main__':
    config_path = 'configs/default_config_ancilla.yaml'
    if len(sys.argv) < 2:
        print(f'Config File not provided, using default')
    else:
        config_path = sys.argv[1]

    with open(config_path) as f:
        # config = json.load(f)
        config = yaml.safe_load(f)

    print(config)

    if config['evaluation'] == 'ancilla':
        metrics_for_ancillas(config)

    elif config['evaluation'] == 'input':
        metrics_for_inputs(config)

    elif config['evaluation'] == 'gate':
        metrics_for_gates(config)

    

    # exit(0)

    # # Variable Number of Ancilla
    # num_q = config['num_q']
    # num_a_min = config['num_a_min']
    # num_a_max = config['num_a_max']
    # num_a_step = config['num_a_step']
    # num_g = config['num_g']
    # num_circuits = config['num_circuits']
    # # global image_write_path
    # image_write_path = config['paths']['image']
    # # global image_write_path
    # # global VALID_NUM_CIRCUITS

    # distance=config['distance']

    # results_dict = {}

    # for var in range(num_a_min, num_a_max+num_a_step, num_a_step):
    #     filled_results = get_probability_metrics(num_q=num_q, num_g=num_g, num_a=var, 
    #                                          results=ProbDiffResults(num_circuits), num_circuits=num_circuits)
    #     results_dict.update({var:filled_results})  

    # for a,r in results_dict.items():
    #     print(f'{a}:\n\t{r}')  

    # plot_results_bar(results_dict, figname=f'Plot_num_ancillas_uncomputed_{num_q}q_{num_g}g_{num_a_min}-{num_a_max}a_{distance}',
    #              image_write_path=image_write_path, xlabel='Number of Ancillary Qubits')
    