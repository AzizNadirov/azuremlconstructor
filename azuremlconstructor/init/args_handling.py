from argparse import ArgumentParser, Namespace, SUPPRESS
from pathlib import Path 
from typing import Union
import re

from azuremlconstructor.init.init import EnvBank


def parse_args():
    parser = ArgumentParser(description="Parse arguments for azuremlconstructor.", prog='azuremlconstructor')
    commands = parser.add_subparsers(title='main commands', dest='command')

    run_command = commands.add_parser('run',
                                      help='Run applied pipeline.')
    run_command.add_argument('path', type=str, nargs='?', default='.',
                             help="path of pipeline. '.' for specify current directory")


    init_command = commands.add_parser('init',
                                       help='Initialise pipeline. ')
    init_command.add_argument('-n', '--name', type=str, required=True,
                              help="Name of pipeline. Also, will be used as project directory name")
    
    init_command.add_argument('path', type=str,  default='.', nargs='?',
                              help="Path where pipeline will be initialised. '.' for specify cwd.")
    
    init_command.add_argument('-e', '--env', type=str, required=False,
                              help="Env file name for this pipeline. You will have to enter password for decrypt the "
                                   "env")


    apply_command = commands.add_parser('apply',
                                        help='Apply configs from the settings file and build pipeline.')
    
    apply_command.add_argument('path', type=str, default='.', nargs='?',
                                help="Path to the pipeline. '.' for choose cwd.")




    rename_command = commands.add_parser('rename',
                                         
                                         help='Rename pipeline.')
    rename_command.add_argument('path', type=str, default='.', nargs='?',
                                help="Path to the pipeline.")
    
    rename_command.add_argument('-n', '--new_name', type=str, required=True,
                                help="New pipeline step name.")

    

    update_command = commands.add_parser('update',
                                         help = "Update pipeline or step regarding to settings")
    
    update_command.add_argument('path', type=str, default='.', nargs='?',
                                    help="Path to the pipeline.")
    update_command.add_argument("--overwrite", help="overwrite all steps", required=False, action='store_true')
    


    denv_parser = commands.add_parser("denv", help="Manage your EnvBank")
    denv_subparsers = denv_parser.add_subparsers(title="denv subcommands")

    create_parser = denv_subparsers.add_parser("create", help="Create a denv")
    create_parser.add_argument("-p", "--path", help="Path to .env file", required=False)
    create_parser.add_argument("-n", "--name", help="Name your denv", required=False)
    create_parser.add_argument("--_subcommand", help=SUPPRESS, default='create', choices=['create', 'get', 'rm'])
    create_parser.add_argument("-i", "--interactive", help="create denv interactively", required=False, action='store_true')



    retrieve_parser = denv_subparsers.add_parser("get", help="Get the denv")
    retrieve_parser.add_argument("name", help="Name of the denv", nargs='?', default=None)
    retrieve_parser.add_argument("-a", "--all", help="get all denv names", required=False, action='store_true')
    retrieve_parser.add_argument("--_subcommand", help=SUPPRESS, default='get', choices=['create', 'get', 'rm'])

    delete_parser = denv_subparsers.add_parser("rm", help="Remove the denv")
    delete_parser.add_argument("-n", "--name", help="Name of the denv", required=True)
    delete_parser.add_argument("--_subcommand", help=SUPPRESS, default='rm', choices=['create', 'get', 'rm'])

    args = parser.parse_args()

    return args



class ArgsHandler:

    COMMANDS: tuple = ('init', 'apply', 'run', 'rename', 'denv', 'update')

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
        if not MIN_LEN < len(name) < MAX_LEN:
            raise ValueError(
                f"Pipeline name length must be between {MIN_LEN}(Recommend minimal length: {MIN_LEN_RECOMMENDED}) and {MAX_LEN}: {name}")

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
            return Path.cwd()

        path = Path(path).resolve()
        if not path.exists():
            raise ValueError(f'Provided path does not exist: \n{path}')
        return path


    @staticmethod
    def valid_select_env(name: str) -> EnvBank:
        from azuremlconstructor.confs.configs import BANK_DIR

        if name is None:    # env not passed
            return None
        
        if not name.isidentifier():
            raise ValueError(f"Denv name must be identifier.")
        
        path = BANK_DIR / f"{name}.e"

        if not path.exists():
            # passed env doesnt exist. Show existing ones
            files = path.glob('*.e')
            files = [file.name for file in files if file.is_file()]
            raise ValueError(f"Denv with name {name} doesn't exist. Envs in storage:\n\t{files}")
        else:
            password_attempts = 3
            while True:
                password = input(f"Enter password for env {name}: ")
                eb = EnvBank.load(name, password)
                if isinstance(eb, EnvBank):
                    return eb

                elif eb == -1:
                    if password_attempts == 0:
                        print("Password attempts ended!")
                        raise SystemExit(1)
                    password_attempts -= 1
                    cmd = input(f"Incorrect password for: {name}. "
                                f"You have {password_attempts} attempts.\nContinue: y|n: ")
                    if cmd.lower() in ('y', 'yes'):
                        continue
                    else:
                        raise SystemExit(1)



    def valid_args(self):
        """ validates args and returns correspondig handler instance """

        if self.args.command is None:
            raise SystemExit("Where is command?? Run with '-h' for more info.")
        assert hasattr(self.args,
                       'command') and self.args.command in ArgsHandler.COMMANDS, f"Incorrect command: {self.args.command}"
        
        command = self.args.command


        if command == 'init':
            """ init -n  -p  -e """
            from .init import InitHandler

            name: str =     ArgsHandler.valid_pipe_name(self.args.name)
            path: Path =    ArgsHandler.valid_path(self.args.path)
            env: EnvBank =  ArgsHandler.valid_select_env(self.args.env)
            
            handler = InitHandler(name=name, path=path, env=env)


        elif command == 'apply':
            """ apply -p """
            from azuremlconstructor.apply.apply import ApplyHandler

            path: Path =    ArgsHandler.valid_path(self.args.path)  # check only for existence
            handler = ApplyHandler(path=path)


        elif command == 'run':
            """ run -p """
            from azuremlconstructor.run.run import RunHandler

            path: Path =    ArgsHandler.valid_path(self.args.path)  # check only for existence
            handler =       RunHandler(path=path)


        elif command == 'rename':
            """ rename  -p -n """
            from azuremlconstructor.rename.rename import RenameHandler

            path: Path =    ArgsHandler.valid_path(self.args.path)
            new_name: str = self.args.new_name
            handler = RenameHandler(path=path, 
                                    new_name=new_name)
            
        elif command == 'update':
            """ update  -p -s """
            from azuremlconstructor.update.update import UpdateHandler

            path: Path = ArgsHandler.valid_path(self.args.path)
            overwrite = self.args.overwrite
            handler = UpdateHandler(path=path, overwrite=overwrite)


        elif command == 'denv':
            """ 
                denv create -p -n
                denv get -n -a
                denv rm -n
            """
            from azuremlconstructor.denv.denv import DenvHandler
            args = {}
            for k in vars(self.args):
                args[k] = getattr(self.args, k)
            handler = DenvHandler(args)


        else:
            raise SystemExit(1)
        
        return handler



    def launch(self):
        """ Launches arg validation and starts handler """
        handler = self.valid_args()
        handler.start()




if __name__ == '__main__':
    pass
