from pathlib import Path

from dotenv import dotenv_values

from amlctor.init.init import EnvBank
from amlctor.confs.configs import BANK_DIR
from amlctor.utils import valid_path




class DenvHandler:
    def __init__(self, args: dict) -> None:
        """ 
            Handles .env 
            cmd: command - [create, get, rm]
            p: path - valid for 'create' command
            n: name of denv valid for all 3 commands
            a: print all denv names, valid for 'get' command
        """
        self.args = args


    def validate(self):
        """ validate and run method """
        subcommand = self.args.get('_subcommand')
        if not subcommand:                          # amlctor denv - without subcommand
            raise SystemExit("denv needs subcommand. Run with '-h' for more info")
        if subcommand == 'create':
            if self.args['interactive'] is False:
                if self.args['path'] is not None and self.args['name'] is not None:
                    path = valid_path(self.args['path'])
                    self.create(path=path, name=self.args['name'])
                else:
                    print("You have to provide path(-p) and name(-n) arguments or create in intaractive mode with '-i' flag")
                    raise SystemExit('exit...')
            else:
                self.i_create()
        
        elif subcommand == 'get':
            self.get(n=self.args['name'], a=self.args['all'])

        elif subcommand == 'rm':
            self.remove(n=self.args['name'])

        else:
            raise ValueError(f"Incorrect subcommand for denv: '{subcommand}'")
        


    def create(self, path: Path, name: str):
        """path - path of folder wich contains .env or .env file path itself """
        if path.name == '.env' or (path / '.env').exists():
            if path.name == '.env': p = path
            else: p = path / '.env'
            denv = dotenv_values(p)
            denv = {k.upper(): v for k, v in denv.items()}
            denv['ENVIRONMENT_FILE'] = None
            eb = EnvBank(name=name, **denv)
            while True:
                pass1 = input("Type new password for denv encryption: ")
                pass2 = input("ReType it again: ")
                if pass1 == pass2:
                    print(eb)
                    eb.save(pass1)
                    break
                else:
                    print("Passwords are not same!")



    def i_create(self):
        """ Interactive EnvBank creation """
        print("Interactive dotEnv creation selected.")
        print("Fill default denv schema fields below.")
        name = input("Name for denv(must be identifier): ")
        EnvBank.valid_name(name)
        subscription_id = input("Subscription ID: ")
        resource_group = input("Resource Group: ")
        build_id = input("Build ID: ")
        workspace_name = input("Workspace Name: ")
        environment_name = input("Environment Name: ")
        tenant_id = input('Tenant ID: ')
        # Create EnvBank instance
        eb = EnvBank(
        name=name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        build_id=build_id,
        workspace_name=workspace_name,
        environment_name=environment_name,
        tenant_id=tenant_id)
        while True:
            pass1 = input("Type new password for denv encryption: ")
            pass2 = input("ReType it again: ")
            if pass1 == pass2:
                eb.save(pass1)
                break
            else:
                print("Passwords are not same!")



    def get(self, n: str, a: bool) -> None:
        """ prints denv/denvs """
        if a is True:
            for file in BANK_DIR.iterdir():
                if file.name.endswith('.e'):
                    print(file.name)
        else:
            password = input(f"Password for denv '{n}': ")
            eb = EnvBank.load(name=n, password=password)
            if not isinstance(eb, EnvBank):
                raise SystemExit("Incorrect denv...")
            

    def remove(self, n: str):
        path = (BANK_DIR / f'{n}.e')
        if path.exists():
            path.unlink()
        else:
            print(f"There is no denv named: '{n}'")

        

    def start(self):
        self.validate()

