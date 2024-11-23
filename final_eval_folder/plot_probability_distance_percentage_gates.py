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
from helperfunctions.randomcircuit import random_quantum_circuit_varied_percentages
from helperfunctions.uncompfunctions import add_uncomputation, exhaustive_uncomputation_adding, greedy_uncomputation_full, greedy_uncomputation_partial
from helperfunctions.circuitgraphfunctions import get_computation_graph, get_uncomp_circuit
from helperfunctions.evaluation import ProbDiffResults, get_difference_in_prob, plot_results, plot_results_bar

def get_probability_metrics(num_q, num_a, num_g,
                            results=ProbDiffResults,
                            percent_aa_gates = 0.1,
                            percent_cc_gates = 0.8,
                            percent_ca_gates = 0.05,
                            percent_ac_gates = 0.05,
                            percent_add_h = 0.5, 
                            num_circuits=1, max_cycles=10**5, 
                            distance='manhattan'):
    for idx in range(num_circuits):
        name_str = f'Circuit_{idx}'
        print(f'***********************{name_str}***************************')

        _circuit, num_q, num_a, num_g = random_quantum_circuit_varied_percentages(
                                            num_q, num_a, num_g, add_random_h=True,
                                            percent_aa_gates = percent_aa_gates,
                                            percent_cc_gates = percent_cc_gates,
                                            percent_ca_gates = percent_ca_gates,
                                            percent_ac_gates = percent_ac_gates,
                                            percent_add_h = percent_add_h)
        
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

def metrics_for_cc_gates(config):
    # Variable Number of Ancilla
    num_q = config['num_q']
    num_a = config['num_a']
    num_g = config['num_g']
    num_circuits = config['num_circuits']
    
    # global image_write_path
    image_write_path = config['paths']['image']
    # global image_write_path
    # global VALID_NUM_CIRCUITS

    distance=config['distance']

    results_dict = {}

    for var in range(0,100,10):
        val=var/100
        non_var=(1-val)/3

        p_cc = val
        p_ac = non_var
        p_ca = non_var
        p_aa = non_var
        
        filled_results = get_probability_metrics(num_q=num_q, num_g=num_g, num_a=num_a, 
                                             results=ProbDiffResults(num_circuits), num_circuits=num_circuits,
                                             percent_cc_gates=p_cc,
                                             percent_aa_gates=p_aa,
                                             percent_ac_gates=p_ac,
                                             percent_ca_gates=p_ca,
                                             distance=distance)
        results_dict.update({var:filled_results})  
        gc.collect()

    for a,r in results_dict.items():
        print(f'{a}:\n\t{r}')  

    # plot_results_bar(results_dict, figname=f'Plot_prob_dist_diff_{num_q}q_{num_g}g_{num_a_min}-{num_a_max}a_{distance}_bar',
    #              image_write_path=image_write_path, xlabel='Number of Ancillary Qubits')
    
    plot_results(results_dict, figname=f'Plot_prob_dist_diff_{num_q}q_{num_g}g_{num_a}a_{distance}_percent_cc',
                 image_write_path=image_write_path, xlabel='Percentage Of Control-Control Gates')


def metrics_for_ca_gates(config):
    # Variable Number of Ancilla
    num_q = config['num_q']
    num_a = config['num_a']
    num_g = config['num_g']
    num_circuits = config['num_circuits']
    
    # global image_write_path
    image_write_path = config['paths']['image']
    # global image_write_path
    # global VALID_NUM_CIRCUITS

    distance=config['distance']

    results_dict = {}

    for var in range(0,100,10):
        val=var/100
        non_var=(1-val)/3

        p_cc = non_var
        p_ac = non_var
        p_ca = val
        p_aa = non_var
        
        filled_results = get_probability_metrics(num_q=num_q, num_g=num_g, num_a=num_a, 
                                             results=ProbDiffResults(num_circuits), num_circuits=num_circuits,
                                             percent_cc_gates=p_cc,
                                             percent_aa_gates=p_aa,
                                             percent_ac_gates=p_ac,
                                             percent_ca_gates=p_ca,
                                             distance=distance)
        results_dict.update({var:filled_results})  
        gc.collect()

    for a,r in results_dict.items():
        print(f'{a}:\n\t{r}')  

    # plot_results_bar(results_dict, figname=f'Plot_prob_dist_diff_{num_q}q_{num_g}g_{num_a_min}-{num_a_max}a_{distance}_bar',
    #              image_write_path=image_write_path, xlabel='Number of Ancillary Qubits')
    
    plot_results(results_dict, figname=f'Plot_prob_dist_diff_{num_q}q_{num_g}g_{num_a}a_{distance}_percent_ca',
                 image_write_path=image_write_path, xlabel='Percentage Of Control-Ancilla Gates')


