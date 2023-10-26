from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from lambdas.ingest.env import IngestEnv
from lambdas.inventory.env import InventoryEnv
from aws_cdk import Duration

class DeploymentSettings(BaseSettings):
    
    model_config = SettingsConfigDict(env_prefix='DEPLOYMENT_', env_file='.env')
    
    pipeline_id: str = Field(description="ID of the pipeline to deploy", default="montesano-test")
    
    ingest_env: IngestEnv = Field(description="Settings for the ingest lambda", default=IngestEnv())
    
    inventory_env: InventoryEnv = Field(description="Settings for the inventory lambda", default=InventoryEnv())

    stac_package : str = Field(description="argument to pass to the `pip install` command to install the package with a `package.stac.create_item` function")

    ingest_timeout: int = Field(description="timeout for the ingest lambda in seconds", default=900)
    
    ingest_memory_size: int = Field(description="memory size for the ingest lambda in MB", default=1024)
    
    ingest_runtime: str = Field(description="runtime for the ingest lambda", default="PYTHON_3_11")
    
    inventory_timeout: int = Field(description="timeout for the inventory lambda in seconds", default=300)
    
    inventory_memory_size: int = Field(description="memory size for the inventory lambda in MB", default=1024)
    
    inventory_runtime: str = Field(description="runtime for the inventory lambda", default="PYTHON_3_11")
