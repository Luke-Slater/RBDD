import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pysat.formula import *
from pyeda.inter import expr
from PARSER.Parser import Parser
from RBDD.RBDD import RBDD
from SAT_STUFF.GENERAL_SAT import SAT
from RBDD.PROCEDURES import PROCEDURES
import pickle, time, os, re
import multiprocessing

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

        with open("DATA/RAW_QUERIES_NMR_PAPER/randomQueries_" + str(pair_1) + "_" + str(pair_2) + "_" + str(i) + ".clq") as file:
            queries = []
            for j in range(0,10):
                temp = sigs
                string = file.readline().strip("\n")
                for k, s in enumerate(sig):
                    pattern = r'\b' + re.escape(s) + r'\b'
                    matches = re.findall(pattern, string)
                    if len(matches) == 0:
                        temp = [x for x in temp if x[0] != s]
                exp = expr(string)
                q = (c.toPySAT(exp.xs[1],sig), c.toPySAT(exp.xs[0],sig))
                queries.append((And(q[0], q[1]),And(q[0],Neg(q[1]))))
                
        
                #O.append([x for x in o if x in [y[1] for y in temp]])
                O.append(o)


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

