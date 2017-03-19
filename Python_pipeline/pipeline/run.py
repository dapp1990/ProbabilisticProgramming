#!/usr/bin/python3

from pipeline.probLogPrograms import ProbLogProgram
from pipeline.pipeline_body import Pipeline

miniC2D_exec_path = "/home/babyburger/Documents/prob/miniC2D-1.0.0/bin/linux/miniC2D"

p = Pipeline()
plp = ProbLogProgram()


def runTask(task):
    print("===================  problog  ===========================")
    result = p.execProbLogModel(task)
    print(result)  # contains conditional proabilities
    print("\n\n===================  miniC2D  ===========================")
    result = p.execProbLogModel(task, miniC2D_exec_path)
    for r in result:
        print(r)
        None


def runTask11():
    runTask(plp.task11())


def runTask12():
    runTask(plp.task12())


def runTask23():
    runTask(plp.task23())


def runBigBayesianNetwork():
    bn = ["alarm.net"]
    print("===================  problog  ===========================")
    result = p.execBayesianNetwork(bn)
    print(result)
    print("\n\n===================  miniC2D  ===========================")
    result = p.execBayesianNetwork(bn, miniC2D_exec_path)
    for r in result:
        print(r)


runTask11()