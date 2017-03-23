from pipeline.variable import Variable
from pipeline.probLogPrograms import ProbLogProgram
import re
import problog
from subprocess import check_output

class CNFConverter():

    def __init__(self):
        self.variables = []
        self.clauses = []
        self.evidence = []
        self.query = None


    def ground(self, ProblogProgram):
        f = open('problog.pl', 'w')
        f.write(ProblogProgram)
        f.close()
        return check_output(["problog", "ground", "problog.pl"]).decode("utf-8")
        #return check_output(["problog", "ground", "problog.pl", "--compact"]).decode("utf-8")


    def convert_to_cnf(self, groundedProgr):
        lines = groundedProgr.split('\n')
        for line in lines:
            pattern = re.compile(r'\s+')
            line = re.sub(pattern, '', line)
            if line == "":
                continue
            elif line.startswith("evidence("):
                self.storeEvidence(line)
                continue
            elif line.startswith("query("):
                self.storeQuery(line)
                continue
            self.parseLine(line)
        print(len(self.variables))
        print(self.variables)
        for var in self.variables:
            print(var.name + "   " + str(var.id))
        print("================================")
        for clause in self.clauses:
            print(clause)


    def parseLine(self, line):
        parts = line.split(':-')
        if(len(parts) == 1):
            self.parseVariable(parts[0])
        else:
            self.parseClause(parts[0], parts[1])


    def parseVariable(self,line):
        parts = line.split(';')
        last_part = parts[len(parts)-1]
        if(last_part.endswith(".")):
            parts[len(parts)-1] = last_part[0:-1]
        if(len(parts) == 1):
            self.binaryVariable(parts[0])
        else:
            self.nonBinaryVariable(parts)


    def binaryVariable(self,variable):
        parts = variable.split("::")
        v_true = Variable(parts[1],len(self.variables)+1,(1,1))     # true lambda variable
        v_false = Variable("not_" + parts[1], len(self.variables) + 2,(1,1))  # false lambda variable
        rho = Variable("rho_" + parts[1], len(self.variables)+3, (parts[0], str(1-float(parts[0]))))  # rho variable
        self.variables.append(v_true)
        self.variables.append(v_false)
        self.variables.append(rho)
        self.clauses.append(str(v_true.id) + " " + str(v_false.id))  # true lambda or false lambda
        self.clauses.append("-" + str(v_true.id) + " -" + str(v_false.id))  # not true lambda or not false lambda
        self.clauses.append("-" + str(rho.id) + " " + str(v_true.id))  # not rho or true lambda
        self.clauses.append(str(rho.id) + " " + str(v_false.id))  # rho or false lambda


    def nonBinaryVariable(self,variables):
        split_vars = []
        for var in variables:
            parts = var.split("::")
            split_vars.append(parts)
        lambdas = []
        rhos = []
        for i in range(len(split_vars)):
            lambdas.append(Variable(split_vars[i][1],len(self.variables) + 2*i + 1,(1,1)))
            if(i != len(split_vars)-1):
                rhos.append(Variable("rho_"+split_vars[i][1],len(self.variables) + 2*(i+1),(split_vars[i][0], str(1-float(split_vars[i][0])))))
        self.variables.extend(lambdas)
        self.variables.extend(rhos)

        lambdastring = ""
        for l in lambdas:
            lambdastring += str(l.id) + " "
        self.clauses.append(lambdastring)

        for i in range(len(lambdas)):
            for j in range(i+1, len(lambdas)):
                self.clauses.append("-" + str(lambdas[i].id) + " -" + str(lambdas[j].id))

        for i in range(len(lambdas)):
            lambdastring = str(lambdas[i].id) + " "
            if(i != len(lambdas)-1):
                lambdastring += "-" + str(rhos[i].id) + " "
            for j in range(0,i):
                lambdastring += str(rhos[j].id) + " "
            self.clauses.append(lambdastring)


    def parseClause(self,header,body):
        None #TODO


    def storeEvidence(self, evidence):
        self.evidence.append(evidence[9:-2])


    def storeQuery(self, query):
        self.query = query[6:-2]


plp = ProbLogProgram()
cnfconverter = CNFConverter()
model = plp.task11()[0] + plp.task11()[1] #+ plp.task11()[2][0]
grounded = cnfconverter.ground(model)
cnfconverter.convert_to_cnf(grounded)

