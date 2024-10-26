import os
import logging
import random
import sys
import time
from typing import Literal
import gc

from matplotlib import pyplot as plt
import numpy
from qiskit import QuantumCircuit, qpy
import rustworkx

from helperfunctions.randomcircuit import random_quantum_circuit_basic, random_quantum_circuit_large
from helperfunctions.uncompfunctions import add_uncomputation, exhaustive_uncomputation_adding, greedy_uncomputation_full, greedy_uncomputation_partial
from helperfunctions.circuitgraphfunctions import get_computation_graph, get_uncomp_circuit
from helperfunctions.constants import EVAL_DIRS, UncompType

from helperfunctions.measurecircuit import get_statevector, get_probability_from_statevector, zero_ancillas_in_statevector, print_probs

from helperfunctions.graphhelper import breakdown_qubit, edge_attr, node_attr, node_matcher, edge_matcher
from rustworkx.visualization import graphviz_draw

# logging.config.fileConfig('logger.config')
logger = logging.getLogger(__name__)
start_time = 0

# class CircuitMetrics:
#     def __init__(self, name_str, num_q, num_a, num_g):
#         self.name_str = name_str
#         self.num_q = num_q
#         self.num_a = num_a
#         self.num_g = num_g

#         self.exhaustive_uncomp_gates = None



#         pass


class EvaluationMetrics:
    def __init__(self, num_circuits):
        self.num_circuits = num_circuits
        self.can_be_regularly_uncomputed = 0
        self.greedy_and_exhaustive_return_same = 0
        # self.exhaustive_eval = {'uncomp_closer': 0, 'uncomp_same':0, 'uncomp_worse':0}
        # self.greedy_full_eval = {'uncomp_closer': 0, 'uncomp_same':0, 'uncomp_worse':0}
        # self.greedy_partial_eval = {'uncomp_closer': 0, 'uncomp_same':0, 'uncomp_worse':0}
        self.uncomp_better = {x:0 for x in UncompType}
        self.uncomp_same = {x:0 for x in UncompType}
        self.uncomp_worse = {x:0 for x in UncompType}


def evaluate_circuits(comp_circuit: QuantumCircuit, uncomp_circuit: QuantumCircuit, num_a, name_str,
                          metric:EvaluationMetrics, uncomp_type:UncompType='regular'):
    
    eq4_comp_statevector = get_statevector(comp_circuit)
    eq4_comp_prob_dist = get_probability_from_statevector(eq4_comp_statevector)
    # logger.info(f'Comp Circuit {name_str} Eq4 Probability Distribution: \n{print_probs(eq4_comp_prob_dist)}')

    eq5_comp_statevector = zero_ancillas_in_statevector(eq4_comp_statevector, num_a)
    eq5_comp_prob_dist = get_probability_from_statevector(eq5_comp_statevector)
    # logger.info(f'Comp Circuit {name_str} Eq5 Probability Distribution: \n{print_probs(eq5_comp_prob_dist)}')

    eq4_uncomp_statevector = get_statevector(uncomp_circuit)
    eq4_uncomp_prob_dist = get_probability_from_statevector(eq4_uncomp_statevector)
    # logger.info(f'{uncomp_type.capitalize()} Uncomp Circuit {name_str} Eq4 Probability Distribution: \n{print_probs(eq4_uncomp_prob_dist)}')

    distance_probs_eq5_4_comp = numpy.linalg.norm(eq5_comp_prob_dist - eq4_comp_prob_dist)
    distance_probs_eq5_4_uncomp = numpy.linalg.norm(eq4_uncomp_prob_dist - eq5_comp_prob_dist)
    
    distance_probs_eq5_4_comp, distance_probs_eq5_4_uncomp = numpy.round((distance_probs_eq5_4_comp, distance_probs_eq5_4_uncomp), decimals=10)

    logger.info(f'The distance between the probability distributions of Eq4 and Eq5 for Circuit {name_str} are {distance_probs_eq5_4_comp}')
    logger.info(f'The distance between the probability distributions of Comp Eq5  and {uncomp_type.value.capitalize()} Uncomp for Circuit {name_str} are {distance_probs_eq5_4_uncomp}')


    if distance_probs_eq5_4_uncomp < distance_probs_eq5_4_comp:
        logger.info(f'{uncomp_type.value.capitalize()} Uncomputation of Circuit {name_str} is closer to Eq5 than Eq4')
        metric.uncomp_better[uncomp_type] += 1

    elif distance_probs_eq5_4_uncomp == distance_probs_eq5_4_comp:
        logger.info(f'{uncomp_type.value.capitalize()} Uncomputation of Circuit {name_str} is the same to Eq5 as Eq4')
        metric.uncomp_same[uncomp_type] += 1
        
    else:
        logger.info(f'{uncomp_type.value.capitalize()} Uncomputation of Circuit {name_str} is farther to Eq5 than Eq4')
        metric.uncomp_worse[uncomp_type] += 1
        

