#!Python 3.9.16
# config constants
from pathlib import Path
import os

BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__))).parent

BANK_DIR = BASE_DIR / "confs/ebs"

TEMPLATES_DIR = BASE_DIR / "src/templates"


# Name Restrictions:
PIPE_NAME_MAX: int = 64
STEP_NAME_MAX: int = 128
PIPE_NAME_MIN: int = 1
STEP_NAME_MIN: int = 1
PIPE_NAME_KEYWORDS = ("default", "outputs", "inputs", "steps", "endpoint", "resourceGroup",
                        "subscriptionId", "tenantId", "clientId", "clientSecret")

STEP_NAME_KEYWORDS = ("default", "outputs", "inputs", "steps", "endpoint", "resourceGroup",
                        "subscriptionId", "tenantId", "clientId", "clientSecret")



