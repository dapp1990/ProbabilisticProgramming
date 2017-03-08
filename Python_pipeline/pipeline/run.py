import problog as pl
from pipeline.probLogModels import Models


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


def loadProbLog(probLogModel):
    plProgram = pl.program.PrologString(probLogModel)
    return plProgram


def loadBayesianNetwork(bayesianNetwork):
    plProgram = None # TODO


task11 = Models().task11()
print(loadProbLog(task11))
print(getCNF(loadProbLog(task11)))