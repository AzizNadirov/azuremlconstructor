#!Python 3.9.16
# config constants
from pathlib import Path
import os

BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__))).parent

BANK_DIR = f"{BASE_DIR}/confs/ebs"

TEMPLATES_DIR = f"{BASE_DIR}/src/templates"


