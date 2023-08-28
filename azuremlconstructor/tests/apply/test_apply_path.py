from unittest import TestCase
from unittest.mock import patch
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from azuremlconstructor.confs.configs import BASE_DIR
from azuremlconstructor.__main__ import main





class TestApply(TestCase):
    def setUp(self):
        # create `pipes` dir for test pipes
        pipe_name = 'test_pipe'
        pipes_dir = Path.cwd() / 'pipes'
        pipes_dir.mkdir(mode=0o770)
        self.pipes_dir = pipes_dir

        # init pipe
        args = ['azuremlconstructor','init', '-n', pipe_name, '-p', pipes_dir]
        @patch('sys.argv', args)

        def init_pipe():
            main()

        init_pipe()
        self.pipe_name = pipe_name

    
    def test_apply(self):
        def fill_settings(path: Path):
            # test settings
            test_confs = {
            'AML_MODULE_NAME'               : 'test_aml',
            'SCRIPT_MODULE_NAME'            : 'test_script',
            'DATALOADER_MODULE_NAME'        : 'test_dataloader',
            'continue_on_step_failure'      : False,
            'pipe_name'                     : 'Test Pipe',
            'DESCRIPTION'                   : 'test descr',
            'file_name'                     : 'test_file_name',
            'file_datastore_name'           : 'test_ds_name',
            'file_path_on_datasore'         : 'test/path',
            'file_files'                    : ['file1.ext', 'file2.ext'],
            'file_data_reference_name'      : 'test_data_ref_name',
            'path_name'                     : 'test_path_name',
            'path_datastore_name'           : 'test_path_datastore_name',
            'path_path_on_datasore'         : 'path/path/on/datasore',
            'path_data_reference_name'      : 'test_path_data_reference_name',
            'step_name'                     : 'test_step',
            'step_compute_target'           : 'test_compute',
            'step_allow_reuse'              : False
            }

            j_env = Environment(loader=FileSystemLoader(f"{BASE_DIR}/tests/src/templates"))
            settings_t = j_env.get_template('settings')
            settings_content = settings_t.render(**test_confs)
            settingspy = path / 'settings/settings.py'
            with settingspy.open('w+') as f:
                f.write(settings_content)
            
        
        args = ['azuremlconstructor', 'apply', '-p', str(self.pipes_dir / self.pipe_name)]
        @patch('sys.argv', args)
        def do_apply():
            fill_settings(path=self.pipes_dir / self.pipe_name)
            main()
        
        do_apply()

        
