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
        p = probLogProgram[0]
        if (probLogProgram[1] is not None):
            p += probLogProgram[1]
        if (probLogProgram[2] is not None):
            p += probLogProgram[2]
        self.continue_pipeline(pl.program.PrologString(p),inferenceEngine)


    def execBayesianNetwork(self, bayesianNetwork, inferenceEngine=None):
        output_filename = "output_" + bayesianNetwork[0]  # output to "output_<input_file_name>"
        bayesianNetwork.append("-o")
        bayesianNetwork.append(output_filename)
        h2p.main(bayesianNetwork)
        self.continue_pipeline(pl.program.PrologFile(output_filename), inferenceEngine)