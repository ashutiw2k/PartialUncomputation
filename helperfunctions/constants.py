from enum import Enum


class StringConstants(Enum):
    # Types of nodes
    INIT = 'initialize'
    COMP = 'computation'
    UNCOMP = 'uncomputation'

    # Type of Qubit
    INPUT = 'input'
    ANCILLA = 'ancilla'

    # Type of edge
    TARGET = 'target'
    CONTROL = 'control'
    ANTIDEP = 'anti-dependence'


class ListConstants(Enum):

    NON_QFREE = ['h']

EVAL_DIRS = ['comp_circuit', 
             'comp_circuit_graph', 
             'exhaustive_uncomp_circuit',
             'exhaustive_uncomp_graph',
             'greedy_uncomp_circuit',
             'greedy_uncomp_graph',
             'greedy_partial_uncomp_circuit',
             'greedy_partial_uncomp_graph',
             'regular_uncomp_circuit',
             'regular_uncomp_graph'
             ]