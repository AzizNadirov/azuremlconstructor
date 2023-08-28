import base64
import os
import json
from pathlib import Path
from typing import Optional
import getpass

import pydantic
from pydantic import BaseModel

from azuremlconstructor.confs.configs import BANK_DIR

from .init_structure import StructureInit


class EnvBank:

    class EnvSchema(BaseModel):
            name: str
            SUBSCRIPTION_ID: str
            RESOURCE_GROUP: str
            BUILD_ID: str
            WORKSPACE_NAME: str
            ENVIRONMENT_NAME: str
            TENANT_ID: str
            ENVIRONMENT_FILE: str = "settings/conda_dependencies.yml"


    def __init__(self, name: str, SUBSCRIPTION_ID: str, RESOURCE_GROUP: str, BUILD_ID: str,
                 WORKSPACE_NAME: str, ENVIRONMENT_NAME: str, TENANT_ID: str, ENVIRONMENT_FILE: str="settings/conda_dependencies.yml"):

        EnvBank.valid_name(name.strip())

        self.name = name.strip()
        self.SUBSCRIPTION_ID = SUBSCRIPTION_ID
        self.RESOURCE_GROUP = RESOURCE_GROUP
        self.BUILD_ID = BUILD_ID
        self.WORKSPACE_NAME = WORKSPACE_NAME
        self.ENVIRONMENT_NAME = ENVIRONMENT_NAME
        self.TENANT_ID = TENANT_ID
        self.ENVIRONMENT_FILE = ENVIRONMENT_FILE



    @staticmethod
    def valid_name(name: str):
        if not name.isidentifier():
            raise ValueError("Env name must be identifier - as variable name.")

        return True


    def encoder(self, password):
        d = {
            "name": self.name, 'SUBSCRIPTION_ID': self.SUBSCRIPTION_ID,
            "RESOURCE_GROUP": self.RESOURCE_GROUP, 'BUILD_ID': self.BUILD_ID,
            "WORKSPACE_NAME": self.WORKSPACE_NAME, 'ENVIRONMENT_NAME': self.ENVIRONMENT_NAME,
            "TENANT_ID": self.TENANT_ID, 'ENVIRONMENT_FILE': self.ENVIRONMENT_FILE}
        
        d = json.dumps(d)
        message = f"{d}"
        message_bytes = message.encode('utf-8')
        password_bytes = password.encode('utf-8')
        encoded_bytes = base64.b64encode(message_bytes + password_bytes)
        encoded_message = encoded_bytes.decode('utf-8')
        return encoded_message


    @staticmethod
    def try_parse_env(json_str):
        """
            Try to parse passed env. If password had been entered correctly, parsing will return
            dictionary with env data, otherwise - data is corrupted and pydantic will not be able to
            parse that, and will raise exception, in that case, return -1

        :param json_str:    decrypted json string for parsing.
        :return:            dict in successfully case, otherwise -1
        """


        class EnvSchema(BaseModel):
            name: Optional[str]
            SUBSCRIPTION_ID: str
            RESOURCE_GROUP: str
            BUILD_ID: str
            WORKSPACE_NAME: str
            ENVIRONMENT_NAME: str
            TENANT_ID: str
            ENVIRONMENT_FILE: str = "settings/conda_dependencies.yml"


        try:
            parsed_dict = EnvSchema.parse_raw(json_str).dict()  
            return EnvBank(**parsed_dict)
        
        # except pydantic.error_wrappers.ValidationError as e:
        except Exception as e:
            print(e)
            return -1


    @staticmethod
    def decoder(encoded_message, password):
        encoded_bytes = encoded_message.encode('utf-8')
        decoded_bytes = base64.b64decode(encoded_bytes)
        message_bytes = decoded_bytes[:-len(password)]
        message = message_bytes.decode('utf-8')
        return message
    

    def get_service_name_for(self, name: str=None)->str:
        if name:    return f"azuremlconstructordenv__{name}"
        else:       return f"azuremlconstructordenv__{self.name}"


    def save(self, password: str):
        service_name = self.get_service_name_for()
        # encode env
        encoded_env = self.encoder(password)
        # savng 
        file = f"{BANK_DIR}/{self.name}.e"
        if os.path.exists(file):
            while True:
                r = input(
                    f"File '{self.name}.e' already exists. Dou you want to overwrite it? Old file will be lost? y/n: "
                    )
                if r.lower() in ('y', 'yes'):
                    with open(file, 'w') as f:
                        f.write(encoded_env)
                        print(f"Env saved as '{file}'")
                        return None
                elif r.lower() in ('n', 'no'):
                    print("Saving canceled.")
                    return None
                else:
                    print(f"Incorrect command: {r}. Enter [Y/N]: ")
        else:
            with open(file, 'w+') as f:
                f.write(encoded_env)
                print(f"Denv saved as '{file}'")


    @staticmethod
    def load(name: str, password: str):
        file = f"{BANK_DIR}/{name}.e"
        if os.path.exists(file):
            with open(file, 'r') as f:
                encoded_env = f.read()
            decoded_env = EnvBank.decoder(encoded_env, password)
            eb = EnvBank.try_parse_env(decoded_env)
            return eb
        else:
            raise SystemExit(f"There is no Env with such name: {file}")
        

    def as_dict(self):
        d = {'name':                self.name,
            'SUBSCRIPTION_ID':      self.SUBSCRIPTION_ID,
            'RESOURCE_GROUP':       self.RESOURCE_GROUP,
            'BUILD_ID':             self.BUILD_ID,
            'WORKSPACE_NAME':       self.WORKSPACE_NAME,
            'ENVIRONMENT_NAME':     self.ENVIRONMENT_NAME,
            'TENANT_ID':            self.TENANT_ID,
            'ENVIRONMENT_FILE':     self.ENVIRONMENT_FILE}
        
        return d
        
    

    def set_environment_file(self, pipe_path: Path):
        """ by default dev 'environment_file' = None. The method sets it for pipeline name """
        self.ENVIRONMENT_FILE = "settings/conda_dependencies.yml"


    def __str__(self):
        return f""" \t{self.name}\n
                subscription_id:        {self.SUBSCRIPTION_ID}
                resource_group:         {self.RESOURCE_GROUP}
                build_id:               {self.BUILD_ID}
                workspace_name:         {self.WORKSPACE_NAME}
                environment_name:       {self.ENVIRONMENT_NAME}
                tenant_id:              {self.TENANT_ID} 
                environment_file:      {self.ENVIRONMENT_FILE}
                """
    

    def __repr__(self) -> str:
        return f"""EnvBamk<{self.name}>: subscription_id: {self.RESOURCE_GROUP}; resource_group: {self.BUILD_ID}; 
                build_id: {self.WORKSPACE_NAME}; workspace_name: {self.ENVIRONMENT_NAME}; environment_name: {self.TENANT_ID}; 
                tenant_id:{self.ENVIRONMENT_FILE}; environment_file: {self.ENVIRONMENT_FILE}"""


class InitHandler:
    def __init__(self, name: str, path: str, env: EnvBank):
        self.name = name
        self.path = path
        self.env = env

    def start(self):
        StructureInit(pipe_name=self.name, path=self.path, env=self.env).start()



