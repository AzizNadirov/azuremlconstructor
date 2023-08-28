from pathlib import Path
from typing import List, Union

from azuremlconstructor._utils import get_settingspy, is_pipe
from azuremlconstructor.core import PathInput, FileInput, Step, PathInputSchema, FileInputSchema, StepSchema, Pipe



class RunHandler:

    def __init__(self, path: Path):
        self.path = path
        self.check_path()
        self.settingspy = get_settingspy(path)
        self.env_path = path / 'settings/.env'


    def check_path(self):
        if not is_pipe(self.path):
            raise ValueError(f"Passed path doesn't contain pipeline: '{self.path}'")
        


    def input_fromschema(self, step: StepSchema) -> List[PathInput | FileInput]:
        if not bool(step.input_data):   # there are no any input data
            return []
        
        inputs = []

        for inp in step.input_data:
            if not isinstance(inp, (PathInputSchema, FileInputSchema)):
                raise ValueError(f"Unknown input data: {type(inp)}")
            
            if isinstance(inp, PathInputSchema):
                input_instance = PathInput(
                                            name=inp.name,
                                            datastore_name=inp.datastore_name,
                                            path_on_datasore=inp.path_on_datastore,
                                            denv_path=self.env_path               
                    )
                inputs.append(input_instance)

            elif isinstance(inp, FileInputSchema):
                input_instance = FileInput(
                                            name=inp.name,
                                            datastore_name=inp.datastore_name,
                                            path_on_datasore=inp.path_on_datastore,
                                            filename=inp.files,
                                            data_reference_name=inp.data_reference_name,
                                            denv_path=self.env_path               
                    )
                inputs.append(input_instance)

            else:
                raise ValueError(f"Mysteric case: invalid input instance: '{inp}' of type: '{type(inp)}'")
        
        return inputs
    


    def step_fromschema(self, step: StepSchema) -> Step:
        step_input = self.input_fromschema(step)      # realise input data
        if step_input is None: step_input = []
        step_instance = Step(
            path = self.path,
            name = step.name,
            compute_target = step.compute_target,
            input_data = step_input,                        # give realised data
            allow_reuse = step.allow_reuse
        )

        return step_instance

            
    def validate(self):
        # def validate():   #TODO
        #     assert isinstance(pipeline, Pipe)
        #     if not bool(pipeline.steps):
        #         raise ValueError(f"There are no steps for run...")
        pass


    def build_pipe(self) -> Pipe:
        pipe_instance = Pipe(
            name = self.settingspy['NAME'],
            description = self.settingspy['DESCRIPTION'],
            steps = [self.step_fromschema(step) for step in self.settingspy['STEPS']],
            path=self.path,
            continue_on_step_failure = self.settingspy['EXTRA']['continue_on_step_failure'],
            commit = True
        )

        return pipe_instance
    


    def publish(self, pipeline: Pipe):
        submit_options = self.settingspy['EXTRA']['submit']
        if submit_options.get('is_active') is True:
            pipeline._publish(submit=submit_options)



    def start(self):
        self.validate()
        pipe = self.build_pipe()
        self.publish(pipeline=pipe)




