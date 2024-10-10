from helperfunctions.randomcircuit import random_quantum_circuit


circuit = random_quantum_circuit(5,5,15)

circuit.draw('mpl', filename='random_circgen_test')