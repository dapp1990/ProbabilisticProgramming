from pipeline.variable import Variable
from pipeline.probLogPrograms import ProbLogProgram
import re
import itertools
from subprocess import check_output


"""
Constraint 1: all clauses must be supplied (even the 0 probability ones)
    #   We were wasting too much time and getting complicated code from trying to take it into consideration, since
    #   we need to find all the combinations we have and find the clauses that are 'missing'.
    #   This can be done by storing the clauses for each header in a dictionary and to look for all permutations (and the missing ones)
Constraint 2: we assume in the case of multiple headers, that they are on the same line (and not spread over multiple lines)
    #   This saves us a lot of time wrt additional parsing.  If the rules are spread out anyway, we could join them together by
    #   looking for rules with the same clauses, effectively constructing the multi-header rule.
Constraint 3: We assume the evidence is always true.  If this is not the case, the evidence list must not just accept the names
        of the evidence, but a tuple of (<name>,<boolean).  The getOrderedWeights method must be adjusted accordingly.
"""


"""
Strategy:

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


    def ground(self, ProblogProgram,file=None):
        if file is None:
            f = open('problog.pl', 'w')
            f.write(ProblogProgram)
            f.close()
            return check_output(["problog", "ground", "problog.pl"]).decode("utf-8")
        else:
            return check_output(["problog", "ground", file]).decode("utf-8")
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

        """
        print(" ALL VARIABLES")
        for var in self.variables.values():
            print(var.name + "    " + str(var.id) + "     " + str(var.weight))
        print("amount of clauses: " + str(len(self.clauses)))
        print("ALL CLAUSES")
        for cl in self.clauses:
            print(cl)
        """

        if self.query is not None:
            if self.query in self.variables:
                self.variables[self.query].weight = (1,0)
                if "not_"+self.query in self.variables:
                    self.variables["not_"+self.query].weight = (0,1)
            else:
                self.variables[self.query] = Variable(self.query,self.getNewCounter(),(1,0))

        self.parseSecondIteration(remainder_lines)

        """
        print(" ALL VARIABLES")
        for var in self.variables.values():
            print(var.name + "    " + str(var.id) + "     " + str(var.weight))
        print("amount of clauses: " + str(len(self.clauses)))
        print("ALL CLAUSES")
        for cl in self.clauses:
            print(cl)
        """

        weights = self.getOrderedWeights()

        with open("created_cnf.cnf", "w") as myfile:
            w_string = "c weights "
            for weight in weights:
                w_string += weight + " "
            w_string += "\n"
            myfile.write(w_string);
            header_line = "p cnf " + str(len(self.variables)) + " " + str(len(self.clauses)) + "\n"
            myfile.write(header_line)
            for clause in self.clauses:
                myfile.write(clause + " 0\n")


    def getOrderedWeights(self):
        for ev in self.evidence:
            self.variables[ev].weight = (1,0)  # assuming evidence is always true
            ev_counterpart = "not_"+ev
            if ev_counterpart in self.variables:
                self.variables[ev_counterpart].weight(0,1)
        weights = [None] * len(self.variables)
        for var in self.variables.values():
            weights[var.id-1] = str(var.weight[0]) + " " + str(var.weight[1])

        return weights


    def parseLineFirstIteration(self, line, remainder_lines):
        parts = line.split(':-')
        if(len(parts) == 1):
            self.parseVariable(parts[0])
        else:
            notParsed = self.parseClauseFirstIteration(parts[0], parts[1])
            if notParsed is not None:
                remainder_lines.append(notParsed)


    def parseSecondIteration(self, remaining_lines):
        query_list = []
        for (header,body) in remaining_lines:
            all_clauses = self.recursiveReplaceBody2(body)
            # all_clauses now contains a list of clauses for the given header(s)

            if "::" in header:
                subheaders = header.split(";")
                rhos_list = []
                for i in range(len(subheaders)):
                    subheader = subheaders[i]
                    (weight,name) = subheader.split("::")
                    if len(subheaders) == 1:  # binary header
                        for clause in all_clauses:
                            rho_name = self.getRhoName(name, clause)
                            weight_tuple = (weight, str(round(1 - float(weight), 2)))
                            rho = Variable(rho_name, self.getNewCounter(), weight_tuple)
                            self.variables[rho_name] = rho
                            c = ""
                            for clause_el in clause:
                                if clause_el.startswith("\+"):
                                    clause_el = clause_el[2:]
                                    c += "-" + str(self.variables["not_" + clause_el].id) + " "
                                else:
                                    c += "-" + str(self.variables[clause_el].id) + " "
                            pos_c = c + "-" + str(rho.id) + " "
                            pos_c += str(self.variables[name].id) + " "
                            self.clauses.append(pos_c)
                            neg_c = c + str(rho.id) + " "
                            neg_c += str(self.variables["not_" + name].id) + " "
                            self.clauses.append(neg_c)
                    else:
                        for j in range(len(all_clauses)):
                            clause = all_clauses[j]
                            if i == len(subheaders)-1:
                                c = ""
                                for clause_el in clause:
                                    if clause_el.startswith("\+"):
                                        clause_el = clause_el[2:]
                                        c += "-" + str(self.variables["not_" + clause_el].id) + " "
                                    else:
                                        c += "-" + str(self.variables[clause_el].id) + " "
                                for k in range(j,len(rhos_list),len(all_clauses)):
                                    c += str(rhos_list[k].id) + " "
                                c += str(self.variables[name].id) + " "
                                self.clauses.append(c)
                            else:
                                rho_name = self.getRhoName(name, clause)
                                weight_tuple = (weight, str(round(1 - float(weight),2)))
                                rho = Variable(rho_name, self.getNewCounter(), weight_tuple)
                                self.variables[rho_name] = rho
                                c = ""
                                for clause_el in clause:
                                    if clause_el.startswith("\+"):
                                        clause_el = clause_el[2:]
                                        c += "-" + str(self.variables["not_" + clause_el].id) + " "
                                    else:
                                        c += "-" + str(self.variables[clause_el].id) + " "
                                for k in range(j,len(rhos_list),len(all_clauses)):
                                    c += str(rhos_list[k].id) + " "
                                c += "-" + str(rho.id) + " "
                                c += str(self.variables[name].id) + " "
                                self.clauses.append(c)
                                rhos_list.append(rho)
            else:  # this is a line with query header
                query_list.extend(all_clauses)

        clause_combos = itertools.product(*query_list)
        query_clauses = []
        for t in clause_combos:
            clause_set = set({})
            for el in t:
                clause_set.add(el)
            query_clauses.append(clause_set)

        # create and enter all query clauses
        for clause in query_list:
            cl = ""
            for el in clause:
                cl += "-" + str(self.variables[el].id) + " "
            cl += str(self.variables[self.query].id) + " "
            self.clauses.append(cl)

        for clause in query_clauses:
            if len(query_clauses) == 1 and len(clause) == 0:
                continue
            cl = ""
            for el in clause:
                cl += str(self.variables[el].id) + " "
            cl += "-" + str(self.variables[self.query].id) + " "
            self.clauses.append(cl)


    def getRhoName(self,name,clause):
        rho_name = "rho_" + name + "--"
        first = False
        for clause_el in clause:
            if not first:
                first = True
            else:
                rho_name += ","
            rho_name += clause_el
        return rho_name


    def recursiveReplaceBody2(self,body):
        new_body = [[]]
        for outer_body_part in body:
            if outer_body_part in self.clauseDictionary:
                body_part_clauses = self.clauseDictionary[outer_body_part]

                replace_new_body = []
                for clause in body_part_clauses:
                    results = self.recursiveReplaceBody2(clause)
                    for r in results:
                        for nb in new_body:
                            new_clause = []
                            new_clause.extend(nb)
                            new_clause.extend(r)
                            replace_new_body.append(new_clause)
                new_body = replace_new_body
            else:
                for nb in new_body:
                    nb.append(outer_body_part)
        return new_body


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
        rho = Variable("rho_" + parts[1], self.getNewCounter(), (parts[0], str(round(1-float(parts[0]),2))))  # rho variable
        self.variables[v_true.name] = v_true
        self.variables[v_false.name] = v_false
        self.variables[rho.name] = rho
        self.enterBinaryVariableLambdaClauses(v_true,v_false)
        self.clauses.append("-" + str(rho.id) + " " + str(v_true.id))  # not rho or true lambda
        self.clauses.append(str(rho.id) + " " + str(v_false.id))  # rho or false lambda


    def enterBinaryVariableLambdaClauses(self,v_true,v_false):
        self.clauses.append(str(v_true.id) + " " + str(v_false.id))  # true lambda or false lambda
        self.clauses.append("-" + str(v_true.id) + " -" + str(v_false.id))  # not true lambda or not false lambda


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
                rhos.append(Variable("rho_"+split_vars[i][1],self.getNewCounter(),(split_vars[i][0], str(round(1-float(split_vars[i][0]),2)))))
        for la in lambdas:
            self.variables[la.name] = la
        for rho in rhos:
            self.variables[rho.name] = rho

        self.enterNonBinaryVariableLambdaClauses(lambdas)

        for i in range(len(lambdas)):
            lambdastring = str(lambdas[i].id) + " "
            if(i != len(lambdas)-1):
                lambdastring += "-" + str(rhos[i].id) + " "
            for j in range(0,i):
                lambdastring += str(rhos[j].id) + " "
            if lambdastring == "":
                continue
            self.clauses.append(lambdastring)


    def enterNonBinaryVariableLambdaClauses(self,lambdas):
        lambdastring = ""
        for l in lambdas:
            lambdastring += str(l.id) + " "
        if lambdastring != "":
            self.clauses.append(lambdastring)

        for i in range(len(lambdas)):
            for j in range(i + 1, len(lambdas)):
                self.clauses.append("-" + str(lambdas[i].id) + " -" + str(lambdas[j].id))


    def parseClauseFirstIteration(self,header,body):
        if header == self.query:
            body = body[0:-1]
            body_parts = self.splitClauseBodyElements(body)
            return (header, body_parts)
        if("::" in header):
            sub_headers = header.split(";")
            header_var_list = []
            for h in sub_headers:
                more_parts = h.split("::")
                if(len(more_parts) == 2):
                    name = more_parts[1]
                else:
                    name = h
                if(name in self.variables):
                    continue
                #if name == self.query:
                #    self.variables[name] = Variable(name, self.getNewCounter(), (1,0))
                #    continue
                self.variables[name] = Variable(name, self.getNewCounter(), (1,1))
                if len(sub_headers) == 1:
                    self.variables["not_"+name] = Variable("not_"+name,self.getNewCounter(),(1,1))
                    self.enterBinaryVariableLambdaClauses(self.variables[name],self.variables["not_"+name])
                else:
                    header_var_list.append(self.variables[name])

            self.enterNonBinaryVariableLambdaClauses(header_var_list)

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
        pattern = re.compile(r'\s+')
        evidence = re.sub(pattern, '', evidence)
        self.evidence.append(evidence[9:-2])


    def storeQuery(self, query):
        if query is None:
            return
        pattern = re.compile(r'\s+')
        query = re.sub(pattern, '', query)
        self.query = query[6:-2]



def test():
    plp = ProbLogProgram()
    cnfconverter = CNFConverter()
    model = plp.task12()[0] + plp.task12()[2][0]
    #model = plp.task11()[0] + plp.task11()[1] + plp.task11()[2][0]
    grounded = cnfconverter.ground(model)
    cnfconverter.convert_to_cnf(grounded, plp.task12()[2][0])


#test()