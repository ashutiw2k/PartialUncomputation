from typing import Literal
import numpy
from qiskit import QuantumCircuit
from matplotlib import pyplot as plt
from scipy.spatial.distance import euclidean, cityblock, jensenshannon
from scipy.stats import wasserstein_distance
from helperfunctions.measurecircuit import get_probability_from_statevector, get_statevector, print_probs, zero_ancillas_in_statevector

class NumAncillaUncomped:
    def __init__(self) -> None:
        self.exhaustive = []
        self.num_exhaustive = []
        self.greedy_full = []
        self.num_greedy_full = []
        self.greedy_partial = []
        self.num_greedy_partial = []
        self.regular = []
        self.num_regular = []
    
    def add_exhaustive(self, ancillas):
        self.exhaustive.append(ancillas)
        self.num_exhaustive.append(len(ancillas))

    def add_greedy_full(self, ancillas):
        self.greedy_full.append(ancillas)
        self.num_greedy_full.append(len(ancillas))

    def add_greedy_partial(self, ancillas):
        self.greedy_partial.append(ancillas)
        self.num_greedy_partial.append(len(ancillas))

    def add_regular(self, ancillas):
        self.regular.append(ancillas)
        self.num_regular.append(len(ancillas))

    def get_all_nums(self):
        return self.num_exhaustive, self.num_greedy_full, self.num_greedy_partial
        
class ProbDiffResults:
    def __init__(self, valid_num_circuits):
        self.exhaustive_comp_diff = numpy.zeros(valid_num_circuits)
        self.exhaustive_uncomp_diff = numpy.zeros(valid_num_circuits)
        self.exhaustive_eq4 = numpy.zeros(valid_num_circuits)
        self.exhaustive_eq5 = numpy.zeros(valid_num_circuits)
        self.exhaustive_uncomp = numpy.zeros(valid_num_circuits)
        

        self.greedy_full_comp_diff = numpy.zeros(valid_num_circuits)
        self.greedy_full_uncomp_diff = numpy.zeros(valid_num_circuits)
        self.greedy_full_eq4 = numpy.zeros(valid_num_circuits)
        self.greedy_full_eq5 = numpy.zeros(valid_num_circuits)
        self.greedy_full_uncomp = numpy.zeros(valid_num_circuits)
        
        self.greedy_partial_comp_diff = numpy.zeros(valid_num_circuits)
        self.greedy_partial_uncomp_diff = numpy.zeros(valid_num_circuits)        
        self.greedy_partial_eq4 = numpy.zeros(valid_num_circuits)
        self.greedy_partial_eq5 = numpy.zeros(valid_num_circuits)
        self.greedy_partial_uncomp = numpy.zeros(valid_num_circuits)

        self.regular_comp_diff = numpy.zeros(valid_num_circuits)
        self.regular_uncomp_diff = numpy.zeros(valid_num_circuits)
        self.regular_eq4 = numpy.zeros(valid_num_circuits)
        self.regular_eq5 = numpy.zeros(valid_num_circuits)
        self.regular_uncomp = numpy.zeros(valid_num_circuits)

    def add_to_exhaustive(self, comp_diff, uncomp_diff, eq4, eq5, uncomp, idx):
        # numpy.append(self.exhaustive_uncomp_diff, comp)
        # numpy.append(self.exhaustive_uncomp_diff, uncomp)
        self.exhaustive_comp_diff[idx] = comp_diff
        self.exhaustive_uncomp_diff[idx] = uncomp_diff
        # self.exhaustive_eq4[idx] = eq4
        # self.exhaustive_eq5[idx] = eq5
        # self.exhaustive_uncomp[idx] = uncomp


    def add_to_greedy_partial(self, comp_diff, uncomp_diff, eq4, eq5, uncomp, idx):
        # numpy.append(self.exhaustive_uncomp_diff, comp)
        # numpy.append(self.exhaustive_uncomp_diff, uncomp)
        self.greedy_partial_comp_diff[idx] = comp_diff
        self.greedy_partial_uncomp_diff[idx] = uncomp_diff
        # self.greedy_partial_eq4[idx] = eq4
        # self.greedy_partial_eq5[idx] = eq5
        # self.greedy_partial_uncomp[idx] = uncomp
    
    def add_to_greedy_full(self, comp_diff, uncomp_diff, eq4, eq5, uncomp, idx):
        # numpy.append(self.exhaustive_uncomp_diff, comp)
        # numpy.append(self.exhaustive_uncomp_diff, uncomp)
        self.greedy_full_comp_diff[idx] = comp_diff
        self.greedy_full_uncomp_diff[idx] = uncomp_diff
        # self.greedy_full_eq4[idx] = eq4
        # self.greedy_full_eq5[idx] = eq5
        # self.greedy_full_uncomp[idx] = uncomp
    
    def add_to_regular(self, comp_diff, uncomp_diff, eq4, eq5, uncomp, idx):
        # numpy.append(self.exhaustive_uncomp_diff, comp)
        # numpy.append(self.exhaustive_uncomp_diff, uncomp)
        self.regular_comp_diff[idx] = comp_diff
        self.regular_uncomp_diff[idx] = uncomp_diff
        # self.regular_eq4[idx] = eq4
        # self.regular_eq5[idx] = eq5
        # self.regular_uncomp[idx] = uncomp

    def __str__(self):
        return f'''
                Exhaustive Comp Avg:\t\t{numpy.average(self.exhaustive_comp_diff)}
                Exhaustive UnComp Avg:\t\t{numpy.average(self.exhaustive_uncomp_diff)}
                Greedy Full Comp Avg:\t\t{numpy.average(self.greedy_full_comp_diff)}
                Greedy Full UnComp Avg:\t\t{numpy.average(self.greedy_full_uncomp_diff)}
                Greedy Partial Comp Avg:\t{numpy.average(self.greedy_partial_comp_diff)}
                Greedy Partial UnComp Avg:\t{numpy.average(self.greedy_partial_uncomp_diff)}
                Regular Comp Avg:\t\t{numpy.average(self.regular_comp_diff)}
                Regular UnComp Avg:\t\t{numpy.average(self.regular_uncomp_diff)}
                '''

        
