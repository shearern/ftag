import sys, os
#import argparse
from textwrap import dedent

#from .InitCmd import InitCmd
from .AddCmd import AddCmd


AVAIL_COMMANDS = (
#    InitCmd(),
    AddCmd(),
)


def print_usage(argv=None):
    '''Print usage'''

    if argv is None:
        argv = sys.argv[1:]

    print(dedent("""\
        USAGE: {prog} (command)
        
        Where command is one of:
        """).strip().format(
            prog = os.path.basename(sys.argv[0]),
        ))
    for cmd in AVAIL_COMMANDS:
        print("  %-30s %s" % (cmd.name + ':', cmd.__doc__.split("\n")[0]))


def parse_arguments(argv=None):
    '''Parse commandline arguments'''

    if argv is None:
        argv = sys.argv[1:]

    # Build parser
    parser = argparse.ArgumentParser(description=dedent("""\
        Utility to tag files 
        """).strip())

    # Global arguments
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='List all files being operated on')

    # Command arguments
    subparsers = parser.add_subparsers()
    InitCmd.add_arguments(subparsers)
    AddCmd.add_arguments(subparsers)

    # Parse args
    args = parser.parse_args(argv)

    # Returned parsed arguments
    return args