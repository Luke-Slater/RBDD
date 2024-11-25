from pyeda.inter import *
from pyeda.boolalg.expr import *
from pysat.formula import Neg as SAT_Neg, Atom as SAT_Atom, Or as SAT_Or, And as SAT_And, Implies as SAT_Implies

class Parser:
    def __init__(self, path):
        if path != "":
                
            self.path = path
            with open(path, 'r') as file:
                content = file.readlines()
            
            self.vars = content[0].strip().split(',')
            self.vars = [None] + [SAT_Atom(v) for v in self.vars]
            content.pop(0)
            
            conditionals = []
            for conditional in content:
                conditionals.append(conditional.rstrip('r').strip().strip(','))

            #replacements = {'!': '~', ',': '&', ';': '|'}
            #translation_table = str.maketrans(replacements)

            formulas = []
            for c in conditionals:
                xs = c.split("|~")
                #xs = [x.translate(translation_table) for x in xs]
                formulas.append(expr(xs[0] + "=>" + xs[1]))

            pysat_formulas = []
            for f in formulas:
                pysat_formulas.append(self.toPySAT(f))

            self.formulas = pysat_formulas

    def toPySAT(self, f, sig):
        if not isinstance(f, Expression):
            f = expr(f)
        if isinstance(f, Complement):
            x = SAT_Atom(sig.index(str(f)[1:])+1)
            return SAT_Neg(x)
        elif isinstance(f, Variable):
            x = SAT_Atom(sig.index(str(f))+1)
            return x
        elif isinstance(f, NotOp):
            f = SAT_Neg(self.toPySAT(f.xs[0], sig))
            return f
        elif isinstance(f, AndOp):
            f = SAT_And(*[self.toPySAT(x, sig) for x in f.xs])
            return f
        elif isinstance(f, OrOp):
            f = SAT_Or(*[self.toPySAT(x, sig) for x in f.xs])
            return f
        elif isinstance(f, ImpliesOp):
            f = SAT_Implies(*[self.toPySAT(x, sig) for x in f.xs])
            return f