def get_difference_in_prob(comp_circuit: QuantumCircuit, uncomp_circuit:QuantumCircuit, num_a,
                     distance:Literal['euclidean', 'manhattan', 'wasserstein', 'jensenshannon']='manhattan'):
    eq4_comp_statevector = get_statevector(comp_circuit)
    eq4_comp_prob_dist = get_probability_from_statevector(eq4_comp_statevector)
    # logger.info(f'Comp Circuit {name_str} Eq4 Probability Distribution: \n{print_probs(eq4_comp_prob_dist)}')

    eq5_comp_statevector = zero_ancillas_in_statevector(eq4_comp_statevector, num_a)
    eq5_comp_prob_dist = get_probability_from_statevector(eq5_comp_statevector)
    # logger.info(f'Comp Circuit {name_str} Eq5 Probability Distribution: \n{print_probs(eq5_comp_prob_dist)}')

    eq4_uncomp_statevector = get_statevector(uncomp_circuit)
    eq4_uncomp_prob_dist = get_probability_from_statevector(eq4_uncomp_statevector)
    # logger.info(f'{uncomp_type.capitalize()} Uncomp Circuit {name_str} Eq4 Probability Distribution: \n{print_probs(eq4_uncomp_prob_dist)}')
    
    # print(numpy.sum(eq4_comp_prob_dist))
    # print_probs(eq4_comp_prob_dist)
    # print(numpy.sum(eq4_uncomp_prob_dist))
    # print_probs(eq4_uncomp_prob_dist)
    # print(numpy.sum(eq5_comp_prob_dist))
    # print_probs(eq5_comp_prob_dist)
    # assert numpy.sum(eq4_comp_prob_dist) == 1
    # assert numpy.sum(eq5_comp_prob_dist) == 1
    # assert numpy.sum(eq4_uncomp_prob_dist) == 1
    
    distance_probs_eq5_4_comp = 0
    distance_probs_eq5_4_uncomp = 0

    if distance == 'euclidean':
        distance_probs_eq5_4_comp = euclidean(eq5_comp_prob_dist, eq4_comp_prob_dist)
        distance_probs_eq5_4_uncomp = euclidean(eq5_comp_prob_dist, eq4_uncomp_prob_dist)
    elif distance == 'manhattan':
        distance_probs_eq5_4_comp = cityblock(eq5_comp_prob_dist, eq4_comp_prob_dist)
        distance_probs_eq5_4_uncomp = cityblock(eq5_comp_prob_dist, eq4_uncomp_prob_dist)
    # This is the Earth Movers Distance. 
    elif distance == 'wasserstein':
        distance_probs_eq5_4_comp = wasserstein_distance(eq5_comp_prob_dist, eq4_comp_prob_dist)
        distance_probs_eq5_4_uncomp = wasserstein_distance(eq5_comp_prob_dist, eq4_uncomp_prob_dist)
    elif distance == 'jensenshannon':
        distance_probs_eq5_4_comp = jensenshannon(eq5_comp_prob_dist, eq4_comp_prob_dist)
        distance_probs_eq5_4_uncomp = jensenshannon(eq5_comp_prob_dist, eq4_uncomp_prob_dist)

    
    
    distance_probs_eq5_4_comp, distance_probs_eq5_4_uncomp = numpy.round((distance_probs_eq5_4_comp, distance_probs_eq5_4_uncomp), decimals=10)

    return distance_probs_eq5_4_comp, distance_probs_eq5_4_uncomp, eq4_comp_prob_dist, eq5_comp_prob_dist, eq4_uncomp_prob_dist

