import argparse
import privytrace.analyzer as analyzer
from privytrace.helpers import startStopwatch, endStopwatch

ideal =                 ['None|1|2',    '1|2|3',    '2|3|4',    '3|4|5',    '4|5|None']
missing_origin =        [ None,         '1|2|3',    '2|3|4',    '3|4|5',    '4|5|None']
missing_termination =   ['None|1|2',    '1|2|3',    '2|3|4',    '3|4|5',     None     ]
alternate_misses_0 =    [ None,         '1|2|3',     None,      '3|4|5',    '4|5|None']
alternate_misses_1 =    ['None|1|2',    None,       '2|3|4',    None,       '4|5|None']
alternate_misses_t =    [ None,         '1|2|3',     None,      '3|4|5',    None]
consecutive_misses =    ['None|1|2',    None,       None,       '3|4|5',    '4|5|None'] 

def analyze(recs, dev = True):
    analyzer.init(recs, dev)
    analyzer.analyze()
    
def analyze_case(case):
    if case == 'ic':
        analyze(ideal)
    elif case == 'mo':
        analyze(missing_origin)
    elif case == 'mt':
        analyze(missing_termination)
    elif case == 'am0':
        analyze(alternate_misses_0)
    elif case == 'am1':
        analyze(alternate_misses_1)
    elif case == 'amt':
        analyze(alternate_misses_t)
    elif case == 'cm':
        analyze(consecutive_misses)
    else:
        print("Invalid case")
    
def init(args):
    analyze_case(args.case)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run analysis on cached records')
    parser.add_argument('-c', '--case',  type=str, help='Analyze given case case', required=False)
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
    else:
        init(args)