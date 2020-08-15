#Submitted by: M. Ashish
#Roll No.: EP17B006

import sys
arg=sys.argv
import numpy as np
import cmath
import math

#Initializing all variables which will be used later

CIRCUIT = '.circuit'
END = '.end'
AC = '.ac'
cktlines = []
components = []
nodeslist = []
nodes = {}; nodesinv = {}
hashrem = 0
n=0; k=0

frequency = 0

#Verifying, opening and reading the netlist file

if len(arg)!=2:
    print("\nPlease enter %s <inputfile>." % arg[0])
    exit()

try:
    with open(arg[1]) as f:
        lines = f.readlines()
        start = -1; end = -2

        #Extracting the required lines only and removing comments

        for line in lines:
            if CIRCUIT == line[:len(CIRCUIT)]:
                start = lines.index(line)
            elif END == line[:len(END)]:
                end = lines.index(line)
                break
        if start>=end:
            print('This file does not contain a valid circuit!')
            exit()

        #Reading the value of frequency for AC Circuits

        for line in lines:
            if AC == line[:len(AC)]:
                
                frequency = float(line.split()[2])          # Since we are working with only one frequency
        
            
        for line in lines[start+1:end]:
            cktlines.append(line.split())

        #Removing comments

        for i in range(0,len(cktlines)):
            for j in range(0,len(cktlines[i])):
                if cktlines[i][j][0]=='#':
                    hashrem = cktlines[i].index('#')
                    for l in range(0,len(cktlines[i])-hashrem):
                        cktlines[i].pop()
                    break

except IOError:
    print('Invalid file!')
    exit()

#Defining classes for each type of element in a circuit

class Resistor:
    def __init__(self, name, n1, n2, value):
        self.type = 'R'
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.value = value

class Inductor:
    def __init__(self, name, n1, n2, value):
        self.type = 'L'
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.value = complex(0, 2*math.pi*frequency*float(value))

class Capacitor:
    def __init__(self, name, n1, n2, value):
        self.type = 'C'
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.value = complex(0, (-1/(2*math.pi*frequency*float(value))))

class IVS:
    def __init__(self, name, n1, n2, vtype, value, phase):
        self.type = 'V'
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.vtype = vtype
        if vtype=='dc':
            self.value = float(value)
        elif vtype=='ac':
            self.value = float(value)*complex(math.cos(float(phase)), math.sin(float(phase)))
        self.phase = phase

#Note:  Even though we are only working with Independent voltage sources, resistors, capacitors and inductors right now,
#       I am defining classes for other types of elements also as it can be used later in the course.

class ICS:
    def __init__(self, name, n1, n2, value):
        self.type = 'I'
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.value = value

class VCVS:
    def __init__(self, name, n1, n2, dn1, dn2, value):
        self.type = 'E'
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.dn1 = dn1
        self.dn2 = dn2
        self.value = value

class VCCS:
    def __init__(self, name, n1, n2, dn1, dn2, value):
        self.type = 'G'
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.dn1 = dn1
        self.dn2 = dn2
        self.value = value

#Saving each component as an object in a list

for i in range(0,len(cktlines)):
    if cktlines[i][0][0]=='R':
        components.append(Resistor(cktlines[i][0], cktlines[i][1], cktlines[i][2], cktlines[i][3]))
    elif cktlines[i][0][0]=='L':
        components.append(Inductor(cktlines[i][0], cktlines[i][1], cktlines[i][2], cktlines[i][3]))
    elif cktlines[i][0][0]=='C':
        components.append(Capacitor(cktlines[i][0], cktlines[i][1], cktlines[i][2], cktlines[i][3]))
    elif cktlines[i][0][0]=='V':
        if cktlines[i][3]=='dc':
            components.append(IVS(cktlines[i][0], cktlines[i][1], cktlines[i][2], cktlines[i][3], cktlines[i][4], 0))
        elif cktlines[i][3]=='ac':
            components.append(IVS(cktlines[i][0], cktlines[i][1], cktlines[i][2], cktlines[i][3], cktlines[i][4], cktlines[i][5]))
    elif cktlines[i][0][0]=='I':
        components.append(ICS(cktlines[i][0], cktlines[i][1], cktlines[i][2], cktlines[i][3]))
    elif cktlines[i][0][0]=='E':
        components.append(VCVS(cktlines[i][0], cktlines[i][1], cktlines[i][2], cktlines[i][3], cktlines[i][4], cktlines[i][5]))
    elif cktlines[i][0][0]=='G':
        components.append(VCCS(cktlines[i][0], cktlines[i][1], cktlines[i][2], cktlines[i][3], cktlines[i][4], cktlines[i][5]))

