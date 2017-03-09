import problog as pl
import pipeline.hugin2problog as h2p


class Pipeline:

    def continue_pipeline(self, plProgram, inferenceEngine):
        lf = pl.formula.LogicFormula.create_from(plProgram)  # ground into logic formula
        cnf = pl.cnf_formula.CNF.create_from(lf)     # get CNF
        print(cnf)
        if inferenceEngine is None:
            None #TODO
        else:
            None #TODO


    def execProbLogModel(self, probLogProgram, inferenceEngine=None):
        if (inferenceEngine is None):
            p = probLogProgram[0]
            if (probLogProgram[1] is not None):
                p += probLogProgram[1]
            if (probLogProgram[2] is not None):
                p += probLogProgram[2]
            self.continue_pipeline(pl.program.PrologString(p), None)
        else:
            None  # TODO
            # lf = pl.engine.ground(plProgram[0],pl.formula.LogicFormula(),plProgram[2],plProgram[1])


    def execBayesianNetwork(self, bayesianNetwork, inferenceEngine=None):
        h2p.main()  # TODO