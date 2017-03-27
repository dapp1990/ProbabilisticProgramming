from pipeline.variable import Variable
from pipeline.probLogPrograms import ProbLogProgram
import re
import problog
from subprocess import check_output


"""
Strategy:
*) Loop over the text twice

Iteration 1:
1a) Look for atoms and store them in variable list
1b) Look for clauses with no probability in the header (and does not belong to query)
    --> store clause in dictionary of the form dict<clause-header, [<clause-body1>, <clause-body2>, ...]>

Iteration 2:
1) Look for remainder elements of text (clauses with probability or header from query)
2a) Clause with probability:
    - create header variable and insert in list, if does not exist yet
    - add header with probability as new variable to clause body (with the given probability)
    - create the correct clauses in cnf
2b) Clause with query header:
    - variable for query and store clause -> verify body for atoms (if non-atom, use dictionary from stored clauses with no probability)

"""


class CNFConverter():

    def __init__(self):
        self.variables = dict({})
        self.variable_counter = 0
        self.clauses = []
        self.evidence = []
        self.query = None
        self.clauseDictionary = dict({})


    def getNewCounter(self):
        self.variable_counter += 1
        return self.variable_counter


    def ground(self, ProblogProgram):
        f = open('problog.pl', 'w')
        f.write(ProblogProgram)
        f.close()
        return check_output(["problog", "ground", "problog.pl"]).decode("utf-8")
        #return check_output(["problog", "ground", "problog.pl", "--compact"]).decode("utf-8")


    def convert_to_cnf(self, groundedProgr, query):
        self.storeQuery(query)

        # first iteration
        lines = groundedProgr.split('\n')
        remainder_lines = []
        for line in lines:
            pattern = re.compile(r'\s+')
            line = re.sub(pattern, '', line)
            if line == "" or line.startswith("query("):
                continue
            elif line.startswith("evidence("):
                self.storeEvidence(line)
                continue
            self.parseLineFirstIteration(line, remainder_lines)

        for var in self.variables.values():
            None#print(var.name +"    " + str(var.id))
        self.parseSecondIteration(remainder_lines)



    def parseLineFirstIteration(self, line, remainder_lines):
        parts = line.split(':-')
        if(len(parts) == 1):
            self.parseVariable(parts[0])
        else:
            notParsed = self.parseClauseFirstIteration(parts[0], parts[1])
            if notParsed is not None:
                remainder_lines.append(notParsed)


    def parseSecondIteration(self, remaining_lines):
        for line in remaining_lines:
            None #print(line)
        # sort clauses first
        temp_clause_dict = dict({})
        print(remaining_lines)
        remaining_lines.append(("path(1,5)",["path(3,5)","path(2,5)","path(2,5)"]))
        for (header,body) in remaining_lines:
            print("START iteration")
            #print(header + "   " + str(body))
            body = self.recursiveReplaceBody([body])[0]
            print(body)
            split_clauses_list = []
            self.splitClauses(body,split_clauses_list)

            #TODO loop over the header and find the subheaders to loop for rhos
            if "::" in header:
                (weight,name) = header.split('::')
                rho_name = header+"--"
                first = False
                for b in body:
                    if not first:
                        first = True
                    else:
                        rho_name += ","
                    rho_name += b
                rho = Variable(rho_name, self.getNewCounter(), weight)
                if name in temp_clause_dict:
                    temp_clause_dict[name].append((body,rho))
                else:
                    temp_clause_dict[name] = [(body,rho)]


    def recursiveReplaceBody(self,body):
        new_body = []
        for outer_body_part in body:
            new_inner_body = []
            for body_part in outer_body_part:
                if body_part in self.clauseDictionary:
                    new_inner_body.extend(self.recursiveReplaceBody(self.clauseDictionary[body_part]))
                else:
                    new_inner_body.append(body_part)
            new_body.append(new_inner_body)
        return new_body


    def splitClauses(self,body,clauses):
        for body_element in body:
            if type(body_element) == list:
                None
            else:
                None
    #expected output: [[edge(1,2),edge(2,5)],[edge(1,5)]]


    def splitClauseBodyElements(self,body):
        comma_indices = []
        parenthesis = False
        for i in range(len(body)):
            if not parenthesis and body[i] == ",":
                comma_indices.append(i)
            elif body[i] == "(":
                parenthesis = True
            elif body[i] == ")":
                parenthesis = False
        body_parts = []
        prev_ind = -1
        for ind in comma_indices:
            body_parts.append(body[prev_ind + 1:ind])
            prev_ind = ind
        body_parts.append(body[prev_ind + 1:])
        return body_parts


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
        v_true = Variable(parts[1],self.getNewCounter(),(1,1))     # true lambda variable
        v_false = Variable("not_" + parts[1], self.getNewCounter(),(1,1))  # false lambda variable
        rho = Variable("rho_" + parts[1], self.getNewCounter(), (parts[0], str(1-float(parts[0]))))  # rho variable
        self.variables[v_true.name] = v_true
        self.variables[v_false.name] = v_false
        self.variables[rho.name] = rho
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
            lambdas.append(Variable(split_vars[i][1],self.getNewCounter(),(1,1)))
            if(i != len(split_vars)-1):
                rhos.append(Variable("rho_"+split_vars[i][1],self.getNewCounter(),(split_vars[i][0], str(1-float(split_vars[i][0])))))
        for la in lambdas:
            self.variables[la.name] = la
        for rho in rhos:
            self.variables[rho.name] = rho

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


    def parseClauseFirstIteration(self,header,body):
        if("::" in header or header == self.query):
            sub_headers = header.split(";")
            for h in sub_headers:
                more_parts = h.split("::")
                if(len(more_parts) == 2):
                    name = more_parts[1]
                else:
                    name = h
                if(name in self.variables):
                    continue
                if name == self.query:
                    self.variables[name] = Variable(name, self.getNewCounter(), "1 0")
                    continue
                self.variables[name] = Variable(name, self.getNewCounter(), "1 1")
                self.variables["not_"+name] = Variable("not_"+name,self.getNewCounter(),"1 1")
            body = body[0:-1]
            body_parts = self.splitClauseBodyElements(body)
            return (header,body_parts)
        body = body[0:-1]
        body_parts = self.splitClauseBodyElements(body)
        if header in self.clauseDictionary:
            self.clauseDictionary[header].append(body_parts)
        else:
            self.clauseDictionary[header] = [body_parts]


    def storeEvidence(self, evidence):
        self.evidence.append(evidence[9:-2])


    def storeQuery(self, query):
        self.query = query[6:-2]


plp = ProbLogProgram()
cnfconverter = CNFConverter()
model = plp.task12()[0] + plp.task12()[2][0]
#model = plp.task11()[0] + plp.task11()[1] + plp.task11()[2][0]
grounded = cnfconverter.ground(model)
cnfconverter.convert_to_cnf(grounded, plp.task12()[2][0])

