import os
import logging
import random
import sys

from qiskit import QuantumCircuit

from helperfunctions.randomcircuit import random_quantum_circuit
from helperfunctions.uncompfunctions import add_uncomputation, exhaustive_uncomputation_adding, greedy_uncomputation
from helperfunctions.circuitgraphfunctions import get_computation_graph, get_uncomp_circuit

from helperfunctions.graphhelper import edge_attr, node_attr
from rustworkx.visualization import graphviz_draw

# logging.config.fileConfig('logger.config')
logger = logging.getLogger(__name__)

def simple_circuit_with_a2_uncomputable():
    circuit = QuantumCircuit(6)

    for i in range(3):
        circuit.cx(i,i+3)

    circuit.cx(4,1)

    return circuit


def eval_main_func(num_circuits):
    logger.info(f'Starting Evaluation with {num_circuits} random quantum circuits')
    print('****************************************************************************')
    for i in range(num_circuits):
        if num_circuits > 1:
            num_q = random.randint(3,8)
            num_a = random.randint(3,8)
            num_g = random.randint(8,20)

            logger.info(f'Generating Random Circuit {i} with {num_q} input, {num_a} ancilla and {num_g} gates')
            _circuit = random_quantum_circuit(num_q,num_a,num_g)

        else:
            _circuit = simple_circuit_with_a2_uncomputable()
            num_q = 3
            num_a = 3

        name_str = f'Circuit_{i}'

        _circuit.draw('mpl', 
                     filename=f'evaluation_folder/comp_circuit/{name_str}.png')
        
        logger.info(f'Creating Circuit Graph of circuit {name_str}')
        _circuit_graph = get_computation_graph(_circuit, num_q)

        graphviz_draw(_circuit_graph,
                      node_attr_fn=node_attr,
                      edge_attr_fn=edge_attr,
                      filename=f'evaluation_folder/comp_circuit_graph/{name_str}.png')
        
        _regular_uncomp_circuit_graph, has_cycle = add_uncomputation(_circuit_graph, range(num_q,num_q+num_a))

        if has_cycle:
            logger.warning(f'Trying to uncompute circuit {name_str} produces a cycle')

            logger.info(f'Attempting to run exhaustive uncomp on {name_str}')
            largest_set = exhaustive_uncomputation_adding(_circuit_graph, num_q, num_a)
            logger.info(f'Largest Set of ancilla for {name_str} that can be uncomputed is {largest_set}')
            _exhaustive_uncomp_circuit_graph, has_cycle = add_uncomputation(_circuit_graph, list(largest_set))
            if has_cycle:
                logger.error(f'Exhaustive Uncomp of {name_str} still has cycle')
            
            logger.info(f'Drawing Exhaustive Uncomp Circuit Graph for {name_str}')
            graphviz_draw(_exhaustive_uncomp_circuit_graph,
                      node_attr_fn=node_attr,
                      edge_attr_fn=edge_attr,
                      filename=f'evaluation_folder/exhaustive_uncomp_graph/{name_str}.png')

            logger.info(f'Building Exhaustive Uncomp Circuit for {name_str}')
            _exhaustive_uncomp_circuit = get_uncomp_circuit(_exhaustive_uncomp_circuit_graph)
            _exhaustive_uncomp_circuit.draw('mpl', filename=f'evaluation_folder/exhaustive_uncomp_circuit/{name_str}.png')

# ***************************************************************************************************************#
            logger.info(f'Attempting to run greedy uncomp on {name_str}')
            _greedy_uncomp_circuit_graph = greedy_uncomputation(_circuit_graph, num_q, num_a)
            
            logger.info(f'Drawing Greedy Uncomp Circuit Graph for {name_str}')
            graphviz_draw(_greedy_uncomp_circuit_graph,
                      node_attr_fn=node_attr,
                      edge_attr_fn=edge_attr,
                      filename=f'evaluation_folder/greedy_uncomp_graph/{name_str}.png')

            logger.info(f'Building Greedy Uncomp Circuit for {name_str}')
            _greedy_uncomp_circuit = get_uncomp_circuit(_greedy_uncomp_circuit_graph)
            _greedy_uncomp_circuit.draw('mpl', filename=f'evaluation_folder/greedy_uncomp_circuit/{name_str}.png')

        else:
            logger.info(f'Drawing Regular Uncomp Circuit Graph for {name_str}')
            graphviz_draw(_regular_uncomp_circuit_graph,
                      node_attr_fn=node_attr,
                      edge_attr_fn=edge_attr,
                      filename=f'evaluation_folder/regular_uncomp_graph/{name_str}.png')
            
            logger.info(f'Building Regular Uncomp Circuit for {name_str}')
            _uncomp_circuit = get_uncomp_circuit(_regular_uncomp_circuit_graph)
            _uncomp_circuit.draw('mpl', filename=f'evaluation_folder/regular_uncomp_circuit/{name_str}.png')


if __name__ == '__main__':
    
    num_circuits = 1
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        num_circuits = int(sys.argv[1])

    logging.basicConfig(
        filename="evaluation_folder/eval.logs",
        format='%(asctime)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s',
        level=logging.INFO,
        filemode='w'
    )

    # Removing previous files from directory
    eval_dir = 'evaluation_folder'
    for path in os.listdir(eval_dir):
        p = os.path.join(eval_dir, path)
        if os.path.isdir(p):
            for file in os.listdir(p):
                f = os.path.join(p, file)
                if os.path.isfile(f):
                    os.remove(f)
    

    eval_main_func(num_circuits)

    # Save all logging information
    f1 = open('evaluation_folder/eval_logs.txt', 'a+')
    f2 = open('evaluation_folder/eval.logs', 'r')

    f1.write(f2.read())

    f1.close()
    f2.close()

    print('****************************************************************************')
  