0.8::calls(mary) :- alarm.
0.1::alarm :- \+burglary, earthquake(mild).
0.9::alarm :- burglary, earthquake(heavy).
0.3::alarm :- \+burglary, earthquake(heavy).
0.8::calls(john) :- alarm.
0.01::earthquake(heavy); 0.19::earthquake(mild); 0.8::earthquake(none).
0.1::calls(john) :- \+alarm.
0.85::alarm :- burglary, earthquake(mild).
0.8::alarm :- burglary, earthquake(none).
0.1::calls(mary) :- \+alarm.
0.7::burglary.
evidence(calls(john)).
evidence(calls(mary)).
