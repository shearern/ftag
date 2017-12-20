import os

from .FtagCommand import FtagCommand

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

    @staticmethod
    def add_arguments(subparsers):

        cmd = subparsers.add_parser('add', help=AddCmd.__doc__.strip())

        cmd.set_defaults(
            command = 'add',
            cmdcls = AddCmd,
        )

        cmd.add_argument(
            '--root',
            help = "Root folder for tags (containts .file-tags.json)"
            )
        cmd.add_argument('tag', help="Tag to add")
        cmd.add_argument('paths', help="Files to add tag to", nargs='*')


    def go(self, args):
        paths = expand_paths(args.paths)
        root = find_add_root(args, paths)

        for path in expand_paths(paths):
            file = TaggedFilePath(root, path)
            file.add_tag(args.tag)
            if args.verbose:
                print(path)

        root.index.save()
