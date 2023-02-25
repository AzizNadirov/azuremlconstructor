from argparse import ArgumentParser, Namespace
import os
import pathlib
import re

from core.init.init import EnvBank


def parse_args():
    parser = ArgumentParser(description="Parse arguments for amlctor.", prog='amlctor')
    commands = parser.add_subparsers(title='main commands', dest='command')

    run_command = commands.add_parser('run',
                                      help='Run applied pipeline.')
    run_command.add_argument('-p', '--path', type=str, required=True,
                             help="path of pipeline. '.' for specify current directory")

    init_command = commands.add_parser('init',
                                       help='Initialise pipeline. ')
    init_command.add_argument('-n', '--name', type=str, required=True,
                              help="Name of pipeline. Also, will be used as project directory name")
    init_command.add_argument('-p', '--path', type=str, required=True,
                              help="Path where pipeline will be initialised. '.' for specify cwd.")
    init_command.add_argument('-e', '--env', type=str, required=False,
                              help="Env file name for this pipeline. You will have to enter password for decrypt the "
                                   "env")

    apply_command = commands.add_parser('apply',
                                        help='Apply configs from the settings file and build pipeline.')
    apply_command.add_argument('-p', '--path', type=str, required=True,
                               help="Path to the pipeline. '.' for choose cwd.")

    rename_command = commands.add_parser('rename',
                                         help='Rename step or pipeline.')
    rename_command.add_argument('-p', '--path', type=str, required=True,
                                help="Path to the pipeline.")
    rename_command.add_argument('-o', '--old_name', type=str, required=True,
                                help="Old pipeline step name.")
    rename_command.add_argument('-n', '--new_name', type=str, required=True,
                                help="New pipeline step name.")
    rename_command.add_argument('-x', '--pipe', required=False, action='store_true',
                                help="pass this flag if it's name of pipeline.")

    args = parser.parse_args()

    return args


class ArgsHandler:
    COMMANDS: tuple = ('init', 'apply', 'run', 'build')

    def __init__(self, args: Namespace):
        self.args = args

    @staticmethod
    def valid_pipe_name(name: str) -> str:
        MIN_LEN = 1
        MIN_LEN_RECOMMENDED = 3
        MAX_LEN = 64
        CONTENT_RE_PATTERN = r'^[a-zA-Z0-9_-]+$'
        KEYWORDS = (
            "default", "outputs", "inputs", "steps", "endpoint", "resourceGroup",
            "subscriptionId", "tenantId", "clientId", "clientSecret"
        )

        # len 
        name = name.strip()
        if MIN_LEN < len(name) < MAX_LEN:
            raise ValueError(
                f"Pipeline name length must be between {MIN_LEN}(Recommend minimal length: {MIN_LEN_RECOMMENDED}) and {MAX_LEN}")

        # content: letters, digits, - and _  allowed.
        if not re.match(CONTENT_RE_PATTERN, name):
            raise ValueError(f"Pipeline name can contain only: letters, digits, - and _")

        # reserved keywords: 
        if name in KEYWORDS:
            raise ValueError(f"Don't use reserved names as pipeline name. Reserved Names:\n\t{KEYWORDS}")

        return name

    @staticmethod
    def valid_path(path: str) -> str:
        if path.strip() == '.':
            return os.getcwd()

        path = pathlib.Path(path)
        if not path.exists():
            raise ValueError(f'specified path does not exist: \n{path}')
        return path

    @staticmethod
    def valid_select_env(name: str) -> EnvBank:
        from confs.configs import BANK_DIR

        if not name.isidentifier():
            raise ValueError(f"env name must be identifier.")
        path = f"{BANK_DIR}/{name}.e"
        path = pathlib.Path(path)
        if not path.exists():
            files = path.glob('*.e')
            files = [file.name for file in files if file.is_file()]
            raise ValueError(f"env with name {name} doesn't exist. Envs in storage:\n{files}")
        else:
            password_attempts = 3
            while True:
                password = input(f"Enter password for env {name}: ")
                eb = EnvBank.load(name)
                if isinstance(eb, EnvBank):
                    return eb

                elif eb == -1:
                    if password_attempts == 0:
                        print("Password attempts ended!")
                        raise SystemExit(1)
                    password_attempts -= 1
                    cmd = input(f"Incorrect password for: {name}. "
                                f"You have {password_attempts} attempts.\nContinue: y|n ?")
                    if cmd.lower() in ('y', 'yes'):
                        continue
                    else:
                        raise SystemExit(1)

    def valid_args(self):
        assert hasattr(self.args,
                       'command') and self.args.command in ArgsHandler.COMMANDS, f"Incorrect command: {self.args.command}"
        command = self.args.command
        if command == 'init':
            """ init -n  -p  -e """
            name = ArgsHandler.valid_pipe_name(self.args.name)
            path = ArgsHandler.valid_path(self.args.path)
            env = ArgsHandler.valid_select_env(self.args.env)

        elif command == 'apply':
            """ apply -n  -p  -e """
            path = ArgsHandler.valid_path(self.args.path)

        elif command == 'run':
            """ init -p """
            path = ArgsHandler.valid_path(self.args.path)

        elif command == 'rename':
            """ rename  -p -o -n -x"""
            path = ArgsHandler.valid_path(self.args.path)
            # TODO implement rename

        else:
            raise SystemExit(1)


if __name__ == '__main__':
    pass