def metrics_for_ac_gates(config):
    # Variable Number of Ancilla
    num_q = config['num_q']
    num_a = config['num_a']
    num_g = config['num_g']
    num_circuits = config['num_circuits']
    
    # global image_write_path
    image_write_path = config['paths']['image']
    # global image_write_path
    # global VALID_NUM_CIRCUITS

    distance=config['distance']

    results_dict = {}

    for var in range(0,100,10):
        val=var/100
        non_var=(1-val)/3

        p_cc = non_var
        p_ac = val
        p_ca = non_var
        p_aa = non_var
        
        filled_results = get_probability_metrics(num_q=num_q, num_g=num_g, num_a=num_a, 
                                             results=ProbDiffResults(num_circuits), num_circuits=num_circuits,
                                             percent_cc_gates=p_cc,
                                             percent_aa_gates=p_aa,
                                             percent_ac_gates=p_ac,
                                             percent_ca_gates=p_ca,
                                             distance=distance)
        results_dict.update({var:filled_results})  
        gc.collect()

    for a,r in results_dict.items():
        print(f'{a}:\n\t{r}')  

    # plot_results_bar(results_dict, figname=f'Plot_prob_dist_diff_{num_q}q_{num_g}g_{num_a_min}-{num_a_max}a_{distance}_bar',
    #              image_write_path=image_write_path, xlabel='Number of Ancillary Qubits')
    
    plot_results(results_dict, figname=f'Plot_prob_dist_diff_{num_q}q_{num_g}g_{num_a}a_{distance}_percent_ac',
                 image_write_path=image_write_path, xlabel='Percentage Of Ancilla-Control Gates')


def metrics_for_aa_gates(config):
    # Variable Number of Ancilla
    num_q = config['num_q']
    num_a = config['num_a']
    num_g = config['num_g']
    num_circuits = config['num_circuits']
    
    # global image_write_path
    image_write_path = config['paths']['image']
    # global image_write_path
    # global VALID_NUM_CIRCUITS

    distance=config['distance']

    results_dict = {}

    for var in range(0,100,10):
        val=var/100
        non_var=(1-val)/3
        
        p_cc = non_var
        p_ac = non_var
        p_ca = non_var
        p_aa = val
        
        filled_results = get_probability_metrics(num_q=num_q, num_g=num_g, num_a=num_a, 
                                             results=ProbDiffResults(num_circuits), num_circuits=num_circuits,
                                             percent_cc_gates=p_cc,
                                             percent_aa_gates=p_aa,
                                             percent_ac_gates=p_ac,
                                             percent_ca_gates=p_ca,
                                             distance=distance)
        results_dict.update({var:filled_results})  
        gc.collect()

    for a,r in results_dict.items():
        print(f'{a}:\n\t{r}')  

    # plot_results_bar(results_dict, figname=f'Plot_prob_dist_diff_{num_q}q_{num_g}g_{num_a_min}-{num_a_max}a_{distance}_bar',
    #              image_write_path=image_write_path, xlabel='Number of Ancillary Qubits')
    
    plot_results(results_dict, figname=f'Plot_prob_dist_diff_{num_q}q_{num_g}g_{num_a}a_{distance}_percent_aa',
                 image_write_path=image_write_path, xlabel='Percentage Of Ancilla-Ancilla Gates')



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

    if config['evaluation'] == 'percent_cc':
        metrics_for_cc_gates(config)
    if config['evaluation'] == 'percent_ca':
        metrics_for_ca_gates(config)
    if config['evaluation'] == 'percent_ac':
        metrics_for_ac_gates(config)
    if config['evaluation'] == 'percent_aa':
        metrics_for_aa_gates(config)


    

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
    #     filled_results = get_probability_metrics(num_q=num_q, num_g=num_g, num_a=num_a, 
    #                                          results=ProbDiffResults(num_circuits), num_circuits=num_circuits)
    #     results_dict.update({var:filled_results})  

    # for a,r in results_dict.items():
    #     print(f'{a}:\n\t{r}')  

    # plot_results_bar(results_dict, figname=f'Plot_num_ancillas_uncomputed_{num_q}q_{num_g}g_{num_a_min}-{num_a_max}a_{distance}',
    #              image_write_path=image_write_path, xlabel='Number of Ancillary Qubits')
    