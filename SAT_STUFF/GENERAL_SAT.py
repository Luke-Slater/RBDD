from pysat.formula import *
from pysat.solvers import Solver
import time

class SAT:

    @staticmethod
    def base_rank(conditionals):
        K = [[]]
        next = conditionals
        i = 0
        while True:
            f = And(*[Implies(conditional[0], conditional[1]) for conditional in next])
            temp = next
            next = []
            for conditional in temp:
                with Solver(bootstrap_with=And(f, conditional[0])) as solver:
                    result = solver.solve()
                    if result is not True:
                        next.append(conditional)
                    else:
                        K[i].append(conditional)
            if next == [] or K[i] == [] or (K[i] == K[i-1] and i>0):
                if K[i] == []: K = K[:-1]
                break
            else:
                K.append([])
                i += 1
        return K

    @staticmethod
    def entails(ranking, conditional):
        pos = And(conditional[0], conditional[1])
        neg = And(conditional[0], Neg(conditional[1]))
        if ranking == []:
            return False
        k = len(ranking)-1
        total = 0
        def recZinf(j, total):
            test = And(*[ranking[h] for h in range(j,k+1)])
            with Solver(bootstrap_with=And(test, pos)) as solver:
                start = time.perf_counter()
                result1 = solver.solve()
                end = time.perf_counter()
                total += end-start
            if result1 is False:
                return False, total
            with Solver(bootstrap_with=And(test, neg)) as solver:
                start = time.perf_counter()
                result2 = solver.solve()
                end = time.perf_counter()
                total += end-start
            if result2 is True:
                if j == 0:
                    return False, total
                result3 = recZinf(j-1, total)
                if result3 is False:
                    return False, total
            return True, total
        with Solver(bootstrap_with=conditional[0]) as solver:
            result = solver.solve()
        if result is False:
            return True, total
        else:
            result, total = recZinf(k, total)
            return result, total