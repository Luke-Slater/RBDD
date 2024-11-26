import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pysat.formula import *
from PARSER.Parser import Parser
from RBDD.RBDD import RBDD
from RBDD.PROCEDURES import PROCEDURES
import time, os
import multiprocessing

def tuple_to_formula(tup):
    if tup[0] == "AND":
        return And(tuple_to_formula(tup[1]), tuple_to_formula(tup[2]))
    elif tup[0] == "OR":
        return Or(tuple_to_formula(tup[1]), tuple_to_formula(tup[2]))
    elif tup[0] == "IMPLIES":
        return Implies(tuple_to_formula(tup[1]), tuple_to_formula(tup[2]))
    elif tup[0] == "NEG":
        return Neg(tuple_to_formula(tup[1]))
    elif tup[0] == "ATOM":
        return Atom(int(tup[1]))

def process_pair(pair, start, end):
    pair_1 = pair[0]
    pair_2 = pair[1]
    c = Parser("")
    for i in range(start, end):
        instance = str(i) + "_" + str(pair[0]) + "_" + str(pair[1])

        start = time.perf_counter()

        with open("DATA/NMR_PAPER_RBDDs/" + instance + ".txt") as file:
            n = int(file.readline().strip("\n"))
            sig = file.readline().strip("\n").split(" ")
            o = [int(x) for x in file.readline().strip("\n").split(" ")]
            sigs = [(sig[i],i+1) for i in range(0, len(sig))]

        file_name = "DATA/NMR_PAPER_QBDDs/" + instance + ".txt"
        O = []

        with open("DATA/BELIEF_BASES_ENCODED/" + instance + ".txt") as file:
            conditionals = []
            for line in file:
                conditionals.append(eval(line.strip("\n")))
            conditionals = [tuple_to_formula(c) for c in conditionals]
            for q in conditionals:
                O.append(o)

        queries = []
        for c in conditionals:
            queries.append((And(c.left,c.right),And(c.left,Neg(c.right))))

        rbdd = RBDD.from_file("DATA/NMR_PAPER_RBDDs/" + instance + ".txt")
        rbdd.find_ranks(set())
        total = 0
        for x, q in enumerate(queries):
            q_1 = q[0]
            q_2 = q[1]
            f = [q_1,q_2]
            start = time.perf_counter()
            cbdd, n = RBDD.build_vector(f,[None]+O[x])
            #r_, n_ = OBDD.build(q_2,[None]+O[x])
            end = time.perf_counter()
            #r.write_to_file(file_name)
            total += end-start
            cbdd.find_ranks(set())
            start = time.perf_counter()
            result = PROCEDURES.entails(rbdd,cbdd)
            end = time.perf_counter()
            total += end-start
        return total

def parallel_process(pair):
    num_processors = 8  
    pool = multiprocessing.Pool(processes=num_processors)

    total_range = 100  
    chunk_size = (total_range + num_processors - 1) // num_processors  
    ranges = [(i * chunk_size, min((i + 1) * chunk_size, total_range)) for i in range(num_processors)]

    result_objects = []

    for start, end in ranges:
        result = pool.apply_async(process_pair, args=(pair, start, end))
        result_objects.append(result)

    results = []
    for result in result_objects:
        results.append(result.get())

    pool.close()  
    pool.join()   
    return results


if __name__ == '__main__':

    pair_1 = sys.argv[1]
    pair_2 = sys.argv[2]
    pair = (int(pair_1),int(pair_2))
    n = parallel_process(pair)
    print("RESULTS: " + str(pair[0]) + "_" + str(pair[1]))
    print("AVERAGE COMPILE TIME: " + str((sum(n)/1000)*1000))

