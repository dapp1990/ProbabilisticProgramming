import problog as pl
from subprocess import check_output
import pipeline.cnf_converter as cnfconv


class Pipeline:

    def continue_pipeline(self, probLogProgram, inferenceEngine,outputFileName=None):
        if inferenceEngine is None:  # run all queries at once with Problog
            p = probLogProgram[0]
            if (probLogProgram[1] is not None):
                p += probLogProgram[1]
            if probLogProgram[2] is not None:
                for query in probLogProgram[2]:
                    p += query + "\n"
            plProgram = pl.program.PrologString(p)
            lf = pl.formula.LogicFormula.create_from(plProgram)  # ground into logic formula
            cnf = pl.cnf_formula.CNF.create_from(lf)  # get CNF
            nnf = pl.nnf_formula.NNF.create_from(cnf)  # transform to nnf
            return nnf.evaluate()  # compute conditional probabilities
        else:  # run queries one at a time for other inference engines
            if outputFileName is None:  # create outpufilename (containing model + evidence)
                outputFileName = "problog.pl"
                with open(outputFileName, "w") as myfile:
                    myfile.write(probLogProgram[0])
                    if(probLogProgram[1] is not None):
                        myfile.write(probLogProgram[1])
                    myfile.close()

            index = 1
            results = []
            for query in probLogProgram[2]:
                cnfconverter = cnfconv.CNFConverter()
                new_output_filename = "query" + str(index) + outputFileName
                index += 1
                with open(new_output_filename, "w") as writefile:
                    with open(outputFileName, "r") as readfile:
                        for line in readfile.readlines():
                            writefile.write(line)
                        readfile.close()
                    writefile.write(query)
                    writefile.close()
                grounded = cnfconverter.ground(None, new_output_filename)
                if probLogProgram[1] is None:
                    cnfconverter.convert_to_cnf(grounded, query, "output_"+new_output_filename, True)
                    output = check_output([inferenceEngine, "-c", "output_"+new_output_filename,
                                           "-W"])  # , "--vtree_type", "i", "--vtree_method", "4"])
                    print(output.decode("utf-8"))
                    results.append(output.decode("utf-8"))
                else:
                    cnfconverter.convert_to_cnf(grounded, query, "output_noquery_" + new_output_filename, False)
                    output_noquery = check_output([inferenceEngine, "-c", "output_noquery_" + new_output_filename,
                                           "-W"])  # , "--vtree_type", "i", "--vtree_method", "4"])
                    cnfconverter = cnfconv.CNFConverter()
                    cnfconverter.convert_to_cnf(grounded, query, "output_" + new_output_filename, True)
                    output = check_output([inferenceEngine, "-c", "output_" + new_output_filename,
                                           "-W"])
                    print(output_noquery.decode("utf-8"))
                    print(output.decode("utf-8"))
                    results.append(output_noquery.decode("utf-8"))
                    results.append(output.decode("utf-8"))
            return results


    # Enter a ProbLog program as a tuple: (model, evidence, queries)
    def execProbLogModel(self, probLogProgram, inferenceEngine=None):
        return self.continue_pipeline(probLogProgram, inferenceEngine)


    # Enter the relative path to a Bayesian network file (.net extension)
    def execBayesianNetwork(self, output_filename, inferenceEngine=None):


        queries = [" query(hREKG(\"LOW\")).", " query(pRESS(\"HIGH\")).", " query(aRTCO2(\"LOW\"))."]
        #queries = [" query(pRESS(\"HIGH\")).", " query(aRTCO2(\"LOW\")).", " query(sAO2(\"LOW\"))."]
        #query = " query(hREKG(\"LOW\"))."
        #query = " query(pRESS(\"HIGH\"))."
        #query = " query(kINKEDTUBE)."
        #query = " query(sAO2(\"LOW\"))."
        #query = " query(aRTCO2(\"LOW\"))."

        problogProgram = ""
        with open(output_filename, "r") as myfile:
            for line in myfile.readlines():
                problogProgram += line
                myfile.close()

        return self.continue_pipeline((problogProgram, None, queries), inferenceEngine, output_filename)


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