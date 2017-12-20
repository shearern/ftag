import os

from .. import UsageError
from .FtagCommand import FtagCommand, FtagCommandArgs

from ..core import FileTagRoot, TaggedFilePath
from ..core.common import find_root, expand_paths
from ..core.exceptions import NoFileTagRoot

def find_add_root(args, paths=None):
    '''Find root folder to work from'''
    if args.root is not None:
        return FileTagRoot(args.root)

    # Walk up parents to find path
    root = find_root('.')
    if root is not None:
        return FileTagRoot(root)


class AddCmd(FtagCommand):
    '''
    Add a tag to a file or set of files
    '''

    name = 'add'

    usage = '''\
        add (--root dir) --tag name paths
        
        Where:
            --tag name
                Tag to add
                
            --root dir
                Root folder for tags (containts .file-tags.json)

            paths 
                Are the files to add the tags to 
        '''

    def parse_args(self, argv):

        args = FtagCommandArgs(
            tag = None,
            root = None,
            paths = list(),
            verbose = False,
        )

        for opt in self._read_arguments(argv, ('--tag', '--root')):
            if opt.type == 'flag' and opt.name in ('--tag'):
                args.tag = opt.value
            elif opt.type == 'flag' and opt.name in ('--root'):
                args.root = opt.value
            elif opt.type == 'posarg':
                args.paths.append(opt.value)
            else:
                raise UsageError(cmd=self, error="Unknown argument: " + str(opt))

        if args.tag is None:
            raise UsageError(cmd=self, error="--tag is required")

        return args


    def execute(self, argv):

        args = self.parse_args(argv)

        paths = list(expand_paths(args.paths))
        root = find_add_root(args, paths)

        for path in expand_paths(paths):
            file = TaggedFilePath(root, path)
            file.add_tag(args.tag)
            if args.verbose:
                print(path)

        root.index.save()
