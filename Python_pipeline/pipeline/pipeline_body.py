import problog as pl
import pipeline.hugin2problog as h2p
from subprocess import check_output


class Pipeline:

    def continue_pipeline(self, plProgram, inferenceEngine):
        lf = pl.formula.LogicFormula.create_from(plProgram)  # ground into logic formula
        cnf = pl.cnf_formula.CNF.create_from(lf)     # get CNF
        if inferenceEngine is None:  # use problog to solve
            nnf = pl.nnf_formula.NNF.create_from(cnf)  # transform to nnf
            return nnf.evaluate()   # compute conditional probabilities
        else:  # use inference engine (miniC2D)
            self.createFile(cnf)
            output = check_output([inferenceEngine, "-c", "temp.cnf", "-W", "--vtree_type", "i", "--vtree_method", "2"])
            return output.decode("utf-8")


    # Enter a ProbLog program as a tuple: (model, evidence, queries)
    def execProbLogModel(self, probLogProgram, inferenceEngine=None):
        p = probLogProgram[0]
        if (probLogProgram[1] is not None):
            p += probLogProgram[1]
        if (probLogProgram[2] is not None):
            p += probLogProgram[2]
        return self.continue_pipeline(pl.program.PrologString(p),inferenceEngine)

    # Enter the relative path to a Bayesian network file (.net extension)
    def execBayesianNetwork(self, bayesianNetwork, inferenceEngine=None):
        output_filename = "output_" + bayesianNetwork[0]  # output to "output_<input_file_name>"
        bayesianNetwork.append("-o")
        bayesianNetwork.append(output_filename)
        h2p.main(bayesianNetwork)
        return self.continue_pipeline(pl.program.PrologFile(output_filename), inferenceEngine)

    # Create a temporal cnf file which is used by minic2d
    def createFile(self, cnf):
        limit = cnf.atomcount + 1
        str_weight = "c weights "

        for i in range(1, limit):
            if i in (x[1] for x in cnf.evidence()):
                str_weight += "1 0 "
            elif -i in (x[1] for x in cnf.evidence()):
                str_weight += "0 1 "
            elif i in (x[1] for x in cnf.labeled()):
                str_weight += "1 0 "
            elif -i in (x[1] for x in cnf.labeled()):
                str_weight += "0 1 "
            elif i in cnf.get_weights():
                temp = str(cnf.get_weights()[i])
                complement = 1 - float(temp)
                str_weight += temp + " " + str(complement) + " "
            else:
                str_weight += "1 1 "

        text_file = open("temp.cnf", "w")
        text_file.write(str_weight + "\n" + cnf.to_dimacs())
        text_file.close()