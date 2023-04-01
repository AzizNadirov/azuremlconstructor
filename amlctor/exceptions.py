from pathlib import Path
from typing import Callable, Union



class IncorrectPipeNameException(Exception):
    """ 
        Pipe has incorrect name.
        name: pipeline name
        message: ArgsHandler extracts the message from `schema` and sends here.
    """
    def __init__(self, name: str, message: str, *args: object) -> None:
        self.name = name
        self.message: str = f"{message} '{name}'"
        super().__init__(self.message, *args)



class IncorrectStepNameException(Exception):
    """ Step has incorrect name """
    def __init__(self, step_name: str, message: str, *args: object) -> None:
        self.name = step_name
        self.message: str = f"{message}. Step: '{step_name}'"
        super().__init__(self.message, *args)



class PathHasNoPipelineException(Exception):
    """ There is no any pipeline on the path """
    def __init__(self, path, message,  *args: object) -> None:
        self.path = path
        self.message: str = f"{message}. Path: '{path}'"
        super().__init__(self.message, *args)



class PathHasNoThePipelineException(Exception):
    """ There is no specified pipeline on the path """
    def __init__(self, path: Path, pipe_name: str, message: str, *args: object) -> None:
        self.path = path
        self.message: str = f"{message}. Pipeline: '{pipe_name}' at '{path}'"
        super().__init__(self.message, *args)



class PipelineHasNoTheStepException(Exception):
    """ There is no a specified step in the pipeline on the path """
    def __init__(self, pipe_name: str, step_name: str, message: str, *args: object) -> None:
        self.message: str = f"{message} 'Pipeline: {pipe_name}' Step: '{step_name}'"
        super().__init__(self.message, *args)



class PipelineHasNoStepException(Exception):
    """ There is no any steps in pipeline on the path """
    def __init__(self, path: Path, pipe_name: str, message: str, *args: object) -> None:
        self.path = path
        self.message: str = f"{message} Pipeline: '{pipe_name}' at '{path}'"
        super().__init__(self.message, *args)



class IncorrectTypeArgumentException(Exception):
    def __init__(self, message: str, valid_type: Union[Callable, tuple, list], actually_is: Callable, *args: object) -> None:
        self.message = f"{message}. Should be: '{valid_type}'; Passed: '{actually_is}'"
        super().__init__(message, *args)



class IncorrectFileNameException(Exception):
    def __init__(self, message: str, filename: str, *args: object) -> None:
        self.message = f"{message}. '{filename}'"
        super().__init__(*args)

