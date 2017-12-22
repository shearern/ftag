#!/usr/bin/python
import sys, os
from textwrap import dedent

from ftaglib import UsageError

from ftaglib.cmds import FtagCommand
from ftaglib.cmds import InitCmd
#from ftaglib.cmds import AddCmd


def abort(msg):
    print("ERROR: " + str(msg))
    sys.exit(2)


AVAIL_COMMANDS = [
    InitCmd(),
#    AddCmd(),
]

def select_command(argv):
    '''
    Choose the command to be executed

    :param argv: sys.argv[1:]
    :return: FtagCommand object
    '''

    try:
        cmd_name = argv[0]
    except IndexError:
        return None

    for cmd in AVAIL_COMMANDS:
        if cmd.name == cmd_name:
            return cmd
        if cmd_name in cmd.aliases:
            return cmd

    raise UsageError(error="Not a valid sub command: " + cmd_name)


class HelpCommand(FtagCommand):
    '''
    List additional help for a command
    '''

    name = 'help'
    aliases = ('--help', )

    @property
    def prog_name(self):
        return os.path.basename(sys.argv[0])

    @property
    def usage(self):
        return dedent("""\
            help (command)
            
            Where command is one of:
            """).strip().format(
                prog = self.prog_name,
            ) + "\n" + self.list_avail_commands()


    def execute(self, argv):

        # Determine command being requested
        if len(argv) >= 1:
            cmd_name = argv[0]
            cmd = select_command((cmd_name, ))
            print(dedent(cmd.__doc__).strip() + "\n")
            print("USAGE: %s "%(self.prog_name) + dedent(cmd.usage))

        # No command provided
        else:
            print("USAGE: %s command" % (self.prog_name))
            print("")
            print("Where command is one of:")
            print(self.list_avail_commands())

    def list_avail_commands(self):
        rtn = list()
        cmd_pat = "  %%-%ds %%s" % (max(len(c.name) for c in AVAIL_COMMANDS)+2)
        for cmd in AVAIL_COMMANDS:
            rtn.append(cmd_pat % (cmd.name + ':', cmd.__doc__.strip().split("\n")[0]))
        return "\n".join(rtn)


AVAIL_COMMANDS.append(HelpCommand())


if __name__ == '__main__':

    try:
        cmd = select_command(sys.argv[1:])

        # Print help if no commands provided
        if cmd is None:
            select_command(('help', )).execute(tuple())
            sys.exit(1)

        # Execute command
        cmd.execute(sys.argv[2:])

    # Usage error
    except UsageError, e:
        print("Usage Error: " + str(e))
        print("")
        select_command(('help', )).execute(('help', ))
        sys.exit(1)

    # args = parse_arguments()
    # cmd = args.cmdcls()
    #
    # try:
    #     cmd.go(args)
    # except FileTagException as e:
    #     print("ERROR: %s: %s" % (e.__class__.__name__, str(e)))

    #print_usage()



