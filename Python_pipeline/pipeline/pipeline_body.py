import problog as pl
import pipeline.hugin2problog as h2p
from subprocess import check_output
import pipeline.cnf_converter as cnfconv


class Pipeline:

    def continue_pipeline(self, plProgram, inferenceEngine):
        lf = pl.formula.LogicFormula.create_from(plProgram)  # ground into logic formula

        if inferenceEngine is None:  # run all queries at once with Problog
            cnf = pl.cnf_formula.CNF.create_from(lf)  # get CNF
            nnf = pl.nnf_formula.NNF.create_from(cnf)  # transform to nnf
            return nnf.evaluate()  # compute conditional probabilities
        else:  # run queries one at a time for other inference engines
            None
            """
            result = []
            for query in q:
                print("-----------------------------")
                print(query)
                lf.clear_queries()
                lf.add_query(query[0],query[1])
                cnf = pl.cnf_formula.CNF.create_from(lf)  # get CNF

                #text_file = open("temp.cnf", "w")
                #text_file.write(cnf.to_dimacs(weighted=True))
                #text_file.close()
                print("-HEEEEEEEEEEEEERE")
                print(cnf.get_weights())


                self.createFile(cnf)
                #print(lf)
                output = check_output([inferenceEngine, "-c", "temp.cnf", "-W", "--vtree_type", "i", "--vtree_method", "2"])
                something = output.decode("utf-8")
                print(something)
                result.append(something)
            return result
            """


    # Enter a ProbLog program as a tuple: (model, evidence, queries)
    def execProbLogModel(self, probLogProgram, inferenceEngine=None):
        p = probLogProgram[0]
        if (probLogProgram[1] is not None):
            p += probLogProgram[1]
        if probLogProgram[2] is not None:
            for query in probLogProgram[2]:
                p+= query + "\n"
        return self.continue_pipeline(pl.program.PrologString(p), inferenceEngine)


    # Enter the relative path to a Bayesian network file (.net extension)
    def execBayesianNetwork(self, bayesianNetwork, inferenceEngine=None):
        output_filename = "output_" + bayesianNetwork[0]  # output to "output_<input_file_name>"
        command_list = []
        command_list.append(bayesianNetwork[0])
        command_list.append("-o")
        command_list.append(output_filename)
        h2p.main(command_list)

        #query = " query(hREKG(\"LOW\"))."
        query = " query(pRESS(\"HIGH\"))."
        #query = " query(kINKEDTUBE)."
        with open(output_filename, "a") as myfile:
            myfile.write(query)

        cnfconverter = cnfconv.CNFConverter()
        grounded = cnfconverter.ground(None,output_filename)
        cnfconverter.convert_to_cnf(grounded, query)


        return self.continue_pipeline(pl.program.PrologFile(output_filename), inferenceEngine)


    # Create a temporal cnf file which is used by minic2d
    def createFile(self, cnf):
        limit = cnf.atomcount + 1
        str_weight = "c weights "

        # pl.evaluator.Evaluator
        print(cnf.get_names_with_label())
        print(cnf.evidence())
        print(cnf.labeled())
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
                if temp == "True":
                    str_weight += "1 1 "
                    continue
                complement = 1.00 - float(temp)
                complement = round(complement, 2)
                str_weight += str(temp) + " " + str(complement) + " "
            else:
                str_weight += "1 1 "

        text_file = open("temp.cnf", "w")
        text_file.write(str_weight + "\n" + cnf.to_dimacs())
        text_file.close()