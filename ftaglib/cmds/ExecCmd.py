import os, sys
import subprocess

from .. import UsageError
from .FtagCommand import FtagCommand, FtagCommandArgs
from ..core.utils import expand_paths, ask_yes_no
from ..core import FtagExplorer
from .. import NoTagDatabaseForPath
from ..core import FtagFilterExpression
from .. import ShellCommandFailed

class ExecCmd(FtagCommand):
    '''
    List files and tags
    '''

    name = 'exec'

    usage = '''\
        tag exec (options) -c "command {}" paths

        -c, --command "command spec"
            Execute the given command on every file that matches the filter (if specified)
            
            Command spec is the command to run on each file.  Use {} for the placeholder
            each path.  The absolute path to the file will be passed, and no quotes will
            be included by default.
            
            example:
                rm -v '{}'
                
        -f, --if filter
            Run the command only paths that match a the given filter.
            This is not required, but almost always desired.
            
        --halt
            Halt the process if a command fails (return code not zero)
            
        --ignore
            Ignore any commands that fail and keep running.
            The default is to prompt to continune on error
        
        -n, --dry-run
            Don't actually execute the command.  Run with --show to see what would be
            executed
            
        --nooutput
            Don't show stdout and stderr output from executed commands 
        
        --show
            Show the commands as they are being run
                
        paths 
            Are the files to add the tags to.  If directories are supplied, recurse
            is assumed.      
        '''


    def parse_args(self, argv):

        # Init
        args = FtagCommandArgs(
            paths = list(),
            tagfilter = None,
            show = False,
            command = None,
            halt_on_error = False,
            ignore_errors = False,
            dry_run = False,
            show_stdout = True,
        )

        # Parse

        # Read remaining args
        for opt in self._read_arguments(argv[1:], ('-c', '--command', '-f', '--if')):
            if opt.type == 'posarg':
                args.paths.append(opt.value)

            elif opt.type == 'flag' and opt.name == '--halt':
                args.halt_on_error = True
            elif opt.type == 'flag' and opt.name == '--ignore':
                args.ignore_errors = True
            elif opt.type == 'flag' and opt.name == '--show':
                args.show = True
            elif opt.type == 'flag' and opt.name == '--nooutput':
                args.show_stdout = False

            elif opt.type == 'flag' and opt.name in ('-c', '--command'):
                args.command = opt.value
            elif opt.type == 'flag' and opt.name in ('-f', '--if'):
                args.tagfilter = FtagFilterExpression(opt.value)
            else:
                raise UsageError(cmd=self, error="Unknown argument: " + str(opt))

        # Validate
        if len(args.paths) == 0:
            raise UsageError(cmd=self, error="paths are required")
        if args.command is None:
            raise UsageError(cmd=self, error="command is required")
        if '{}' not in args.command:
            raise UsageError(cmd=self, error="command should have {}")
        if args.halt_on_error and args.ignore_errors:
            raise UsageError(cmd=self, error="Can't specify --halt and --ignore together")

        return args


    def execute(self, argv):

        args = self.parse_args(argv)
        explorer = FtagExplorer()

        self._return_code = 0

        try:
            # Walk over all supplied paths
            for arg_path in expand_paths(args.paths, recurse=False):
                for dirpath, dirnames, filenames in os.walk(arg_path):
                    for filename in filenames:
                        path = os.path.normpath(os.path.join(dirpath, filename))
                        tagged = explorer.get(path)
                        if args.tagfilter is None or args.tagfilter.matches(tagged):
                            self._run_command_on(path, args)

        finally:
            explorer.close_dbs()


    def _run_command_on(self, path, args):

        # Format command
        command = args.command.replace('{}', path.abs)

        # Show user what we're going to do
        if args.show:
            print(command)

        # execute command
        if not args.dry_run:

            if args.show_stdout:
                stdout = sys.stdout
            else:
                stdout = None

            if args.show_stdout:
                stderr = sys.stderr
            else:
                stderr = None

            try:
                subprocess.check_call(args.command, shell=True, stdout=stdout, stderr=stderr)
            except Exception, e:
                if args.ignore_errors:
                    print("Command failed: %s: %s" % (command, str(e)))
                elif args.halt_on_error:
                    raise ShellCommandFailed("Command failed: %s: %s" % (command, str(e)))
                else:
                    print("Command failed: %s: %s" % (command, str(e)))
                    if not ask_yes_no("Continue executing?"):
                        raise ShellCommandFailed("Command failed: %s: %s" % (command, str(e)))




