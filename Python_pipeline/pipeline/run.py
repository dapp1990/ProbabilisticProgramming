#!/usr/bin/python3

from pipeline.probLogPrograms import ProbLogProgram
from pipeline.pipeline_body import Pipeline

miniC2D_exec_path = "/home/babyburger/Documents/prob/miniC2D-1.0.0/bin/linux/miniC2D"

p = Pipeline()
plp = ProbLogProgram()

# bn = ["alarm.net"]
# p.execBayesianNetwork(bn)

task11 = plp.task11()
result = p.execProbLogModel(task11)
print(result)