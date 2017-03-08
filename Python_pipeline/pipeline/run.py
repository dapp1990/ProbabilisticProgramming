from pipeline.probLogModels import Models
from pipeline.pipeline_body import Pipeline

p = Pipeline()
task11 = Models().task11()
print(p.execProbLogModel(task11))
print(p.getCNF(p.execProbLogModel(task11)))