import collections
import copy
from itertools import chain, combinations
from typing import Dict, List
import logging
import rustworkx

from .constants import StringConstants, ListConstants
from .graphhelper import CGNode


ANCILLA = StringConstants.ANCILLA.value

COMP = StringConstants.COMP.value
UNCOMP = StringConstants.UNCOMP.value

TARGET = StringConstants.TARGET.value
CONTROL = StringConstants.CONTROL.value
ANTIDEP = StringConstants.ANTIDEP.value

NON_QFREE = ListConstants.NON_QFREE.value

logger = logging.getLogger(__name__)

def get_uncomp_node_index(circuit_graph: rustworkx.PyDiGraph, node_index):
    for node in circuit_graph.nodes():
        if node.node_type is UNCOMP \
            and node.qubit_wire == circuit_graph.get_node_data(node_index).qubit_wire \
            and node.get_nodenum() == circuit_graph.get_node_data(node_index).get_nodenum():
            
            return node.get_index()
    return node_index

def get_comp_node_index(circuit_graph: rustworkx.PyDiGraph, node_index):
    for node in circuit_graph.nodes():
        if node.node_type is not UNCOMP \
            and node.qubit_wire == circuit_graph.get_node_data(node_index).qubit_wire \
            and node.get_nodenum() == circuit_graph.get_node_data(node_index).get_nodenum():

            return node.get_index()
    return node_index


def add_uncomputation_step(circuit_graph: rustworkx.PyDiGraph, idx):
    '''
    PLDI's UncompStep implementation
    '''

    node = circuit_graph.get_node_data(idx)
    node_adj = circuit_graph.adj_direction(idx, True)

    assert node.opname not in NON_QFREE

    try:
        node_controls_idx = list(map(lambda x: x[0], list(filter(lambda x: x[1] == CONTROL, list(node_adj.items())))))
    except IndexError:
        node_controls_idx = []

    print(node_controls_idx)

    node_controls_idx_uncomp = list(map(lambda x: get_uncomp_node_index(circuit_graph, x), node_controls_idx))
    print(node_controls_idx_uncomp)

    prev_node_index = node.get_index()
    for n in circuit_graph.nodes():
        if n.qubit_wire == node.qubit_wire and n.node_type is UNCOMP and n.get_nodenum() == node.get_nodenum():
            prev_node_index = n.get_index()

    print(prev_node_index)

    uncomp_node = CGNode(node.qubit_dict, qubit_type=node.qubit_type, node_type=UNCOMP, opname=node.opname)
    # uncomp_node_index = circuit_graph.add_node(uncomp_node)
    uncomp_node_index = circuit_graph.add_child(prev_node_index, uncomp_node, TARGET)
    circuit_graph.get_node_data(uncomp_node_index).set_index(uncomp_node_index)
    circuit_graph.get_node_data(uncomp_node_index).set_nodenum(
        circuit_graph.get_node_data(node.get_index()).get_nodenum() - 1
    )

    # Adding Control Edges and the antidep of control edges. 
    for control_idx in node_controls_idx_uncomp:
        circuit_graph.add_edge(control_idx, uncomp_node_index, CONTROL)

        controls_adj = circuit_graph.adj_direction(control_idx, False)
        try:
            controls_target_idx = list(map(lambda x: x[0], list(filter(lambda x: x[1] == TARGET and not circuit_graph.has_edge(x[0], uncomp_node_index), list(controls_adj.items())))))
        except IndexError:
            controls_target_idx = []

        for idx in controls_target_idx:
            circuit_graph.add_edge(uncomp_node_index, idx, ANTIDEP)


    prev_node_adj = circuit_graph.adj_direction(prev_node_index, False)
    print(prev_node_adj)
    try:
        prev_node_controlled_idx = list(map(lambda x: x[0], list(filter(lambda x: x[1] == CONTROL and not circuit_graph.has_edge(x[0], uncomp_node_index), list(prev_node_adj.items())))))
    except IndexError:
        prev_node_controlled_idx = []

    for idx in prev_node_controlled_idx:
        circuit_graph.add_edge(idx, uncomp_node_index, ANTIDEP)


    print(uncomp_node)

    print('----------------------------------------')


    return rustworkx.digraph_find_cycle(circuit_graph)

