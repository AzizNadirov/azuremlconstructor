from unittest import TestCase
import base64
import os
import json

from confs.configs import BANK_DIR

from core.init import EnvBank


class TestEBCreation(TestCase):
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

    def test_encoder(self):
        password = 'superpass'
        msg = self.eb.encoder(password=password)


