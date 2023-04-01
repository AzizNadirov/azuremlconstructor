from pathlib import Path
from dataclasses import dataclass
from typing import List, Union

from azureml.pipeline.core import Pipeline
from azureml.pipeline.steps import PythonScriptStep
from azureml.core.runconfig import RunConfiguration
from azureml.core import Workspace, Datastore, Environment, Run
from azureml.core.authentication import InteractiveLoginAuthentication

from amlctor.apply.env import get_env
from amlctor.utils import get_settingspy_module

from amlctor.input import PathInput, FileInput, FileInputSchema, PathInputSchema



class Step:
    def __init__(self,
                 path: Path,
                 name: str, 
                 compute_target: str, 
                 input_data: List[Union[PathInput, FileInput]], 
                 allow_reuse: bool=False):
        
        """
            path:               pipeline path
            name:               step name
            compute_target:     aml compute cluster name
            input_data:         data inputs for the step
            allow_reuse:        TODO
        """
        
        self.name = name
        self.compute_target = compute_target
        self.input = input_data
        self.allow_reuse = allow_reuse
        e = get_env()
        self.env = Environment.from_conda_specification(e.environment_name, e.environment_file)
        self.step = self.build_step(path)


    def build_step(self, path: Path):
        settingspy = get_settingspy_module(path)

        step = PythonScriptStep(name=self.name,
                                script_name=f"{self.name}/{settingspy['AML_MODULE_NAME']}.py",
                                compute_target=self.compute_target,
                                source_directory=None,
                                inputs=[i.data for i in self.input],
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
        self.workspace = self.get_workspace()
        self.env = get_env()
        self.continue_on_step_failure = continue_on_step_failure
        self.path = path
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


    def _publish(self):
        self._validate()
        published_pipe = self.pipeline.publish(name=self.name,
                                               description=self.description,
                                               version=self.env.build_id,
                                               continue_on_step_failure=self.continue_on_step_failure)

        print(f"Published: {published_pipe.name}")
        print(f"With build: {published_pipe.version}")


    def get_workspace(self):
        e = get_env()
        interactive_auth = InteractiveLoginAuthentication(tenant_id=e.tenant_id)
        workspace = Workspace.get(
            name=e.workspace_name,
            subscription_id=e.subscription_id,
            resource_group=e.resource_group,
            auth=interactive_auth
        )
        return workspace
    


@dataclass(frozen=True)
class StepSchema:
    name: str
    compute_target: str
    input_data: List[Union[FileInputSchema, PathInputSchema]]
    allow_reuse: bool = False