def add_uncomputation(circuit_graph: rustworkx.PyDiGraph, ancillas:List[int], allow_cycle=False):
    '''
    PLDI's Uncomp implementation
    '''
    uncomp_circuit_graph = copy.deepcopy(circuit_graph)
    graph_nodes_reverse = list(rustworkx.topological_sort(copy.deepcopy(circuit_graph)))
    graph_nodes_reverse.reverse()
    print(graph_nodes_reverse)
    for idx in graph_nodes_reverse:
        if circuit_graph.get_node_data(idx).qubit_wire in ancillas and circuit_graph.get_node_data(idx).node_type is COMP:
            cycle = add_uncomputation_step(uncomp_circuit_graph, idx)

            if not allow_cycle and len(cycle) > 0:
                print(f'Adding Uncomp node for {uncomp_circuit_graph.get_node_data(idx).graph_label()} creates a cycle of nodes => {cycle}:')
                for id in cycle:
                    print(uncomp_circuit_graph.get_node_data(id[0]).graph_label(), uncomp_circuit_graph.get_node_data(id[1]).graph_label(), sep=' --> ')

                return uncomp_circuit_graph, True

    return uncomp_circuit_graph, False


def exhaustive_uncomputation_adding(circuit_graph: rustworkx.PyDiGraph, num_qubit, num_ancilla):
    '''
    Exhaustively iterate over adding uncomputation for all possible ancillas
    '''
    
    ancillas = list(range(num_qubit, num_qubit+num_ancilla))
    ancillas_power_set = chain.from_iterable(combinations(ancillas, r) for r in range(len(ancillas)+1))
    largest_uncomputable = ()
    for ancilla_set in ancillas_power_set:
        # uncomp_circuit_graph = copy.deepcopy(circuit_graph)
        uncomp_circuit_graph, has_cycle = add_uncomputation(circuit_graph, list(ancilla_set))
        
        if not has_cycle and len(ancilla_set) > len(largest_uncomputable):
            largest_uncomputable = ancilla_set

    return largest_uncomputable
    

def remove_uncomputation_step(uncomp_circuit_graph: rustworkx.PyDiGraph, idx):
    comp_node_index = get_comp_node_index(uncomp_circuit_graph, idx)

    adj_nodes = uncomp_circuit_graph.adj_direction(idx, False) # Get all outbound edges
    print(adj_nodes)

    try:
        controlled_idx = list(map(lambda x: x[0], list(filter(lambda x: x[1] == CONTROL, list(adj_nodes.items())))))
    except IndexError:
        controlled_idx = []

    print(controlled_idx)

    uncomp_circuit_graph.remove_node(idx)
    
    for idx in controlled_idx:
        uncomp_circuit_graph.add_edge(comp_node_index, idx, CONTROL)
        
        adj_edges_leaving = uncomp_circuit_graph.adj_direction(comp_node_index, False)
        next_node_idx = list(filter(lambda x: adj_edges_leaving[x] is TARGET, adj_edges_leaving.keys()))
            # list(map(lambda x: x[0], list(filter(lambda x: x[1] == TARGET and not uncomp_circuit_graph.has_edge(x[0], idx), list(adj_edges_leaving.items())))))
        if len(next_node_idx) > 1:
            raise ValueError.add_note(f'searching for targets returned more than one value : {next_node_idx}') 
    
        uncomp_circuit_graph.add_edge(idx, next_node_idx[0], ANTIDEP)


