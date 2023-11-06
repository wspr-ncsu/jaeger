import privytrace.analyzer as analyzer

ideal =                 ['None|1|2',    '1|2|3',    '2|3|4',    '3|4|5',    '4|5|None']
missing_origin =        [ None,         '1|2|3',    '2|3|4',    '3|4|5',    '4|5|None']
missing_termination =   ['None|1|2',    '1|2|3',    '2|3|4',    '3|4|5',     None     ]
alternate_misses_1 =    ['None|1|2',    None,       '2|3|4',    None,       '4|5|None']
alternate_misses_2 =    [ None,         '1|2|3',     None,      '3|4|5',    '4|5|None']
alternate_misses_3 =    [ None,         '1|2|3',     None,      '3|4|5',    None]
consecutive_misses =    ['None|1|2',    None,       None,       '3|4|5',    '4|5|None'] 

analyzer.init(consecutive_misses)
analyzer.analyze()
# subgraphs = analyzer.get_subgraphs()
# print(subgraphs)