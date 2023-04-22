from pathlib import Path
from typing import Union

from amlctor.apply.apply import StructureApply

from amlctor.utils import is_pipe, get_settingspy
from amlctor.exceptions import PathHasNoPipelineException, PipelineHasNoTheStepException
from amlctor.schemas import PathHasNoPipelineSchema, PipelineHasNoTheStepSchema



class UpdateHandler:
    def __init__(self, path: Path, for_step: Union[str, bool]) -> None:
        """ 
            Update dataloaders. 
            path: path to the pipeline
            for_step:   if False - update for all steps
                        otherwise for the step name passed here
        """
        # TODO generally, there are so many things for thinking on. For now, just `dataloaders`
        self.path = path
        self.for_step = for_step
        


    def validate(self) -> bool:
        def validate_DIU(path: Path):
                """ Validate DataInput names uniqueness """
                steps = get_settingspy(path)['STEPS']
                for step in steps:
                    tmp_datainputlst = []
                    for inp in step.input_data:
                        if inp.name in tmp_datainputlst:
                            raise ValueError(f"Dublicate DataInput name: '{inp.name}'. Input names of the step must be unique!")
                        else:
                            tmp_datainputlst.append(inp.name)

        if self.for_step is False:   # for all steps
            if not is_pipe(self.path):
                raise PathHasNoPipelineException(path=self.path,
            
                                               message=PathHasNoPipelineSchema.message)
            validate_DIU(self.path)
            return True
        else:
            if not is_pipe(self.path, self.for_step, is_step=True):
                pipe_name = self.path.name
                raise PipelineHasNoTheStepException(pipe_name=pipe_name, step_name=self.for_step,
                                                    message=PipelineHasNoTheStepSchema.message)
            validate_DIU(self.path)
            
            return True
            


    def update(self):
        self.settingspy = get_settingspy(self.path)
        if not self.for_step is True:           # Update for all steps
            steps = self.settingspy['STEPS']
            for step in steps:
                dataloader = self.path / step.name / f"{self.settingspy['DATALOADER_MODULE_NAME']}.py"
                content, _ = StructureApply.create_dataloader_content(step)
                with dataloader.open(mode='w') as dataloader_file:
                    dataloader_file.write(content)
        else:
            dataloader = self.path / self.for_step / f"{self.settingspy['DATALOADER_MODULE_NAME']}.py"
            content, _ = StructureApply.create_dataloader_content(step)
            with dataloader.open(mode='w') as dataloader_file:
                dataloader_file.write(content)

            

    def start(self):
        self.validate()
        self.update()