def remove_uncomputation_full(uncomp_circuit_graph:rustworkx.PyDiGraph, ancillas):
    circuit_graph = copy.deepcopy(uncomp_circuit_graph)
    graph_nodes_reverse = circuit_graph.nodes()
    graph_nodes_reverse.reverse()
    # print(graph_nodes_reverse)
    for node in graph_nodes_reverse:
        if node.qubit_wire in ancillas and node.node_type is UNCOMP:
            remove_uncomputation_step(circuit_graph, node.index)

    
    return circuit_graph


def exhaustive_uncomputation_removing(circuit_graph: rustworkx.PyDiGraph, num_qubit, num_ancilla):
    
    ancillas = list(range(num_qubit, num_qubit+num_ancilla))
    ancillas_power_set = chain.from_iterable(combinations(ancillas, r) for r in range(len(ancillas)+1))
    smallest_removable = ancillas
    
    uncomp_circuit_graph, has_cycle = add_uncomputation(circuit_graph, ancillas, allow_cycle=True)

    # if not has_cycle:
    #     return ancillas

    for ancilla_set in ancillas_power_set:
        reduced_uncomp_circuit_graph = remove_uncomputation_full(uncomp_circuit_graph, ancilla_set)
        cycle = rustworkx.digraph_find_cycle(reduced_uncomp_circuit_graph)

        if len(cycle) == 0 and len(ancilla_set) < len(smallest_removable):
            smallest_removable = ancilla_set


    return smallest_removable
    
    
def greedy_uncomputation_full(circuit_graph: rustworkx.PyDiGraph, num_qubit, num_ancilla):
    
    ancillas = list(range(num_qubit, num_qubit+num_ancilla))
    uncomp_circuit_graph, has_cycle = add_uncomputation(circuit_graph, ancillas, allow_cycle=True)

    cycle_check = rustworkx.digraph_find_cycle(uncomp_circuit_graph)
    while len(cycle_check) > 0:
        uncomp_cycle_counter = collections.Counter({i:0 for i in range(num_qubit+num_ancilla)})
        comp_cycle_counter = collections.Counter({i:0 for i in range(num_qubit+num_ancilla)})

        simple_cycles = rustworkx.simple_cycles(uncomp_circuit_graph)
        for cycle in simple_cycles:
            # print(cycle)
            for idx in cycle:
                node = uncomp_circuit_graph.get_node_data(idx)
                if node.qubit_type is ANCILLA: 
                    if node.node_type is UNCOMP:
                        uncomp_cycle_counter[node.qubit_wire] +=1
                    else:
                        comp_cycle_counter[node.qubit_wire] +=1

        if comp_cycle_counter.total() > 0:
            print(f'Warning, removing uncomputation introduced cycles with computation ancilla nodes')
            logger.warning(f'Warning, removing uncomputation introduced cycles with computation ancilla nodes')
            print(comp_cycle_counter)
            logger.warning(comp_cycle_counter)

        qubit, num_cycles = uncomp_cycle_counter.most_common(1)[0]
        print(qubit, num_cycles)

        uncomp_circuit_graph = remove_uncomputation_full(uncomp_circuit_graph, [qubit])

        cycle_check = rustworkx.digraph_find_cycle(uncomp_circuit_graph)

    return uncomp_circuit_graph