def simple_circuit_with_a2_uncomputable():
    circuit = QuantumCircuit(6)

    for i in range(3):
        circuit.h(i)
        circuit.cx(i,i+3)

    circuit.cx(4,1)

    return circuit, 3, 3, 7

def simple_circuit_with_partial_uncomp():
    '''
    The circuit's form is \n
     ┌───┐          ┌───┐                          \n
q_0: ┤ H ├──■───────┤ X ├───────────────────────── \n
     ├───┤  │       └─┬─┘                          \n
q_1: ┤ H ├──┼────■────┼─────────────────────────── \n
     ├───┤  │    │    │                            \n
q_2: ┤ H ├──┼────┼────┼──────────────■──────────── \n
     └───┘┌─┴─┐┌─┴─┐  │  ┌───┐     ┌─┴─┐     ┌───┐ \n
q_3: ─────┤ X ├┤ X ├──■──┤ X ├──■──┤ X ├──■──┤ X ├ \n
          └───┘└───┘     └─┬─┘┌─┴─┐└───┘┌─┴─┐└─┬─┘ \n
q_4: ──────────────────────■──┤ X ├─────┤ X ├──■── \n
                              └───┘     └───┘      \n
q_5: ───────────────────────────────────────────── \n
                                                  
    '''

    circuit = QuantumCircuit(6)

    for i in range(3):
        circuit.h(i)
        # circuit.cx(i,i+3)
        
    circuit.cx(0,3)
    circuit.cx(1,3)
    
    
    circuit.cx(3,0)
    
    circuit.cx(4,3)
    circuit.cx(3,4)
    
    circuit.cx(2,3)
    
    circuit.cx(3,4)
    circuit.cx(4,3)
    
    # circuit.cx(0,5)
    # circuit.cx(1,5)
    # circuit.cx(2,5)


    return circuit,3,3,11


def eval_main_func(num_circuits, eval_dir='evaluation_folder'):
    logger.info(f'Starting Evaluation of Exhaustive Uncomp with {num_circuits} random quantum circuits')
    global start_time
    valid_num_circuits = num_circuits if num_circuits > 0 else 1

    metrics = EvaluationMetrics(valid_num_circuits)

    print('****************************************************************************')
    for i in range(valid_num_circuits):
        if num_circuits > 0:

            logger.info(f'Generating Random Circuit {i}')
            # _circuit, num_q, num_a, num_g = random_quantum_circuit_basic()
            _circuit, num_q, num_a, num_g = random_quantum_circuit_large()

        else:
            _circuit, num_q, num_a, num_g = simple_circuit_with_partial_uncomp()
            

        name_str = f'Circuit_{i}'

        _circuit.draw('latex', 
                     filename=f'{eval_dir}/comp_circuit/{name_str}.png')
        
        with open(f'{eval_dir}/comp_circuit_qpy/{name_str}.qpy', 'wb') as f:
            qpy.dump(_circuit, f)
            f.close()
        
        logger.info(f'Building Random Circuit took {time.time_ns()-start_time} ns')
        start_time = time.time_ns()
        logger.info(f'Creating Circuit Graph of circuit {name_str}')
        ancillas_list = [breakdown_qubit(q)['label'] for q in _circuit.qubits][-num_a:]
        _circuit_graph = get_computation_graph(_circuit, ancillas_list)

        # graphviz_draw(_circuit_graph,
        #               node_attr_fn=node_attr,
        #               edge_attr_fn=edge_attr,
        #               filename=f'{eval_dir}/comp_circuit_graph/{name_str}.png')

        logger.info(f'Building Circuit Graph took {time.time_ns()-start_time} ns')
        start_time = time.time_ns()
        
        if rustworkx.digraph_find_cycle(_circuit_graph):
            print(f'Computation Graph has cycles !!!!')
            logger.error(f'Computation Circuit Graph for circuit {name_str} has cycles!!')
            for cycle in rustworkx.simple_cycles(_circuit_graph):
                print(cycle)
                logger.error(f'Cycle in {name_str} : {cycle}')

        logger.info(f'Checking for cycle in Comp Circuit Graph took {time.time_ns()-start_time} ns')
        start_time = time.time_ns()
        
        _regular_uncomp_circuit_graph, has_cycle = add_uncomputation(_circuit_graph, ancillas_list)

        logger.info(f'Adding Uncomputation to circuit graph took {time.time_ns()-start_time} ns')
        start_time = time.time_ns()

        if has_cycle:
            logger.warning(f'Trying to uncompute circuit {name_str} produces a cycle')

            logger.info(f'Attempting to run exhaustive uncomp on {name_str}')
            largest_set = exhaustive_uncomputation_adding(_circuit_graph, ancillas_list)
            logger.info(f'Largest Set of ancilla for {name_str} that can be uncomputed is {largest_set}')
            logger.info(f'Time to find largest set took {time.time_ns()-start_time} ns')
            start_time = time.time_ns()
            _exhaustive_uncomp_circuit_graph, has_cycle = add_uncomputation(_circuit_graph, list(largest_set))
            if has_cycle:
                logger.error(f'Exhaustive Uncomp of {name_str} still has cycle')
            
            # logger.info(f'Drawing Exhaustive Uncomp Circuit Graph for {name_str}')
            # graphviz_draw(_exhaustive_uncomp_circuit_graph,
            #           node_attr_fn=node_attr,
            #           edge_attr_fn=edge_attr,
            #           filename=f'{eval_dir}/exhaustive_uncomp_graph/{name_str}.png')

            logger.info(f'Adding Uncomp for largest set took {time.time_ns()-start_time} ns')
            start_time = time.time_ns()

            logger.info(f'Building Exhaustive Uncomp Circuit for {name_str}')
            _exhaustive_uncomp_circuit = get_uncomp_circuit(_exhaustive_uncomp_circuit_graph)
            _exhaustive_uncomp_circuit.draw('latex', filename=f'{eval_dir}/exhaustive_uncomp_circuit/{name_str}.png')

            logger.info(f'Time to build uncomp circuit took {time.time_ns()-start_time} ns')
            start_time = time.time_ns()

            
            evaluate_circuits(comp_circuit=_circuit, 
                              uncomp_circuit=_exhaustive_uncomp_circuit, 
                              num_a=num_a, name_str=name_str, metric=metrics, uncomp_type=UncompType.EXHAUSTIVE)
            

            with open(f'{eval_dir}/exhaustive_uncomp_circuit_qpy/{name_str}.qpy', 'wb') as f:
                qpy.dump(_exhaustive_uncomp_circuit, f)
                f.close()
            

