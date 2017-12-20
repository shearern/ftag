from abc import ABCMeta, abstractmethod, abstractproperty

from .. import UsageError

class FtagCommandArgs(object):
    '''Collection of parsed arguments for a command'''
    def __init__(self, **defaults):
        self.__dict__.update(defaults)


class FtagCommandArg(object):
    '''A signel argument passed to the command'''
    def __init__(self, type, name=None, value=None, pos=None):
        self.name = name
        self.type = type
        self.value = value
        self.pos = pos
    def __str__(self):
        return self.name

class FtagCommand(object):
    '''Base for sub-commands for ftag.py'''
    __metaclass__ = ABCMeta


    @abstractproperty
    def name(self):
        '''Return the Default name for this command'''

    @property
    def aliases(self):
        '''List of additional command names that can be used to invoke this command'''
        return tuple()

    @abstractproperty
    def usage(self):
        '''Usage pattern for this sub command'''

    @abstractmethod
    def execute(self, argv):
        '''
        Run the given command

        :param args: sys.argv[2:] (skipping program name and command name)
        '''

    # -- Utilities --

    def _read_arguments(self, argv, opts_with_values=None):
        '''
        Pull arguments off commandline arg list one at a time

        :param argv: List of arguments to parse
        :return: One or more FtagCommandArg
        '''

        argv = argv[:]

        pos = 0

        while len(argv) > 0:

            opt = argv.pop(0)

            if opt.startswith('--'):

                arg = FtagCommandArg('flag', opt)

                # Get associated value
                if opts_with_values is not None and arg.name in opts_with_values:
                    try:
                        arg.value = argv.pop(0)
                    except IndexError:
                        raise UsageError(error = "Option %s requires a value" % (arg.name),
                                         cmd = self)

                yield arg

            elif opt.startswith('-'):
                # Handle multiple options (i.e.: -rf)
                for opt in opt[1:]:
                    arg = FtagCommandArg('flag', '-' + opt)

                    # Get associated value
                    if opts_with_values is not None and arg.name in opts_with_values:
                        try:
                            arg.value = argv.pop(0)
                        except IndexError:
                            raise UsageError(error = "Option %s requires a value" % (arg.name),
                                             cmd = self)

                    yield arg

            else:
                yield FtagCommandArg('posarg', pos=pos, value=opt)
                pos += 1


    def ask_yes_no(self, question, default=None):
        if default is None:
            ans = raw_input(question.strip() + " (y/n): ")
        elif default:
            ans = raw_input(question.strip() + " (Y/n): ")
        else:
            ans = raw_input(question.strip() + " (y/N): ")

        if len(ans.strip()) == 0:
            return default
        elif ans.strip().lower() in ('y', 'yes'):
            return True
        elif ans.strip().lower() in ('n', 'no'):
            return False
        else:
            print("Not a valid answer")
            return self.ask_yes_no(question, default)