def plot_ancilla_results(results_dict, figname='NEEDFIGNAME', image_write_path='NEED_IMAGE_PATH',
                 title='Number of Ancillas Uncomputed', 
                 xlabel = 'Total Number of Ancillas', 
                 ylabel = 'Average Number of Ancillas Uncomputed'):
    x_axis = []
    # ex_comp_avg = []
    ex_uncomp_avg = []
    # gf_comp_avg = []
    gf_uncomp_avg = []
    # gp_comp_avg = []
    gp_uncomp_avg = []
    
    for i,x in results_dict.items():
        # print(i)
        # print(x)
        # print('-------------------------------')
        x_axis.append(i)
        # ex_comp_avg.append(numpy.average(x.exhaustive_comp_diff))
        ex_uncomp_avg.append(numpy.trunc(numpy.average(x.num_exhaustive)))
        # gf_comp_avg.append(numpy.average(x.greedy_full_comp_diff))
        gf_uncomp_avg.append(numpy.trunc(numpy.average(x.num_greedy_full)))
        # gp_comp_avg.append(numpy.average(x.greedy_partial_comp_diff))
        gp_uncomp_avg.append(numpy.trunc(numpy.average(x.num_greedy_partial)))

    # plt.plot(x_axis, ex_comp_avg, marker='o', linestyle='-', label='Original')
    plt.plot(x_axis, ex_uncomp_avg, marker='o', linestyle='-', label='Exhaustive')
    plt.plot(x_axis, gf_uncomp_avg, marker='o', linestyle='-', label='Greedy-Full')
    plt.plot(x_axis, gp_uncomp_avg, marker='o', linestyle='-', label='Greedy-Partial')

    plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    # fig = plt.show()
    # plt.figure(figsize=)
    plt.xlim(x_axis[0]-1, x_axis[-1]+1)
    plt.autoscale(False, axis='x')
    # plt.xscale('linear')
    plt.savefig(f'{image_write_path}{figname}')

def plot_results(results_dict, figname='NEEDFIGNAME', image_write_path='NEED_IMAGE_PATH',
                 title='Difference In Probability - All Methods', 
                 xlabel = 'Number of (C-Not) Gates', 
                 ylabel = 'Difference in Probability Distribution'):
    x_axis = []
    ex_comp_avg = []
    ex_uncomp_avg = []
    gf_comp_avg = []
    gf_uncomp_avg = []
    gp_comp_avg = []
    gp_uncomp_avg = []
    
    for i,x in results_dict.items():
        # print(i)
        # print(x)
        # print('-------------------------------')
        x_axis.append(i)
        ex_comp_avg.append(numpy.average(x.exhaustive_comp_diff))
        ex_uncomp_avg.append(numpy.average(x.exhaustive_uncomp_diff))
        gf_comp_avg.append(numpy.average(x.greedy_full_comp_diff))
        gf_uncomp_avg.append(numpy.average(x.greedy_full_uncomp_diff))
        gp_comp_avg.append(numpy.average(x.greedy_partial_comp_diff))
        gp_uncomp_avg.append(numpy.average(x.greedy_partial_uncomp_diff))

    plt.plot(x_axis, ex_comp_avg, marker='o', linestyle='-', label='No Uncomputation')
    plt.plot(x_axis, ex_uncomp_avg, marker='o', linestyle='-', label='Exhaustive')
    plt.plot(x_axis, gf_uncomp_avg, marker='o', linestyle='-', label='Greedy-Full')
    plt.plot(x_axis, gp_uncomp_avg, marker='o', linestyle='-', label='Greedy-Partial')

    plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    # fig = plt.show()
    # plt.figure(figsize=)
    plt.xlim(x_axis[0]-1, x_axis[-1]+1)
    plt.autoscale(False, axis='x')
    # plt.xscale('linear')
    plt.savefig(f'{image_write_path}/{figname}')
    