# ***************************************************************************************************************#
            logger.info(f'Attempting to run greedy uncomp on {name_str}')
            _greedy_uncomp_circuit_graph = greedy_uncomputation_full(_circuit_graph, ancillas_list, max_cycles=5*(10**5))
            
            logger.info(f'Drawing Greedy Uncomp Circuit Graph for {name_str}')
            # graphviz_draw(_greedy_uncomp_circuit_graph,
            #           node_attr_fn=node_attr,
            #           edge_attr_fn=edge_attr,
            #           filename=f'{eval_dir}/greedy_uncomp_graph/{name_str}.png')

            logger.info(f'Building Greedy Uncomp Circuit for {name_str}')
            _greedy_uncomp_circuit = get_uncomp_circuit(_greedy_uncomp_circuit_graph)
            _greedy_uncomp_circuit.draw('latex', filename=f'{eval_dir}/greedy_uncomp_circuit/{name_str}.png')


            evaluate_circuits(comp_circuit=_circuit, 
                              uncomp_circuit=_greedy_uncomp_circuit, 
                              num_a=num_a, name_str=name_str, metric=metrics, uncomp_type=UncompType.GREEDY_FULL)
            

            with open(f'{eval_dir}/greedy_uncomp_circuit_qpy/{name_str}.qpy', 'wb') as f:
                qpy.dump(_greedy_uncomp_circuit, f)
                f.close()
            

#**************************************************************************************************************#
            logger.info(f'Comparing the uncomp circuit grapphs by greedy and exhaustive for {name_str}')
            if rustworkx.is_isomorphic(_greedy_uncomp_circuit_graph, _exhaustive_uncomp_circuit_graph,
                                       node_matcher=node_matcher, edge_matcher=edge_matcher):
                logger.info(f'Both methods return the same circuit graphs')
                metrics.greedy_and_exhaustive_return_same += 1
            else:
                logger.info(f'Both methods return different circuit graphs')

