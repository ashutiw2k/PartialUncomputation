from helperfunctions.randomcircuit import random_quantum_circuit


circuit = random_quantum_circuit(3,3,5)

circuit.draw('mpl', filename='random_circgen_test')