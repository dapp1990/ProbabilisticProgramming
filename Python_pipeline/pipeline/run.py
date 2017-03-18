#!/usr/bin/python3

from pipeline.probLogPrograms import ProbLogProgram
from pipeline.pipeline_body import Pipeline

miniC2D_exec_path = "/home/babyburger/Documents/prob/miniC2D-1.0.0/bin/linux/miniC2D"

p = Pipeline()
plp = ProbLogProgram()


def runTask11():
    task11 = plp.task11()
    print("===================  problog  ===========================")
    result = p.execProbLogModel(task11)
    print(result)  # contains conditional proabilities
    print("\n\n===================  miniC2D  ===========================")
    result = p.execProbLogModel(task11, miniC2D_exec_path)
    for r in result:
        print(r)


def runTask12():
    task12 = plp.task12()
    print("===================  problog  ===========================")
    result = p.execProbLogModel(task12)
    print(result)  # contains conditional proabilities
    print("\n\n===================  miniC2D  ===========================")
    result = p.execProbLogModel(task12, miniC2D_exec_path)
    for r in result:
        print(r)


def runTask23():
    task23 = plp.task23()
    print("===================  problog  ===========================")
    result = p.execProbLogModel(task23)
    print(result)  # contains conditional proabilities
    print("\n\n===================  miniC2D  ===========================")
    result = p.execProbLogModel(task23, miniC2D_exec_path)
    for r in result:
        print(r)


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