#Retrieving the list of all unique nodes in the circuit

nodeslist.append('GND')
for component in components:
    nodeslist.append(component.n1)
    nodeslist.append(component.n2)
nodeslist = list(dict.fromkeys(nodeslist))

#Defining a dictionary with node name as key and an integer as value

for i in range(0,len(nodeslist)):
    nodes[nodeslist[i]]=i
    nodesinv[i] = nodeslist[i]

#Calculating the number of unique nodes and voltage sources

n = len(nodeslist)
for component in components:
    if component.type=='V':
        k=k+1
    elif component.type=='E':
        k=k+1

#Initializing matrices which need to be solved

A = np.array([[complex(0.,0.) for i in range(k+n)] for j in range(k+n+1)])
b = np.array([complex(0.,0.) for i in range(k+n+1)])

A[k+n][nodes['GND']] = 1    #Setting the voltage at ground to be 0

#Updating the element of matrix depending on the type of component

vs = {}; vsinv = {}
v_source_no=-1
for component in components:
    if component.type=='R':
        node1 = nodes[component.n1]
        node2 = nodes[component.n2]
        A[node1][node1] = A[node1][node1] + (1/float(component.value))
        A[node2][node2] = A[node2][node2] + (1/float(component.value))
        A[node1][node2] = A[node1][node2] - (1/float(component.value))
        A[node2][node1] = A[node2][node1] - (1/float(component.value))

    elif component.type=='C':
        node1 = nodes[component.n1]
        node2 = nodes[component.n2]
        A[node1][node1] = A[node1][node1] + (1/(component.value))
        A[node2][node2] = A[node2][node2] + (1/(component.value))
        A[node1][node2] = A[node1][node2] - (1/(component.value))
        A[node2][node1] = A[node2][node1] - (1/(component.value))

    elif component.type=='L':
        node1 = nodes[component.n1]
        node2 = nodes[component.n2]
        A[node1][node1] = A[node1][node1] + (1/(component.value))
        A[node2][node2] = A[node2][node2] + (1/(component.value))
        A[node1][node2] = A[node1][node2] - (1/(component.value))
        A[node2][node1] = A[node2][node1] - (1/(component.value))

    elif component.type=='V':
        v_source_no = v_source_no+1
        node1 = nodes[component.n1]
        node2 = nodes[component.n2]
        vs[component.name] = v_source_no
        vsinv[v_source_no] = component.name
        A[node1][n+v_source_no] = 1
        A[node2][n+v_source_no] = -1
        A[n+v_source_no][node1] = -1
        A[n+v_source_no][node2] = 1
        b[n+v_source_no] = b[n+v_source_no] + component.value
        
#Deleting the KCL analysis at GND because the equations are getting repeated (and thereby making the matrix a square matrix)

A = np.delete(A, (0), axis = 0)
b = np.delete(b, (0), axis = 0)

#Solving the matrix equation

try:
    x = np.linalg.solve(A,b)
except ValueError as e:
    print("The circuit cannot be solved!")
    print(e)

#Printing the node voltages and current through voltage sources in phasor form.

for i in range(n):

    string = str(abs(x[i])) + ' <' + str(cmath.phase(x[i]))
    
    print("The Voltage at node %s is %s volts" %(nodesinv[i], string))

for i in range(k):

    string = str(abs(x[n+i])) + ' <' + str(cmath.phase(x[n+i]))
    print("The current through the voltage source %s is %s amperes." %(vsinv[i], string))

print("Note: Please note that all the outputs are printed in the form r <t\n      where r is the modulus and t is the phase.")