def remove_uncomputation_partial(uncomp_circuit_graph:rustworkx.PyDiGraph, ancilla: int, nodes_in_cycle:List[int]):
    circuit_graph = copy.deepcopy(uncomp_circuit_graph)
    graph_nodes_reverse = circuit_graph.nodes()
    graph_nodes_reverse.reverse()
    # print(graph_nodes_reverse)
    # Initialize node for this will have same index as ancilla

    # first_node = circuit_graph.get_node_data(ancilla)
    adj_nodes = circuit_graph.adj_direction(ancilla, False)
    target_path = [ancilla]
    # cycles_per_nodes = collections.Counter(nodes_in_cycle)
    uncomp_nodes_part_of_cycle = set(nodes_in_cycle)

    while len(adj_nodes) > 0:
        try:
            target_node = list(filter(lambda x: adj_nodes.get(x) is TARGET, adj_nodes.keys()))[0]
        except IndexError:
            break

        # print(target_node)
        target_path.append(target_node)
        # node = circuit_graph.get_node_data(target_node)
        adj_nodes = circuit_graph.adj_direction(target_node, False)

    target_path.sort(reverse=True)

    # print(f'nodes_in_cycle: {nodes_in_cycle}')
    # print(f'target_path: {target_path}')
    # print(f'cycles_per_nodes: {cycles_per_nodes}')
    # print(f'uncomp_nodes_part_of_cycle: {uncomp_nodes_part_of_cycle}')
    # print(f'qubit_node_cycles: {qubit_node_cycles}')
    
    # exit(0) 

    for idx in target_path:
        if idx in uncomp_nodes_part_of_cycle:
            # controls_ancilla = False
            idx_adj_nodes = circuit_graph.adj_direction(idx, False)
            controls = list(filter(lambda x: idx_adj_nodes.get(x) is CONTROL and circuit_graph.get_node_data(x).node_type is UNCOMP, 
                                   idx_adj_nodes.keys()))
            # idx_cycles = qubit_node_cycles[idx]
            # print(f'{idx} : {idx_cycles}')


            if len(controls) == 0:
                remove_uncomputation_step(circuit_graph, idx)
            else:
                break
        
    return circuit_graph


def greedy_uncomputation_partial(circuit_graph: rustworkx.PyDiGraph, num_qubit, num_ancilla):

    ancillas = list(range(num_qubit, num_qubit+num_ancilla))
    uncomp_circuit_graph, has_cycle = add_uncomputation(circuit_graph, ancillas, allow_cycle=True)

    cycle_check = rustworkx.digraph_find_cycle(uncomp_circuit_graph)

    while len(cycle_check) > 0:
        uncomp_cycle_counter = collections.Counter({i:0 for i in range(num_qubit+num_ancilla)})
        comp_cycle_counter = collections.Counter({i:0 for i in range(num_qubit+num_ancilla)})

        comp_cycle_nodes = collections.UserDict({i:collections.UserList([]) for i in range(num_qubit+num_ancilla)})
        uncomp_cycle_nodes = collections.UserDict({i:collections.UserList([]) for i in range(num_qubit+num_ancilla)})

        node_cycle_dict = collections.UserDict({i:collections.UserList([]) for i in uncomp_circuit_graph.node_indices()})


        simple_cycles = rustworkx.simple_cycles(uncomp_circuit_graph)
        for cycle in simple_cycles:
            # print(cycle)
            for idx in cycle:
                node = uncomp_circuit_graph.get_node_data(idx)
                node_cycle_dict[idx].append([i for i in cycle])
                if node.qubit_type is ANCILLA: 
                    if node.node_type is UNCOMP:
                        uncomp_cycle_counter[node.qubit_wire] +=1
                        uncomp_cycle_nodes[node.qubit_wire].append(idx)
                    else:
                        comp_cycle_counter[node.qubit_wire] +=1
                        comp_cycle_nodes[node.qubit_wire].append(idx)

        if comp_cycle_counter.total() > 0:
            print(f'Warning, removing uncomputation introduced cycles with computation ancilla nodes')
            logger.warning(f'Warning, removing uncomputation introduced cycles with computation ancilla nodes')
            print(comp_cycle_counter)
            logger.warning(comp_cycle_counter)

        qubit, num_cycles = uncomp_cycle_counter.most_common(1)[0]
        # qubit_nodes_cycles = {i:node_cycle_dict.get(i) for i in set(uncomp_cycle_nodes[qubit])}
        print(qubit, num_cycles)



        uncomp_circuit_graph = remove_uncomputation_partial(uncomp_circuit_graph, qubit, uncomp_cycle_nodes[qubit])

        cycle_check = rustworkx.digraph_find_cycle(uncomp_circuit_graph)

    return uncomp_circuit_graph




