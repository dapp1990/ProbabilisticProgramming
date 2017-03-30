#!/usr/bin/python3

from pipeline.probLogPrograms import ProbLogProgram
from pipeline.pipeline_body import Pipeline
import pipeline.hugin2problog as h2p

miniC2D_exec_path = "/home/babyburger/Documents/prob/miniC2D-1.0.0/bin/linux/miniC2D"

p = Pipeline()
plp = ProbLogProgram()


def runTask(task):
    print("===================  problog  ===========================")
    result = p.execProbLogModel(task)
    print(result)  # contains conditional probabilities
    print("\n\n===================  miniC2D  ===========================")
    result = p.execProbLogModel(task, miniC2D_exec_path)
    for r in result:
        print(r[0])
        print(r[1])


def runTask11():
    runTask(plp.task11())


def runTask12():
    runTask(plp.task12())


def runTask23():
    print("Task 23 does not work properly for our implementation.")  # this does not work properly
    # runTask(plp.task23())


def runBigBayesianNetwork():
    bn = ["alarm.net"]
    output_filename = "output_" + bn[0]  # output to "output_<input_file_name>"
    command_list = []
    command_list.append(bn[0])
    command_list.append("-o")
    command_list.append(output_filename)
    h2p.main(command_list)
    print("===================  problog  ===========================")
    #result = p.execBayesianNetwork(output_filename)
    #print(result)  # contains conditional probabilities
    print("\n\n===================  miniC2D  ===========================")
    result = p.execBayesianNetwork(output_filename, miniC2D_exec_path)
    for r in result:
        print(r[0])
        print(r[1])


#runTask11()
runTask12()
#runBigBayesianNetwork()