#**************************************************************************************************************#
            logger.info(f'Attempting to run greedy partial uncomp on {name_str}')
            _greedy_partial_uncomp_circuit_graph = greedy_uncomputation_partial(_circuit_graph, ancillas_list, max_cycles=5*(10**5))
            
            logger.info(f'Drawing Greedy Partial Uncomp Circuit Graph for {name_str}')
            # graphviz_draw(_greedy_partial_uncomp_circuit_graph,
            #           node_attr_fn=node_attr,
            #           edge_attr_fn=edge_attr,
            #           filename=f'{eval_dir}/greedy_partial_uncomp_graph/{name_str}.png')

            logger.info(f'Building Greedy Partial Uncomp Circuit for {name_str}')
            _greedy_partial_uncomp_circuit = get_uncomp_circuit(_greedy_partial_uncomp_circuit_graph)
            _greedy_partial_uncomp_circuit.draw('latex', filename=f'{eval_dir}/greedy_partial_uncomp_circuit/{name_str}.png')

            evaluate_circuits(comp_circuit=_circuit, 
                              uncomp_circuit=_greedy_partial_uncomp_circuit, 
                              num_a=num_a, name_str=name_str, metric=metrics, uncomp_type=UncompType.GREEDY_PARTIAL) 

            with open(f'{eval_dir}/greedy_partial_uncomp_circuit_qpy/{name_str}.qpy', 'wb') as f:
                qpy.dump(_greedy_partial_uncomp_circuit, f)
                f.close()
#**************************************************************************************************************#
        else:
            logger.info(f'Drawing Regular Uncomp Circuit Graph for {name_str}')
            # graphviz_draw(_regular_uncomp_circuit_graph,
            #           node_attr_fn=node_attr,
            #           edge_attr_fn=edge_attr,
            #           filename=f'{eval_dir}/regular_uncomp_graph/{name_str}.png')
            
            logger.info(f'Building Regular Uncomp Circuit for {name_str}')
            _uncomp_circuit = get_uncomp_circuit(_regular_uncomp_circuit_graph)
            _uncomp_circuit.draw('latex', filename=f'{eval_dir}/regular_uncomp_circuit/{name_str}.png')

            evaluate_circuits(comp_circuit=_circuit, 
                              uncomp_circuit=_uncomp_circuit, 
                              num_a=num_a, name_str=name_str, metric=metrics, uncomp_type=UncompType.REGULAR)
            
            metrics.can_be_regularly_uncomputed += 1

            with open(f'{eval_dir}/regular_uncomp_circuit_qpy/{name_str}.qpy', 'wb') as f:
                qpy.dump(_uncomp_circuit, f)
                f.close()

        # Collect and free all memory
        # # Clear the current axes.
        # plt.cla() 
        # # Clear the current figure.
        # plt.clf() 
        # # Closes all the figure windows.
        # plt.close('all')
        gc.collect()
#**************************************************************************************************************#

    logger.info(f'Evaluation Results:')
    logger.info(f'Exhaustive and Greedy produced the same circuit in {metrics.greedy_and_exhaustive_return_same}')
    logger.info(f'Uncomputation was closer than Eq4 for {[(i.value,x) for i,x in metrics.uncomp_better.items()]}')
    logger.info(f'Uncomputation was same as Eq4 for {[(i.value,x) for i,x in metrics.uncomp_same.items()]}')
    logger.info(f'Uncomputation was worse than Eq4 for {[(i.value,x) for i,x in metrics.uncomp_worse.items()]}')

if __name__ == '__main__':
    
    print(sys.argv)
    logger.info(f'CMD Args - {sys.argv}')
    num_circuits = 0
    eval_dir = 'evaluation_folder'
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        num_circuits = int(sys.argv[1])
        
    if len(sys.argv) > 2:
        eval_dir = sys.argv[2]

    
    if not os.path.exists(eval_dir):
        os.mkdir(eval_dir)
        for dir in EVAL_DIRS:
            os.mkdir(os.path.join(eval_dir,dir))

        f1 = open(f'{eval_dir}/eval_logs.txt', 'x')
        f2 = open(f'{eval_dir}/eval.logs', 'x')
        f1.close()
        f2.close()


    logging.basicConfig(
        filename=f"{eval_dir}/eval.logs",
        format='%(asctime)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s',
        level=logging.INFO,
        filemode='w'
    )

    # Removing previous files from directory


    for path in os.listdir(eval_dir):
        p = os.path.join(eval_dir, path)
        if os.path.isdir(p):
            for file in os.listdir(p):
                f = os.path.join(p, file)
                if os.path.isfile(f):
                    os.remove(f)

    
    
    start_time = time.time_ns()
    eval_main_func(num_circuits, eval_dir)

    # Save all logging information
    f1 = open(f'{eval_dir}/eval_logs.txt', 'a+')
    f2 = open(f'{eval_dir}/eval.logs', 'r')

    f1.write(f2.read())

    f1.close()
    f2.close()

    print('****************************************************************************')
  