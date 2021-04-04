from pyquil import get_qc, Program
from pyquil.gates import CZ, H, Z, T, CNOT, X, MEASURE
from pyquil.latex import display
from pyquil.api import WavefunctionSimulator
import matplotlib.pyplot as plt
import numpy as np
import random

#get random nr 0 - 7
nr = random.randint(0, 7)

#classical oracle
def classical_oracle(passed_nr):
    if passed_nr == nr:
        return True
    else:
        return False

#classical attempt
guessed = False
nr_of_tries = 0

while (not guessed):
    guessed_nr = int(input("Guess the nr between 0 and 7:"))
    nr_of_tries+=1
    guessed = classical_oracle(guessed_nr)

print(f"You guessed correctly after {nr_of_tries} tries")

def CCZ():
    t_gate_1 = Program(T(1)).dagger()
    t_gate_2 = Program(T(2)).dagger()
    ccz = Program()
    ccz += CNOT(1,2)
    ccz += t_gate_2
    ccz += CNOT(0,2)
    ccz += T(2)
    ccz += CNOT(1,2)
    ccz += t_gate_2
    ccz += CNOT(0,2)
    ccz += T(1)
    ccz += T(2)
    ccz += CNOT(0,1)
    ccz += T(0)
    ccz += t_gate_1
    ccz += CNOT(0,1)
    return ccz

def amplification():
    amplification = Program()
    amplification += H(0)
    amplification += H(1)
    amplification += H(2)
    amplification += X(0)
    amplification += X(1)
    amplification += X(2)
    amplification += CCZ()
    amplification += X(0)
    amplification += X(1)
    amplification += X(2)
    amplification += H(0)
    amplification += H(1)
    amplification += H(2)
    return amplification

#quantum oracle
def quantum_oracle():
    quantum_oracle = Program()

    #create uniform superposition
    quantum_oracle += H(0)
    quantum_oracle += H(1)
    quantum_oracle += H(2)

    #mark the correct state
    if (nr == 0): # 000
        #flip all qubits
        quantum_oracle += X(0)
        quantum_oracle += X(1)
        quantum_oracle += X(2)
        #do 111
        quantum_oracle += CCZ()
        #flip all qubits back
        quantum_oracle += X(0)
        quantum_oracle += X(1)
        quantum_oracle += X(2)
    elif (nr == 1): #001
        #flip second and third qubit
        quantum_oracle += X(1)
        quantum_oracle += X(2)
        #CCZ gate
        quantum_oracle += CCZ()
        #reflip second and third qubit
        quantum_oracle += X(1)
        quantum_oracle += X(2)
    elif (nr == 2): #010
        #flip first and third qubit
        quantum_oracle += X(0)
        quantum_oracle += X(2)
        #CCZ gate
        quantum_oracle += CCZ()
        #reflip first and third qubit
        quantum_oracle += X(0)
        quantum_oracle += X(2)
    elif (nr == 3): #011
        #flip third qubit
        quantum_oracle += X(2)
        #CCZ gate
        quantum_oracle += CCZ()
        #reflip third qubit
        quantum_oracle += X(2)
    elif (nr == 4): #100
        #flip first and second qubit
        quantum_oracle += X(0)
        quantum_oracle += X(1)
        #CCZ gate
        quantum_oracle += CCZ()
        #reflip first and second qubit
        quantum_oracle += X(0)
        quantum_oracle += X(1)
    elif (nr == 5): #101
        #flip second qubit
        quantum_oracle += X(1)
        #CCZ gate
        quantum_oracle += CCZ()
        #reflip second qubit
        quantum_oracle += X(1)
    elif (nr == 6): #110
        #flip first qubit
        quantum_oracle += X(0)
        #CCZ gate
        quantum_oracle += CCZ()
        #reflip first qubit
        quantum_oracle += X(0)
    else: #111
        #CCZ gate
        quantum_oracle += CCZ()

    #for testing, print quantum_oracle and print the state
    wavefunction_simulator = WavefunctionSimulator()
    wavefunction = wavefunction_simulator.wavefunction(quantum_oracle)

    print(f"Number {nr}")
    print(wavefunction)

    return quantum_oracle
    
def grovers_circuit():
    grovers_circuit = Program()
    grovers_circuit += quantum_oracle()
    grovers_circuit += amplification()

    ro = grovers_circuit.declare('ro', 'BIT', 3)
    grovers_circuit += MEASURE(0, ro[0])
    grovers_circuit += MEASURE(1, ro[1])
    grovers_circuit += MEASURE(2, ro[2])
    
    qvm = get_qc('3q-qvm')
    results = []
    for i in range(100):
        results.append(qvm.run(grovers_circuit).tolist())

    return results

def plot_histogram(results):
    unique = []
    for x in results:
        if x not in unique:
            unique.append(x)

    tally = []        
    for i in range(len(unique)):
        tally.append(results.count(unique[i])/100)

    y_pos = np.arange(len(unique))
    plt.bar(y_pos, tally, width=0.2, align='center', alpha=0.5)
    plt.xticks(y_pos, unique)
    plt.ylabel('Percentage')
    plt.title('States')
    plt.show()

#quantum attempt
results = grovers_circuit()

#print(results[0])
#print(results[1])
#print(results[2])

plot_histogram(results)