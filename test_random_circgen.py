from helperfunctions.randomcircuit import random_quantum_circuit_basic


circuit = random_quantum_circuit_basic(3,3,5)

circuit.draw('mpl', filename='random_circgen_test')