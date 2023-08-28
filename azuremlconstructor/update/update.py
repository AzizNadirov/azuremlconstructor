from pathlib import Path
from typing import Union

from azuremlconstructor.apply.apply import StructureApply

from azuremlconstructor._utils import is_pipe, get_settingspy, get_not_applied_steps
from azuremlconstructor.exceptions import PathHasNoPipelineException, PipelineHasNoTheStepException
from azuremlconstructor.schemas import PathHasNoPipelineSchema, PipelineHasNoTheStepSchema



class UpdateHandler:
    def __init__(self, path: Path, overwrite: bool=False) -> None:
        """ 
            Update dataloaders. 
            path: path to the pipeline
            for_step:   if False - update for all steps
                        otherwise for the step name passed here
        """
        self.path = path   
        self.overwrite = overwrite     


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

        if not is_pipe(self.path):
            raise PathHasNoPipelineException(   path=self.path,
                                                message=PathHasNoPipelineSchema.message)
        validate_DIU(self.path)
        return True
            


    def update(self):
        """ check for new or controversial steps/datainput changes """
        # take care on steps
        notapplieds = get_not_applied_steps(path=self.path)
        if len(notapplieds) > 0:    print(f"Steps that are not applied:\n\t{notapplieds}")
        else:                      
            print(f"All steps from settings.py implemented.")
            if not self.overwrite: print(f"Creating modules. If you want to overwrite modules without ant prompt, wun with '--overwrite' flag.")
            else:                  print(f"Overwriting modules.")  
            
        StructureApply(path=self.path).make_step_dirs(for_steps=notapplieds, overwrite=self.overwrite)    # create files for un-appplieds
        print("\tDone")
        # take care of dataloaders
        print("Updating dataloader:")
        self.settingspy = get_settingspy(self.path)
        steps = self.settingspy['STEPS']
        for step in steps:
            print(f"\tFor '{step.name}' step.")
            dataloader = self.path / step.name / f"{self.settingspy['DATALOADER_MODULE_NAME']}.py"
            content, _ = StructureApply.create_dataloader_content(step)
            with dataloader.open(mode='w') as dataloader_file:
                dataloader_file.write(content)
            print("\t\tDone.")

            

    def start(self):
        self.validate()
        self.update()
