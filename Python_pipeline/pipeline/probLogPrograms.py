
class ProbLogProgram:

    def task11(self):
        model = """
                    person(john).
                    person(mary).

                    0.7::burglary.
                    0.01::earthquake(heavy); 0.19::earthquake(mild); 0.8::earthquake(none).

                    0.90::alarm :-   burglary, earthquake(heavy).
                    0.85::alarm :-   burglary, earthquake(mild).
                    0.80::alarm :-   burglary, earthquake(none).
                    0.10::alarm :- \+burglary, earthquake(mild).
                    0.30::alarm :- \+burglary, earthquake(heavy).

                    0.8::calls(X) :- alarm, person(X).
                    0.1::calls(X) :- \+alarm, person(X).
                """
        evidence = """
                        evidence(calls(john),true).
                        evidence(calls(mary),true).
                   """
        queries = """
                        query(burglary).
                        query(earthquake(_)).
                  """
        return (model, evidence, queries)


    def task12(self):
        model = """
                    0.6::edge(1,2).
                    0.1::edge(1,3).
                    0.4::edge(2,5).
                    0.3::edge(2,6).
                    0.3::edge(3,4).
                    0.8::edge(4,5).
                    0.2::edge(5,6).

                    path(X,Y) :- edge(X,Y).
                    path(X,Y) :- edge(X,Z),
                                 Y \== Z,
                             path(Z,Y).
                """

        evidence = None
        queries = """
                        query(path(1,5)).
                        query(path(1,6)).
                  """
        return (model, evidence, queries)


    def task23(self):
        model = """
                    0.05::weight(C,0.1); 0.2::weight(C,0.3); 0.5::weight(C,0.5); 0.2::weight(C,0.7); 0.05::weight(C,0.9) :- coin(C).

                    Param::toss(_,Param,_).
                    heads(C,R) :- weight(C,Param),toss(C,Param,R).
                    tails(C,R) :- weight(C,Param),\+toss(C,Param,R).

                    data(C,[]).
                    data(C,[h|R]) :- heads(C,R), data(C,R).
                    data(C,[t|R]) :- tails(C,R), data(C,R).

                    coin(c1).
                    coin(c2).
                    param(0.1).
                    param(0.3).
                    param(0.5).
                    param(0.7).
                    param(0.9).
                """

        evidence = """
                        evidence(data(c1,[h,h,h,h,h,h,h,h,h,h,h,h,h]),true).
                        evidence(data(c2,[h,t,h,h,h,h,h,t,t,h,t,t,h]),true).
                   """
        queries = """
                        query(weight(C,X)) :- coin(C),param(X).
                  """
        return (model, evidence, queries)
