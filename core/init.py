import base64
import os
import json

from confs.configs import BANK_DIR


class EnvBank:
    def __init__(self, name, subscription_id, resource_group, build_id, workspace_name,
                    environment_name, tenant_id):
        
        self.name = name
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.build_id = build_id
        self.workspace_name = workspace_name
        self.environment_name = environment_name
        self.tenant_id = tenant_id

    def encoder(self, password):
        d = {
            "name": self.name, 'subscription_id': self.subscription_id,
            "resource_group": self.resource_group, 'build_id': self.build_id,
            "workspace_name": self.workspace_name, 'environment_name': self.environment_name,
            "tenant_id": self.tenant_id}
        d = json.dumps(d)
        message = f"{d}"
        message_bytes = message.encode('utf-8')
        password_bytes = password.encode('utf-8')
        encoded_bytes = base64.b64encode(message_bytes + password_bytes)
        encoded_message = encoded_bytes.decode('utf-8')
        return encoded_message
    
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
        file = f"{BANK_DIR}/{self.name}.acc"
        if os.path.exists(file):
            while True:
                r = input(f"File '{self.name}.acc' already exists. Dou you want to overwrite it? Old file will be lost? y/n: ")
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

    @staticmethod
    def load(name: str, password: str):
        file = f"{BANK_DIR}/{name}.acc"
        if os.path.exists(file):
            with open(file, 'r') as f:
                encoded_env = f.read()

            decoded_env = EnvBank.decoder(encoded_env, password)
            dict_env = json.loads(decoded_env)
            
            return EnvBank(**dict_env)
        
        else:
            raise ValueError(f"There is no Env in such name: {file}")
    
if __name__ == '__main__':

    test_eb = EnvBank(
            name='test_eb', 
            subscription_id = 'tst12345',
            resource_group = 'test_res_group',
            build_id= '1234567',
            workspace_name = 'test_wspace',
            environment_name='test_env_name',
            tenant_id='test_tenant_id'
            )

    test_eb.save('superpass')








