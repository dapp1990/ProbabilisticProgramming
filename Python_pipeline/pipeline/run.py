from pipeline.probLogPrograms import ProbLogProgram
from pipeline.pipeline_body import Pipeline

p = Pipeline()
plp = ProbLogProgram()
bn = ["alarm.net"]

p.execBayesianNetwork(bn)

#task11 = plp.task11()
#p.execProbLogModel(task11)
