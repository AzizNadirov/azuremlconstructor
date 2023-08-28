import unittest
from unittest import TestCase
import os
# import json

from azuremlconstructor.confs.configs import BANK_DIR

from azuremlconstructor.init.init import EnvBank


class TestEnvBank(TestCase):
    def setUp(self):
        self.eb = EnvBank(
            name='test_eb', 
            subscription_id = 'tst12345',
            resource_group = 'test_res_group',
            build_id= '1234567',
            workspace_name = 'test_wspace',
            environment_name='test_env_name',
            tenant_id='test_tenant_id'
            )


    def test_save(self):
        password = 'superpass'
        self.eb.save(password=password)

        path = f"{BANK_DIR}/{self.eb.name}.e"
        self.assertTrue(os.path.exists(path))
    

    def test_load(self):
        password = 'superpass'
        name = self.eb.name
        res_eb = EnvBank.load(name=name, password=password)
        # test result eb instance
        self.assertTrue(isinstance(res_eb, EnvBank))
        self.assertTrue(res_eb.name == name)
        self.assertTrue(res_eb.subscription_id == self.eb.subscription_id)
        self.assertTrue(res_eb.resource_group == self.eb.resource_group)
        self.assertTrue(res_eb.build_id == self.eb.build_id)
        self.assertTrue(res_eb.workspace_name == self.eb.workspace_name)
        self.assertTrue(res_eb.environment_name == self.eb.environment_name)
        self.assertTrue(res_eb.tenant_id == self.eb.tenant_id)






if __name__ == '__main__':

    unittest.main()


