

import copy
import qiskit
import rustworkx

from .constants import StringConstants
from .graphhelper import CGNode, breakdown_qubit

INPUT = StringConstants.INPUT.value
ANCILLA = StringConstants.ANCILLA.value

INIT = StringConstants.INIT.value
COMP = StringConstants.COMP.value
UNCOMP = StringConstants.UNCOMP.value

TARGET = StringConstants.TARGET.value
CONTROL = StringConstants.CONTROL.value
ANTIDEP = StringConstants.ANTIDEP.value


def get_computation_graph(circuit: qiskit.circuit.QuantumCircuit, ancilla_start: int):
    circuit_graph = rustworkx.PyDiGraph(multigraph=False)
    last_node_index = {}
    # Add the initial qubits

    ANCILLA_START = ancilla_start

    circuit_qubits = circuit.qubits
    circuit_data = circuit.data

    for qubit in circuit_qubits:
        qubit_dict = breakdown_qubit(qubit)
        qubit_type = INPUT if qubit_dict['wire'] < ANCILLA_START else ANCILLA
        init_node = CGNode(qubit_dict, qubit_type=qubit_type, node_type=INIT)
        index = circuit_graph.add_node(init_node)
        circuit_graph.nodes()[index].set_index(index)
        circuit_graph.nodes()[index].set_nodenum(0)
        last_node_index[init_node.label] = index

    # print(circuit_graph.nodes())
    for node in circuit_graph.nodes():
        print(node)
    print(last_node_index)

    # Adding Computation Gates
    for circ_inst in circuit_data:
        opname = circ_inst.operation.name
        qubit_dict_all = []
        for qubit in circ_inst.qubits:
            qubit_dict_all.append(breakdown_qubit(qubit))
        print(qubit_dict_all)
        # target_qubit_dict = qubit_dict_all[-1]
        # target_label = target_qubit_dict['name'] + str(target_qubit_dict['wire'])
        # target_index = last_node_index[target_label]
        qubit_indicies = [last_node_index[qubit_dict['label']] for qubit_dict in qubit_dict_all]
        print(qubit_indicies)
        prev_node_index = qubit_indicies.pop()
        print(prev_node_index)
        # Adding the node
        qubit_type = INPUT if qubit_dict_all[-1]['wire'] < ANCILLA_START else ANCILLA
        opnode = CGNode(qubit_dict_all[-1], qubit_type=qubit_type, node_type=COMP, opname=opname)
        opnode_index = circuit_graph.add_child(prev_node_index, opnode, TARGET)
        circuit_graph.nodes()[opnode_index].set_index(opnode_index)
        circuit_graph.nodes()[opnode_index].set_nodenum(
            circuit_graph.nodes()[prev_node_index].get_nodenum() + 1
        )
        last_node_index[opnode.label] = opnode_index

        # Adding the control edges and Antidep between controls
        for qubit_index in qubit_indicies:
            circuit_graph.add_edge(qubit_index, opnode_index, CONTROL)        
            
            controls_adj = circuit_graph.adj(qubit_index)
            try:
                controls_target_idx = list(map(lambda x: x[0], list(filter(lambda x: x[1] == TARGET and x[0] > qubit_index and not circuit_graph.has_edge(x[0], opnode_index), list(controls_adj.items())))))
            except IndexError:
                controls_target_idx = []

            for idx in controls_target_idx:
                circuit_graph.add_edge(opnode_index, idx, ANTIDEP)

        # Adding AntiDep Edges (Opnode to OTHER controlled nodes)
        prev_node_adj = circuit_graph.adj(prev_node_index)
        print(prev_node_adj)
        try:
            prev_node_controlled_idx = list(map(lambda x: x[0], list(filter(lambda x: x[1] == CONTROL and not circuit_graph.has_edge(x[0], opnode_index), list(prev_node_adj.items())))))
        except IndexError:
            prev_node_controlled_idx = []

        for idx in prev_node_controlled_idx:
            circuit_graph.add_edge(idx, opnode_index, ANTIDEP)
            

        # print(circuit_graph.adj(opnode_index))

        print('----------------------------------------')


    return circuit_graph


def get_uncomp_circuit(circuit_graph: rustworkx.PyDiGraph):
    
    sorted_circuit_graph = rustworkx.topological_sort(copy.deepcopy(circuit_graph))
    print(sorted_circuit_graph)

    uncomp_circuit = qiskit.QuantumCircuit(len(list(filter(lambda x: x.node_type == INIT, circuit_graph.nodes()))))

    for idx in sorted_circuit_graph:
        # print(circuit_graph.nodes()[idx])
        node = circuit_graph.get_node_data(idx) 
        print(node)
        node_adj = circuit_graph.adj(idx)
        try:
            node_prev_idx = list(filter(lambda x: x[1] == TARGET and x[0] < node.get_index(), list(node_adj.items()))).pop()[0]
        except IndexError:
            node_prev_idx = None

        try:
            node_controls_idx = list(map(lambda x: x[0], list(filter(lambda x: x[1] == CONTROL and x[0] < node.get_index(), list(node_adj.items())))))
        except IndexError:
            node_controls_idx = []

        # node_controls = circuit_graph.find_successors_by_edge(idx, lambda x:x==CONTROL)
        print(node_prev_idx)
        print(node_controls_idx)
        print('------------------------------------------------')
        if node_prev_idx is None:
            continue
        prev_node = circuit_graph.nodes()[node_prev_idx]
        control_nodes = [circuit_graph.nodes()[idx] for idx in node_controls_idx]
        opname = node.opname
        if opname == 'ccx':
            assert len(control_nodes) == 2
            uncomp_circuit.ccx(control_nodes[0].qubit_wire, control_nodes[1].qubit_wire, prev_node.qubit_wire)
        elif opname == 'cx':
            assert len(control_nodes) == 1
            uncomp_circuit.cx(control_nodes[0].qubit_wire, prev_node.qubit_wire)
        elif opname == 'cz':
            assert len(control_nodes) == 1
            uncomp_circuit.cz(control_nodes[0].qubit_wire, prev_node.qubit_wire)
        elif opname == 'x':
            assert len(control_nodes) == 0
            uncomp_circuit.x(prev_node.qubit_wire)
        elif opname == 'z':
            assert len(control_nodes) == 0
            uncomp_circuit.z(prev_node.qubit_wire)
        elif opname == 'h':
            assert len(control_nodes) == 0
            uncomp_circuit.h(prev_node.qubit_wire)


    return uncomp_circuit
