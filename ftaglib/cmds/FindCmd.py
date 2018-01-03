import os

from .. import UsageError
from .FtagCommand import FtagCommand, FtagCommandArgs
from ..core.utils import expand_paths
from ..core import FtagExplorer
from .. import NoTagDatabaseForPath
from ..core import FtagFilterExpression

class FindCmd(FtagCommand):
    '''
    List files and tags
    '''

    name = 'find'

    usage = '''\
        tag find (options) paths
        
        --if filter
            Show only paths that match a the given filter
        
        --show
            Show the tags each path has
        
        paths 
            Are the files to add the tags to        
        '''


    def parse_args(self, argv):

        # Init
        args = FtagCommandArgs(
            paths = list(),
            tagfilter = None,
            show = False,
        )

        # Parse

        # Read remaining args
        for opt in self._read_arguments(argv[1:], ('--if')):
            if opt.type == 'posarg':
                args.paths.append(opt.value)
            elif opt.type == 'flag' and opt.name == '--show':
                args.show = True
            elif opt.type == 'flag' and opt.name == '--if':
                args.tagfilter = FtagFilterExpression(opt.value)
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
                    tagged = explorer.get(path)
                    if args.tagfilter is None or args.tagfilter.matches(tagged):
                        if args.show:
                            print("%s\t[%s]" % (path, ','.join(tagged.tags)))
                        else:
                            print(path)

        explorer.close_dbs()