#!/usr/bin/python

# from ftaglib.args import parse_arguments
# from ftaglib import FileTagException

from ftaglib.cmds import print_usage

if __name__ == '__main__':

    # args = parse_arguments()
    # cmd = args.cmdcls()
    #
    # try:
    #     cmd.go(args)
    # except FileTagException as e:
    #     print("ERROR: %s: %s" % (e.__class__.__name__, str(e)))

    print_usage()
