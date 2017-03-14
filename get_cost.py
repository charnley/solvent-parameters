import sys
import csv
import numpy as np
import multiprocessing as mp
from charmm_interface import run_dftb_pb

XYZ_DIR = "/home/andersx/projects/mnsol-database/charmm_input"

def split_jobs(jobs, workers):
    """ Split job array into MP
    """
    return [jobs[i::workers] for i in xrange(workers)]

def costworker(tid, lines, costs):

    cost = 0.0

    for line in lines:

        tokens = line.split(";")
        ixyz = XYZ_DIR + "/" + tokens[1] + ".xyz"
        charge = int(tokens[3])
        e_exp = float(tokens[4])
        
        w = 1.0

        if (abs(charge) > 0.00001):
            w = 0.1

        print ixyz, charge, w
        e_calc = run_dftb_pb(ixyz, charge, parameters)
        print e_exp, e_calc

        cost += w * (e_exp - e_calc)**2

    costs[tid] = cost

def run_mnsol_parallel(csv_file, parameters, workers=3):

    f = open(csv_file)
    lines = f.readlines()
    f.close()

    weight = 0.0

    for line in lines:
        tokens = line.split(";")
        charge = int(tokens[3])

        w = 1.0

        if (abs(charge) > 0.00001):
            w = 0.1

        weight += w
    f = open(csv_file)
    lines = f.readlines()
    f.close()

    jobs = split_jobs(lines, workers)

    costs = mp.Array("d", [0.0 for x in xrange(workers)])

    processes = [mp.Process(target=costworker, 
        args=(i, jobs[i], costs)) for i in xrange(workers)]

    for p in processes: p.start() # Fork
    for p in processes: p.join()  # Join

    cost = np.sum(costs) / weight

    return cost



def run_mnsol(csv_file, parameters):

    f = open(csv_file)
    lines = f.readlines()
    f.close()

    cost = 0.0
    weight = 0.0

    for line in lines:

        tokens = line.split(";")
        ixyz = XYZ_DIR + "/" + tokens[1] + ".xyz"
        charge = int(tokens[3])
        e_exp = float(tokens[4])
        
        w = 1.0

        if (abs(charge) > 0.00001):
            w = 0.1

        print ixyz, charge, w
        e_calc = run_dftb_pb(ixyz, charge, parameters)
        print e_exp, e_calc

        weight += w

        cost += w * (e_exp - e_calc)**2

    return cost / weight

if __name__ == "__main__":

    csv_file = sys.argv[1]

    # Dummy parameters
    parameters = np.zeros((19))

    # Netural Radii
    parameters[0]  = 1.47 # RADII["H"]  = 1.47
    parameters[1]  = 1.85 # RADII["C"]  = 1.85
    parameters[2]  = 1.94 # RADII["N"]  = 1.94
    parameters[3]  = 1.70 # RADII["O"]  = 1.70
    parameters[4]  = 2.03 # RADII["F"]  = 2.03
    parameters[5]  = 2.12 # RADII["P"]  = 2.12
    parameters[6]  = 2.49 # RADII["S"]  = 2.49
    parameters[7]  = 2.38 # RADII["Cl"] = 2.38
    parameters[8]  = 3.06 # RADII["Br"] = 3.06

    # Radius Charge Dependence
    parameters[9]  = -0.11 # CHDR["H"]  = -0.11
    parameters[10] = -0.24 # CHDR["C"]  = -0.24
    parameters[11] = -0.01 # CHDR["N"]  = -0.01
    parameters[12] = -0.11 # CHDR["O"]  = -0.11
    parameters[13] = -0.01 # CHDR["F"]  = -0.05
    parameters[14] = -0.01 # CHDR["P"]  = -0.05
    parameters[15] = -0.01 # CHDR["S"]  = -0.05
    parameters[16] = -0.01 # CHDR["Cl"] = -0.05
    parameters[17] = -0.01 # CHDR["Br"] = -0.05

    # Surface tension for Non-Polar Term
    parameters[18] = 0.005 # STEN = 0.005

    # cost = run_mnsol(csv_file, parameters)
    cost = run_mnsol_parallel(csv_file, parameters)
    print cost
