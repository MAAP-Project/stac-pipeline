from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class IngestEnv(BaseSettings):
    
    model_config = SettingsConfigDict(env_prefix='INGEST_', env_file='.env')
    
    stac_module: str = Field(description="name of the function in the stac module to call to create a STAC item")
    
    cognito_secret_arn: str = Field(description="arn of secret id for cognito user pool")
    
    post_url: str = Field(description="url for POST request to the ingestor")