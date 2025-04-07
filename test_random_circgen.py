from helperfunctions.randomcircuit import random_quantum_circuit_large_with_params
import matplotlib.pyplot as plt
import gc

for i in range(50):
    print(f'Circuit {i+1}:')
    circuit,q,a,g = random_quantum_circuit_large_with_params(3,5,15,add_random_h=True)
    circuit.draw('latex', filename=f'qcnc_paper_figures/Circuit_RandomCircuitExample_{i}.png')
    plt.close()
    gc.collect()
