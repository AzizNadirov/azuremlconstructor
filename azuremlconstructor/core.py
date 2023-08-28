from pathlib import Path
from dataclasses import dataclass
from typing import List, Union, Dict, Literal

from azureml.pipeline.core import Pipeline
from azureml.core.experiment import Experiment
from azureml.pipeline.steps import PythonScriptStep
from azureml.core.runconfig import RunConfiguration
from azureml.core import Workspace, Environment
from azureml.core.authentication import InteractiveLoginAuthentication

from azuremlconstructor.denv.dot_env_loader import get_env
from azuremlconstructor._utils import get_settingspy

from azuremlconstructor.input import PathInput, FileInput, FileInputSchema, PathInputSchema



class Step:
    def __init__(self,
                 path: Path,
                 name: str, 
                 compute_target: str, 
                 input_data: List[PathInput | FileInput], 
                 allow_reuse: bool=False):
        
        """
            path:               pipeline path
            name:               step name
            compute_target:     aml compute cluster name
            input_data:         data inputs for the step
            allow_reuse:        if True in error case execution will start from current step
        """
        
        self.name = name
        self.compute_target = compute_target
        self.input = input_data
        self.allow_reuse = allow_reuse
        e = get_env(path / 'settings/.env')
        e.ENVIRONMENT_FILE = path / e.ENVIRONMENT_FILE
        self.env = Environment.from_conda_specification(e.ENVIRONMENT_NAME, e.ENVIRONMENT_FILE)
        self.step = self.build_step(path)


    def step_unpack_inputs(self) -> list:
        """ collects all data inputs into one list """
        input_list = []
        for inp in self.input:
            if isinstance(inp, FileInput):
                input_list.extend(inp.data)
            elif isinstance(inp, PathInput):
                input_list.append(inp.data)
        
            else:
                raise ValueError('Unexpected data input type: ', type(inp))

        return input_list



    def build_step(self, path: Path):
        settingspy = get_settingspy(path)
        inputs = [inp.data for inp in self.input]
        step = PythonScriptStep(name=self.name,
                                script_name=f"{self.name}/{settingspy['AML_MODULE_NAME']}.py",
                                compute_target=self.compute_target,
                                source_directory=None,
                                inputs=inputs,
                                arguments=self.get_arguments(),
                                runconfig=self.get_run_config(),
                                allow_reuse=self.allow_reuse)
        return step


    def get_run_config(self):
        run_config = RunConfiguration()
        run_config.environment = self.env
        return run_config


    def get_arguments(self):
        arguments = []
        for data in self.input:
            arguments.append(f"--{data.name}")
            arguments.append(data.data)

        return arguments
    
    


class Pipe:
    def __init__(self, 
                 path: Path,
                 name: str, 
                 description: str,
                 steps: list,
                 continue_on_step_failure: bool=False,
                 commit: bool=True):
        
        self.name = name
        self.description = description
        self.steps = steps
        self.continue_on_step_failure = continue_on_step_failure
        self.continue_on_step_failure = continue_on_step_failure
        self.path = path
        self.workspace = self.get_workspace()
        self.env = get_env(path / 'settings/.env')
        assert isinstance(commit, bool)
        if commit:
            self.pipeline = self.create_pipeline()
        else:
            self.pipeline = None


    def create_pipeline(self):
        steps = [step.step for step in self.steps]
        pipeline = Pipeline(workspace=self.workspace, steps=steps, default_source_directory=self.path)
        return pipeline


    def _validate(self):
        self.pipeline.validate()


    def submit(self, experiment_name: str, job_name: str = None, tags: dict = None, kwargs: dict = None)->str:
        """ submit the pipeline 
            Parameters:
                experiment_name: name of the experiment
                job_name: name of the job
            Returns:
                job url: str - url to the job (portal.azure.com)
        """
        if job_name is None:
            job_name = self.name

        experiment = Experiment(workspace=self.workspace, name=experiment_name)
        if kwargs:      run = experiment.submit(self.pipeline, name=job_name, tags=tags, **kwargs)
        else:           run = experiment.submit(self.pipeline, name=job_name, tags=tags)

        return run.get_portal_url()


    def _publish(self, submit: Dict[Literal['experiment_name', 'job_name', 'is_active', 'tags', 'kwargs'], str] = None):
        self._validate()
        published_pipe = self.pipeline.publish(name=self.name,
                                               description=self.description,
                                               version=self.env.BUILD_ID,
                                               continue_on_step_failure=self.continue_on_step_failure)

        print(f"Published: {published_pipe.name}")
        print(f"With build: {published_pipe.version}")

        # look for submitting options
        if not submit is None:
            url = self.submit(experiment_name=  submit['experiment_name'], 
                              job_name=         submit['job_name'])
            

    def get_workspace(self):
        e = get_env(self.path / 'settings/.env')
        interactive_auth = InteractiveLoginAuthentication(tenant_id=e.TENANT_ID)
        workspace = Workspace.get(
            name=e.WORKSPACE_NAME,
            subscription_id=e.SUBSCRIPTION_ID,
            resource_group=e.RESOURCE_GROUP,
            auth=interactive_auth
        )
        return workspace
    

    def __str__(self):
        return f"<{self.name}: {self.steps}>"
    


@dataclass(frozen=True)
class StepSchema:
    name: str
    compute_target: str
    input_data: List[Union[FileInputSchema, PathInputSchema]]
    allow_reuse: bool = False



