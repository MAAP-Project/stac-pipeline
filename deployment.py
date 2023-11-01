
from aws_cdk import App, Stack
from constructs import Construct
from aws_cdk import Duration
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from aws_cdk.aws_lambda import Runtime
from aws_cdk.aws_sqs import Queue 
from aws_cdk.aws_iam import ManagedPolicy, PolicyStatement, Effect
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from settings import DeploymentSettings
from pathlib import Path
deployment_settings = DeploymentSettings()

LAMBDAS_FOLDER = 'lambdas'
INGEST_LAMBDA_FOLDER = 'ingest'
INVENTORY_LAMBDA_FOLDER = 'inventory'
INGEST_REQUIREMENTS_FILE_PATH = Path(f'{LAMBDAS_FOLDER}/{INGEST_LAMBDA_FOLDER}/requirements.txt')

class StacPipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the SQS queue
        queue = Queue(self,
                      "queue",
                      visibility_timeout=Duration.minutes(15),
                      retention_period=Duration.days(14)
        )

        capitalize_keys = lambda env, prefix: {f'{prefix}{key.upper()}': value for key, value in env.items()}
        inventory_env = capitalize_keys(deployment_settings.inventory_env.model_dump(), 'INVENTORY_')
        
        inventory_lambda = PythonFunction(
            self,
            "inventory",
            entry=f'{LAMBDAS_FOLDER}/{INVENTORY_LAMBDA_FOLDER}',
            index="handler.py",
            handler="handler",
            runtime=getattr(Runtime,deployment_settings.inventory_runtime),
            environment=inventory_env,
            timeout=Duration.seconds(deployment_settings.inventory_timeout),
            memory_size=deployment_settings.inventory_memory_size     
        )
        
        inventory_lambda.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )
        
        # Grant permission to send messages to the queue
        queue.grant_send_messages(inventory_lambda)

        # policy for the ingest lambda to read the cognito secret
        read_cognito_secret_policy = PolicyStatement(
            effect=Effect.ALLOW,
            actions=["secretsmanager:GetSecretValue"],
            resources=[deployment_settings.ingest_env.cognito_secret_arn]
        )

        ingest_env = capitalize_keys(deployment_settings.ingest_env.model_dump(), 'INGEST_')

        # add the user provided stac dependency to the file
        INGEST_REQUIREMENTS_FILE_PATH.write_text(f'{INGEST_REQUIREMENTS_FILE_PATH.read_text()}\n{deployment_settings.stac_package}')

        try:
            ingest_lambda = PythonFunction(
                self,
                "ingest",
                entry=f"{LAMBDAS_FOLDER}/{INGEST_LAMBDA_FOLDER}",
                index="handler.py",
                handler="handler",
                runtime=getattr(Runtime,deployment_settings.ingest_runtime),
                environment=ingest_env,
                timeout=Duration.seconds(deployment_settings.ingest_timeout),
                memory_size=deployment_settings.ingest_memory_size,
            )
        except Exception as e:
            raise e
        finally:
            # the addition ran at this point, and we want to clean that up.
            INGEST_REQUIREMENTS_FILE_PATH.write_text(INGEST_REQUIREMENTS_FILE_PATH.read_text().replace(f'\n{deployment_settings.stac_package}',''))
                    
        # Grant permission to read messages from the queue
        queue.grant_consume_messages(ingest_lambda)

        # Configure the ingest lambda to poll messages from the queue
        ingest_lambda.add_event_source(SqsEventSource(queue))
        
    
        ingest_lambda.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )
        
        ingest_lambda.role.add_to_policy(read_cognito_secret_policy)
        
            
        
app = App()

pipeline = StacPipelineStack(app, f"{deployment_settings.pipeline_id}-stack")

app.synth()