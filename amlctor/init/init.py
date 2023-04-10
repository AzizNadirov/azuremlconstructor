import base64
import os
import json

import pydantic
from pydantic import BaseModel

from confs.configs import BANK_DIR, BASE_DIR

from .init_structure import StructureInit


class EnvBank:

    class EnvSchema(BaseModel):
            name: str
            subscription_id: str
            resource_group: str
            build_id: str
            workspace_name: str
            environment_name: str
            tenant_id: str
            environment_file: str = None


    def __init__(self, name: str, subscription_id: str, resource_group: str, build_id: str,
                 workspace_name: str, environment_name: str, tenant_id: str, environment_file: str=None):

        EnvBank.valid_name(name.strip())

        self.name = name.strip()
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.build_id = build_id
        self.workspace_name = workspace_name
        self.environment_name = environment_name
        self.tenant_id = tenant_id
        self.environment_file = environment_file



    @staticmethod
    def valid_name(name: str):
        if not name.isidentifier():
            raise ValueError("Env name must be identifier - as variable name.")

        return True


    def encoder(self, password):
        d = {
            "name": self.name, 'subscription_id': self.subscription_id,
            "resource_group": self.resource_group, 'build_id': self.build_id,
            "workspace_name": self.workspace_name, 'environment_name': self.environment_name,
            "tenant_id": self.tenant_id, 'environment_file': self.environment_file}
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
            name: str
            subscription_id: str
            resource_group: str
            build_id: str
            workspace_name: str
            environment_name: str
            tenant_id: str
            environment_file: str = None


        try:
            parsed_dict = EnvSchema.parse_raw(json_str).dict()  
            return EnvBank(**parsed_dict)
        
        except pydantic.error_wrappers.ValidationError as e:
            return -1


    @staticmethod
    def decoder(encoded_message, password):
        encoded_bytes = encoded_message.encode('utf-8')
        decoded_bytes = base64.b64decode(encoded_bytes)
        message_bytes = decoded_bytes[:-len(password)]
        message = message_bytes.decode('utf-8')
        return message

    def save(self, password: str):
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
                    print(f"Incorrect command: {r}. Enter y or n .")
        else:
            with open(file, 'w+') as f:
                f.write(encoded_env)
                print(f"Env saved as '{file}'")


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
            'subscription_id':      self.subscription_id,
            'resource_group':       self.resource_group,
            'build_id':             self.build_id,
            'workspace_name':       self.workspace_name,
            'environment_name':     self.environment_name,
            'tenant_id':            self.tenant_id,
            'environment_file':     self.environment_file}
        
        return d
        
    

    def set_environment_file(self, pipe_name: str):
        """ by default dev 'environment_file' = None. The method sets it for pipeline name """
        self.environment_file = f'{pipe_name}/settings/conda_dependencies.yml'


    def __str__(self):
        return f""" \t{self.name}\n
                subscription_id:        {self.subscription_id}
                resource_group:         {self.resource_group}
                build_id:               {self.build_id}
                workspace_name:         {self.workspace_name}
                environment_name:       {self.environment_name}
                tenant_id:              {self.tenant_id} 
                environment_file:      {self.environment_file}
                """
    

    def __repr__(self) -> str:
        return f"""EnvBamk<{self.name}>: subscription_id: {self.subscription_id}; resource_group: {self.resource_group}; 
                build_id: {self.build_id}; workspace_name: {self.workspace_name}; environment_name: {self.environment_name}; 
                tenant_id:{self.tenant_id}; environment_file: {self.environment_file}"""


class InitHandler:
    def __init__(self, name: str, path: str, env: EnvBank):
        self.name = name
        self.path = path
        self.env = env

    def start(self):
        StructureInit(pipe_name=self.name, path=self.path, env=self.env).start()



if __name__ == '__main__':

    test_eb = EnvBank(
        name='test_eb',
        subscription_id='tst12345',
        resource_group='test_res_group',
        build_id='1234567',
        workspace_name='test_wspace',
        environment_name='test_env_name',
        tenant_id='test_tenant_id'
    )

    test_eb.save('superpass')
    eb = EnvBank.load('test_eb', 'superpas')
    print(eb.name)
