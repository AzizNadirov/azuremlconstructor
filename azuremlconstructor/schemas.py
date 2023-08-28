from dataclasses import dataclass

from azuremlconstructor.confs import configs as confs


# Schemas for Custom Exceptions
@dataclass
class IncorrectPipeNameSchema:
    UpMax:              str = f"Pipeline name longer than {confs.PIPE_NAME_MAX}"
    LowMin:             str = f"Pipeline name shorter than {confs.PIPE_NAME_MIN}"
    NotAllowedSymbols:  str = "Pipeline name should contain only letters, digits, - and _ symbols"
    IsKeyWord:          str = f"Pipeline name is keyword. Keywords: '{confs.PIPE_NAME_KEYWORDS}'"



@dataclass
class IncorrectStepNameSchema:
    IsNotIdentifier:    str = f"Step name must be identifier: only letters, digits and _ symbols"
    UpMax:              str = f"Step name longer than {confs.STEP_NAME_MAX}"
    LowMin:             str = f"Step name shorter than {confs.STEP_NAME_MIN}"
    IsKeyWord:          str = f"Step name is keyword. Keywords: '{confs.STEP_NAME_KEYWORDS}'"


@dataclass
class PathHasNoPipelineSchema:
    message:            str = f"Path doesn't contain any pipeline" 



@dataclass
class PathHasNoThePipelineSchema:
    message:            str = f"Path doesn't contain specified pipeline"



@dataclass
class PipelineHasNoTheStepSchema:
    message:            str = f"Path doesn't contain specified step"



@dataclass
class PipelineHasNoStepSchema:
    message:            str = f"Pipeline doesn't contain any step. There is must be at least one step"



@dataclass
class IncorrectArgumentTypeSchema:
    message:            str = f"Got incorrect type of argument"



@dataclass
class IncorrectFileNameSchema:
    message:            str = f"Passed Incorrect file name:"