import os

from .. import UsageError
from .FtagCommand import FtagCommand, FtagCommandArgs
from ..core.utils import expand_paths
from ..core import FtagExplorer
from .. import NoTagDatabaseForPath

class FindCmd(FtagCommand):
    '''
    List files and tags
    '''

    name = 'find'

    usage = '''\
        tag find (options) paths
        
        paths 
            Are the files to add the tags to        
        '''


    def parse_args(self, argv):

        # Init
        args = FtagCommandArgs(
            paths = list(),
        )

        # Parse

        # Read remaining args
        for opt in self._read_arguments(argv[1:]):
            if opt.type == 'posarg':
                args.paths.append(opt.value)
            else:
                raise UsageError(cmd=self, error="Unknown argument: " + str(opt))

        # Validate
        if len(args.paths) == 0:
            raise UsageError(cmd=self, error="paths are required")

        return args


    def execute(self, argv):

        args = self.parse_args(argv)
        explorer = FtagExplorer()

        # Walk over all supplied paths
        for arg_path in expand_paths(args.paths, recurse=False):
            for dirpath, dirnames, filenames in os.walk(arg_path):
                for filename in filenames:
                    path = os.path.normpath(os.path.join(dirpath, filename))
                    print("%s\t[%s]" % (path, ','.join(explorer.get(path).tags)))

        explorer.close_dbs()