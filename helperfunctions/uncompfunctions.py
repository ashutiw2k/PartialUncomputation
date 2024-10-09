import collections
import copy
from itertools import chain, combinations
from typing import List
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


def get_uncomp_node_index(circuit_graph: rustworkx.PyDiGraph, node_index):
    for node in circuit_graph.nodes():
        if node.node_type is UNCOMP and node.get_nodenum() == circuit_graph.nodes()[node_index].get_nodenum:
            return node.get_index()
    return node_index

def add_uncomputation_step(circuit_graph: rustworkx.PyDiGraph, idx):

    node = circuit_graph.nodes()[idx]
    node_adj = circuit_graph.adj(idx)

    assert node.opname not in NON_QFREE

    try:
        node_controls_idx = list(map(lambda x: x[0], list(filter(lambda x: x[1] == CONTROL and x[0] < node.get_index(), list(node_adj.items())))))
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
    circuit_graph.nodes()[uncomp_node_index].set_index(uncomp_node_index)
    circuit_graph.nodes()[uncomp_node_index].set_nodenum(
        circuit_graph.nodes()[node.get_index()].get_nodenum() - 1
    )

    # Adding Control Edges
    for control_idx in node_controls_idx_uncomp:
        circuit_graph.add_edge(control_idx, uncomp_node_index, CONTROL)

    prev_node_adj = circuit_graph.adj(prev_node_index)
    print(prev_node_adj)
    try:
        prev_node_controlled_idx = list(map(lambda x: x[0], list(filter(lambda x: x[1] == CONTROL and x[0] > prev_node_index, list(prev_node_adj.items())))))
    except IndexError:
        prev_node_controlled_idx = []

    for idx in prev_node_controlled_idx:
        circuit_graph.add_edge(idx, uncomp_node_index, ANTIDEP)

    # print(circuit_graph.adj(opnode_index))

    print(uncomp_node)

    print('----------------------------------------')


    return circuit_graph

def add_uncomputation(circuit_graph: rustworkx.PyDiGraph, ancillas:List[int]):

    uncomp_circuit_graph = copy.deepcopy(circuit_graph)
    graph_nodes_reverse = list(rustworkx.topological_sort(copy.deepcopy(circuit_graph)))
    graph_nodes_reverse.reverse()
    print(graph_nodes_reverse)
    for idx in graph_nodes_reverse:
        if circuit_graph.nodes()[idx].qubit_wire in ancillas and circuit_graph.nodes()[idx].node_type is COMP: #and circuit_graph.nodes()[idx].qubit_type is ANCILLA and circuit_graph.nodes()[idx].node_type is COMP:
            add_uncomputation_step(uncomp_circuit_graph, idx)

    return uncomp_circuit_graph


def exhaustive_uncomputation(circuit_graph: rustworkx.PyDiGraph, num_qubit, num_ancilla):
    
    graph_nodes_reverse = list(rustworkx.topological_sort(copy.deepcopy(circuit_graph)))
    graph_nodes_reverse.reverse()
    ancillas = list(range(num_qubit, num_qubit+num_ancilla))
    ancillas_power_set = chain.from_iterable(combinations(ancillas, r) for r in range(len(ancillas)+1))
    largest_uncomputable = ()
    for ancilla_set in ancillas_power_set:
        uncomp_circuit_graph = copy.deepcopy(circuit_graph)
        for idx in graph_nodes_reverse:
            if circuit_graph.nodes()[idx].qubit_type is ANCILLA \
            and circuit_graph.nodes()[idx].node_type is COMP \
            and circuit_graph.nodes()[idx].qubit_wire in ancilla_set:
                add_uncomputation_step(uncomp_circuit_graph, idx)
        
        if not rustworkx.digraph_find_cycle(uncomp_circuit_graph) \
        and len(ancilla_set) > len(largest_uncomputable):
            largest_uncomputable = ancilla_set
    
    






