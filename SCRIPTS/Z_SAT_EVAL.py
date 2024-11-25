import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pysat.formula import *
from PARSER.Parser import Parser
from pyeda.inter import expr
from SAT_STUFF.GENERAL_SAT import SAT
import pickle, time, sys

c = Parser("")

pair_1 = sys.argv[1]
pair_2 = sys.argv[2]
pair = (int(pair_1),int(pair_2))

total = 0
for i in range(0,100):
    with open("DATA/RAW_BELIEF_NMR_PAPER/" + str(i) + "_" + str(pair[0]) + "_" + str(pair[1]) + "/signature.txt") as file:
        sig = file.readline().split(",")

    name = "DATA/RAW_QUERIES_NMR_PAPER/randomQueries_" + str(pair[0]) + "_" + str(pair[1]) + "_" + str(i) + ".clq"
    queries = []
    with open(name, 'r') as file:
        for j in range(0,10):
            exp = expr(file.readline().strip("\n"))
            queries.append((c.toPySAT(exp.xs[1],sig), c.toPySAT(exp.xs[0],sig)))

    conditionals = []
    for j in range(0, pair[1]):
        with open("DATA/RAW_BELIEF_NMR_PAPER/" + str(i) + "_" + str(pair[0]) + "_" + str(pair[1]) + "/" + str(j) + ".pkl", "rb") as file:
            conditional = pickle.load(file)
            conditionals.append(conditional)

    conditionals2 = [(c.toPySAT(conditional[1],sig), c.toPySAT(conditional[0],sig)) for conditional in conditionals]
    K = SAT.base_rank(conditionals2)
    K = [And(*[Implies(conditional[0],conditional[1]) for conditional in k]) for k in K]
    
    for q in queries:
        result, tot = SAT.entails(K,q)
        total += tot

print("RESULTS: " + str(pair[0]) + "_" + str(pair[1]))
print("AVERAGE ENTAILMENT TIME: " + str((total/1000)*1000))
with open("DATA/BENCHMARK_RESULTS/SAT_RESULTS.txt", "a") as file:
    file.write(str(pair) + ": " + str((total/1000)*1000) + "\n")

        

        