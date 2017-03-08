import problog as pl


def bayesianNetWork2ProbLog(bayesianNetwork):
    None # TODO


def ground(plProgram):
    None # TODO


def getCNF(plProgram):
    formula = pl.formula.LogicFormula.create_from(plProgram)
    cnf = pl.cnf_formula.CNF.create_from(formula)
    return cnf


def continue_pipeline(plProgram):
    plProgram = ground(plProgram)
    cnf = getCNF(plProgram)


def loadProbLog(probLog):
    ProbLogProgram = pl.program.PrologString(probLog)


def loadBayesianNetwork(bayesianNetwork):
    ProbLogProgram = None # TODO

