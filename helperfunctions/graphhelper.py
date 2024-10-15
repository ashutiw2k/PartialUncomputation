import qiskit
from .constants import StringConstants

INIT = StringConstants.INIT.value
COMP = StringConstants.COMP.value
UNCOMP = StringConstants.UNCOMP.value

TARGET = StringConstants.TARGET.value
CONTROL = StringConstants.CONTROL.value
ANTIDEP = StringConstants.ANTIDEP.value

class CGNode:
    def __init__(self, qubit_dict, qubit_type=None, node_type=None, opname=None):
        self.qubit = qubit_dict['qubit']
        self.qubit_wire = qubit_dict['wire']
        self.qubit_name = qubit_dict['name']
        self.label = qubit_dict['label']
        self.qubit_dict = qubit_dict

        self.index = -1
        self.qubit_type = qubit_type
        self.node_type = node_type
        self.opname = opname
        self.node_num = -1

    def set_index(self, index):
        self.index = index
    def get_index(self):
        return self.index

    def set_nodenum(self, nodenum):
        self.node_num = nodenum
    def get_nodenum(self):
        return self.node_num

    def graph_label(self):
        return f'{self.index}:{self.opname}:{self.label}_{self.node_num}{"*" if self.node_type is UNCOMP else ""}' if self.opname else self.label

    def __str__(self):
        return f"CGNode: Labeled {self.label} @ index: {self.index} of type {self.qubit_type} is a {self.node_type} node."
    def __doc__(self):
        return f"CGNode: {self.qubit} @ index: {self.index}"

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, CGNode):
            return self.qubit == __o.qubit and self.qubit_wire == __o.qubit_wire and self.qubit_name == __o.qubit_name and self.index == __o.index
        pass

def breakdown_qubit(qubit: qiskit.circuit.Qubit):
    return {'name':qubit._register.name, 'wire':qubit._index, 'qubit':qubit, 'label':qubit._register.name+str(qubit._index)}


def get_pos_of_nodes(graph):
    pos = {}
    for node in graph.nodes():
        pos[node.get_index()] = (node.qubit_wire, node.qubit_name)
    return pos

def node_attr(node: CGNode):
    attribute_dict = {"label": node.graph_label()}
    if node.node_type is INIT:
        attribute_dict.update({'color': 'green', 'fillcolor': 'green', 'style': 'filled'})
    elif node.node_type is COMP:
        attribute_dict.update({'color': 'blue', 'fillcolor': 'blue', 'style': 'filled'})
    elif node.node_type is UNCOMP:
        attribute_dict.update({'color': 'red', 'fillcolor': 'red', 'style': 'filled'})
    else:
        attribute_dict.update({'color': 'yellow', 'fillcolor': 'yellow', 'style': 'filled'})

    return attribute_dict

def edge_attr(edge):
    attribute_dict = {"label": edge[0]}
    if edge == TARGET:
        attribute_dict.update({'color': 'blue', 'style': 'solid'})
    elif edge == CONTROL:
        attribute_dict.update({'color': 'red', 'style': 'dotted', 'arrowtail':'o'})
    elif edge == ANTIDEP:
        attribute_dict.update({'color': 'green', 'style': 'dashed'})
    else:
        attribute_dict.update({'color': 'yellow', 'style': 'dashed'})

    return attribute_dict

def edge_matcher(a, b):
    return a == b

def node_matcher(a:CGNode, b:CGNode):
    return a.label == b.label and a.get_nodenum() == b.get_nodenum() \
    and a.opname == b.opname and a.node_type == b.node_type 