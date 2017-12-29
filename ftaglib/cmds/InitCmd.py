import os

from .. import UsageError
from ..core import FileTagDatabase
from .FtagCommand import FtagCommand, FtagCommandArgs

class InitCmd(FtagCommand):
    '''
    Command to create .file-tags file
    '''

    name = 'init'

    usage = '''\
        init (path)
        
        path:
            Path to directory to store file tags DB (optional)
            If not specified, then defaults to current directory
        '''

    def parse_args(self, argv):

        # Init
        args = FtagCommandArgs()
        args.path = os.path.abspath(os.curdir)

        # Parse
        for arg in self._read_arguments(argv):
            if arg.type == 'posarg' and arg.pos == 0:
                args.path = arg.value
            else:
                raise UsageError(cmd=self, error="Unknown argument: " + str(opt))

        return args

    def execute(self, argv):

        args = self.parse_args(argv)

        path = os.path.join(args.path, FileTagDatabase.FILENAME)
        print("Initalizing " + os.path.abspath(path))

        if os.path.exists(path):
            if not self.ask_yes_no("Overwrite existing file?"):
                print("aborting")
                return

        FileTagDatabase.initialize_new_db(path)
