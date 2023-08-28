from pathlib import Path
import keyring
import getpass

from dotenv import dotenv_values

from azuremlconstructor.init.init import EnvBank
from azuremlconstructor.confs.configs import BANK_DIR
from azuremlconstructor._utils import valid_path




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
        if not subcommand:                          # azuremlconstructor denv - without subcommand
            raise SystemExit("denv needs subcommand. Run with '-h' for more info")
        if subcommand == 'create':
            if self.args['interactive'] is False:
                if not (self.args['path'] is None) and not (self.args['name'] is None):
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
        """path - path to the .env file"""
        if path.suffix == ".env":
            denv = dotenv_values(path)
            denv = {k.upper(): v for k, v in denv.items()}
            denv['ENVIRONMENT_FILE'] = "settings/conda_dependencies.yml"
            eb = EnvBank(name=name, **denv)
            while True:
                pass1 = getpass.getpass("Type new password for denv encryption: ")
                pass2 = getpass.getpass("ReType it again: ")
                if pass1 == pass2:
                    print("Saving...")
                    eb.save(pass1)
                    print("Done")
                    break
                else:
                    print("Passwords are not same!")
        else:
            raise SystemExit("Incorrect path to *.env file.")



    def i_create(self):
        """ Interactive EnvBank creation """
        print("Interactive dotEnv creation selected. Fill default denv schema fields below.")
        name = input("\tName for denv(must be identifier): ")
        EnvBank.valid_name(name)
        subscription_id = input("\tSubscription ID: ")
        resource_group = input("\tResource Group: ")
        build_id = input("\tBuild ID: ")
        workspace_name = input("\tWorkspace Name: ")
        environment_name = input("\tEnvironment Name: ")
        tenant_id = input('\tTenant ID: ')
        # Create EnvBank instance
        eb = EnvBank(
                    name=name,
                    SUBSCRIPTION_ID=subscription_id,
                    RESOURCE_GROUP=resource_group,
                    BUILD_ID=build_id,
                    WORKSPACE_NAME=workspace_name,
                    ENVIRONMENT_NAME=environment_name,
                    TENANT_ID=tenant_id)
        while True:
            pass1 = getpass.getpass("Type new password for denv encryption: ")
            pass2 = getpass.getpass("ReType it again: ")
            if pass1 == pass2:
                eb.save(pass1)
                break
            else:
                print("Passwords are not the same!")



    def get(self, n: str, a: bool) -> None:
        """ prints denv/denvs """
        if a is True:
            # look for denv files files
            fs = [f for f in list(BANK_DIR.iterdir()) if f.name.endswith('.e')]
            if len(fs) == 0:    # if there is no any denv file
                print("No denvs yet.")
                return
            for file in fs:
                print("Denvs:")
                print('\t', file.name)
        else:
            if n is None:
                raise SystemExit(f"You have to provide denv name.")
            password = getpass.getpass(f"Password for denv '{n}': ")
            eb = EnvBank.load(name=n, password=password)
            if not isinstance(eb, EnvBank):
                raise SystemExit("Encryption has failed. File is corrupted or password is incorrect.")
            print(eb)

    def remove(self, n: str):
        path = (BANK_DIR / f'{n}.e')
        if path.exists():
            path.unlink()
        else:
            print(f"There is no denv named: '{n}'")

        

    def start(self):
        self.validate()

