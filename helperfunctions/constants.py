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
