import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pysat.formula import *
from PARSER.Parser import Parser
from RBDD.RBDD import RBDD
from SAT_STUFF.GENERAL_SAT import SAT
import pickle, time, os, re, random
import multiprocessing

def generate_random_unique_permutations(input_list, num_permutations):
    seen_permutations = set()  # Use a set to track unique permutations
    permutations = []
    
    attempts = 0
    max_attempts = num_permutations * 10  # Limit attempts to avoid infinite loops

    while len(permutations) < num_permutations and attempts < max_attempts:
        shuffled = input_list[:]  # Make a copy of the list
        random.shuffle(shuffled)  # Shuffle the copy in place
        perm_tuple = tuple(shuffled)  # Convert to a tuple for set storage
        
        if perm_tuple not in seen_permutations:
            seen_permutations.add(perm_tuple)
            permutations.append(list(perm_tuple))
        
        attempts += 1

    if attempts == max_attempts:
        print("Warning: Reached maximum attempts. Could not generate all unique permutations requested.")
    
    return permutations

def process_pair(pair, start, end):
    c = Parser("")
    for i in range(start, end):
        instance = str(i) + "_" + str(pair[0]) + "_" + str(pair[1])

        start = time.perf_counter()
        with open("DATA/RAW_BELIEF_NMR_PAPER/" + instance + "/signature.txt") as file:
            sig = file.readline().split(",")

        counts = [(0,sig[i]) for i in range(0, len(sig))]

        file_name = "DATA/NMR_PAPER_RBDDs/" + instance + ".txt"

        try: 
            with open(file_name, 'r') as file: 
                n_ = int(file.readline().strip("\n")) 
                if n_ < 200: continue
        except FileNotFoundError: n_ = 9999999999

        conditionals = []
        for j in range(0, pair[1]):
            with open("DATA/RAW_BELIEF_NMR_PAPER/" + instance + "/" + str(j) + ".pkl", "rb") as file:
                conditional = pickle.load(file)
                
                for k, s in enumerate(sig):
                    pattern = r'\b' + re.escape(s) + r'\b'
                    matches = re.findall(pattern, str(conditional[1]))
                    counts[k] =  (counts[k][0] + len(matches), counts[k][1])

                conditionals.append(conditional)

        
        conditionals2 = [(c.toPySAT(conditional[1],sig), c.toPySAT(conditional[0],sig)) for conditional in conditionals]
        K = SAT.base_rank(conditionals2)
    
        f = []

        for j in range(0, len(K)):
            f.append(And(*[Implies(K[j][k][0], K[j][k][1]) for k in range(0, len(K[j]))]))

        counts = sorted(counts, key=lambda x: x[0], reverse=True)
        sig1 = [sig.index(count[1])+1 for count in counts]
        sigs = generate_random_unique_permutations(sig1, 1)
        #sigs = sigs + [sig1]
        
        min_n = 99999999999999999
        max_n = 0
        min_r = ""
        min_sig = ""

        start = time.perf_counter()
        for s in sigs:
            r, n = RBDD.build_sysz(f,[None]+s)
            if n < min_n:
                min_n = n
                min_r = r
                min_sig = s
            if n > max_n:
                max_n = n
        
        end = time.perf_counter()
        rbdd_time = end-start

        try: 
            with open(file_name, 'r') as file: 
                n = int(file.readline().strip("\n")) 
        except FileNotFoundError: n = 9999999999

        if min_n < n:
            print("HIT")
            with open(file_name, 'w') as file:
                file.write(str(min_n) + "\n")
                file.write(" ".join(sig) + "\n")
                file.write(" ".join([str(dd) for dd in min_sig]) + "\n")
            min_r.write_to_file(file_name)
        else:
            min_n = n

        print("RESULTS: " + str(instance) + "\nRBDD time: " + str(rbdd_time)
               + "\nNODE COUNT: " + str(min_n) + "\nMAX COUNT: " + str(max_n))

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

    for result in result_objects:
        result.get() 

    pool.close()  
    pool.join()   


if __name__ == '__main__':

    pair_1 = sys.argv[1]
    pair_2 = sys.argv[2]
    pair = (int(pair_1),int(pair_2))
    n = parallel_process(pair)

