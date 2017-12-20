import os

class InitCmd(object):
    '''
    Command to create .file-tags file
    '''

    @staticmethod
    def add_arguments(subparsers):

        cmd = subparsers.add_parser('init', help=InitCmd.__doc__.strip())

        cmd.set_defaults(
            command = 'init',
            cmdcls = InitCmd,
        )

        cmd.add_argument(
            'path',
            help="Path to root directory to store file tags in",
            nargs='?',
            default='./')


    def go(self, args):
        path = os.path.join(args.path, '.file-tags.json')
        print("Initalizing " + os.path.abspath(path))
        with open(path, 'w') as fh:
            fh.write('{}')