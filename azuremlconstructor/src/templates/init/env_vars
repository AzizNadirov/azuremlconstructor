from dataclasses import dataclass
import os
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Env:
    # Loads all environment variables into a predefined set of properties
    # to load .env file into environment variables for local execution

    load_dotenv()
    workspace_name: Optional[str] = os.environ.get("WORKSPACE_NAME")
    resource_group: Optional[str] = os.environ.get("RESOURCE_GROUP")
    subscription_id: Optional[str] = os.environ.get("SUBSCRIPTION_ID")
    build_id: Optional[str] = os.environ.get("BUILD_ID")
    environment_name: Optional[str] = os.environ.get("ENVIRONMENT_NAME")
    environment_file: Optional[str] = os.environ.get("ENVIRONMENT_FILE")
    tenant_id: Optional[str] = os.environ.get("TENANT_ID")
