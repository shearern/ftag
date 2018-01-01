import os

from .. import UsageError
from .FtagCommand import FtagCommand, FtagCommandArgs
from ..core.utils import expand_paths, validate_tag_name
from ..core import FtagExplorer
from .. import NoTagDatabaseForPath


class TagCmd(FtagCommand):
    '''
    Add or remove tag to a file or set of files
    '''

    name = 'tag'

    usage = '''\
        tag tag_spec (options) paths
        
        tag_spec
            Specifies which tag operations to perform.
            
            Adding tags can be done using +
                +newtag
                
            Removing tags can be done using -
                -oldtag
                
            Multiple operations can be sperated with commands
                +newtag,-oldtag
        
        paths 
            Are the files to add the tags to
            
        options:

            -r, --recurse
                Recurse over all files and directories under the paths specified
                
            -v
                List paths being acted on
            
        '''

    def parse_args(self, argv):


        # Init
        args = FtagCommandArgs(
            recurse = False,
            verbose = False,
            tag_spec = None,
            paths = list(),
        )

        # Parse

        # Read tag spec first since looks like a flag
        try:
            args.tag_spec = argv[0]
        except IndexError:
            raise UsageError(cmd=self, error="Must specify tag_spec (tagging operations)")

        # Read remaining args
        for opt in self._read_arguments(argv[1:]):
            if opt.type == 'flag' and opt.name in ('--recurse', '-r'):
                args.recurse = True
            elif opt.type == 'flag' and opt.name in ('--verbose', '-v'):
                args.verbose = True
            elif opt.type == 'posarg':
                args.paths.append(opt.value)
            else:
                raise UsageError(cmd=self, error="Unknown argument: " + str(opt))

        # Validate
        if len(args.paths) == 0:
            raise UsageError(cmd=self, error="paths are required")

        # Interpret tag operations
        args.tag_operations = {
            '+': list(),
            '-': list(),
        }
        for operation in [s.strip() for s in args.tag_spec.split(",")]:
            if operation.startswith('+'):
                args.tag_operations['+'].append(operation[1:])
            elif operation.startswith('-'):
                args.tag_operations['-'].append(operation[1:])
            else:
                raise UsageError(cmd=self, error="Tag specification must start with + or -: " + operation)

        # Validate tag names
        for tag in args.tag_operations['+']:
            validate_tag_name(tag)
        for tag in args.tag_operations['-']:
            validate_tag_name(tag)

        return args


    def execute(self, argv):

        args = self.parse_args(argv)
        explorer = FtagExplorer()

        # Walk over all supplied paths
        for path in expand_paths(args.paths, recurse=args.recurse):

            if not os.path.exists(path):
                raise UsageError(cmd=self, error="Path doesn't exist: " + path)

            path = explorer.get(path)

            if not path.taggable:
                raise NoTagDatabaseForPath("No tag database found for %s.  Need to run ftag init?" % (path))

            for tag in args.tag_operations['+']:
                path.tags.add(tag)
            for tag in args.tag_operations['-']:
                path.tags.remove(tag)

            if args.verbose:
                print("%s\t%s" % (path.s, ', '.join(path.tags)))

        explorer.close_dbs()