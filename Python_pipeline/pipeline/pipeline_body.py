import problog as pl


class Pipeline:

    def ground(self, plProgram):
        None # TODO


    def getCNF(self, plProgram):
        formula = pl.formula.LogicFormula.create_from(plProgram)
        cnf = pl.cnf_formula.CNF.create_from(formula)
        return cnf


    def continue_pipeline(self, plProgram, miniC2D):
        plProgram = self.ground(plProgram)
        cnf = self.getCNF(plProgram)
        if miniC2D:
            None #TODO
        else:
            None #TODO


    def execProbLogModel(self, probLogModel, miniC2D=False):
        plProgram = pl.program.PrologString(probLogModel)
        self.continue_pipeline(plProgram, miniC2D)


    def execBayesianNetwork(self, bayesianNetwork, miniC2D=False):
        plProgram = None # TODO
        self.continue_pipeline(plProgram, miniC2D)