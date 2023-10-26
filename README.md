# Simple STAC pipeline

This repository stores infrastructure as code for a simple STAC metadata creation and ingestion pipeline that works as follows with three main components: 

- an _'inventory' lambda_ reads a CSV file column and sends each row as a message to an _SQS queue_
- the SQS queue messages are received by another, _'ingest' lambda_ that creates a STAC item for each message and posts it to a STAC catalog. 

Key information to be provided by the user is (1) the inventory csv location and (2) the location of the python package containing the module that will be used by the `ingest` lambda the create the STAC records. An example is shown in `.example_env`. See below for more details on configuration.

## Requirements 

- python
- docker
- the AWS `cdk` CLI and AWS credentials configured in the environment. 

## Installation

```
python -m venv .venv 
source .venv/bin/activate
pip install -r requirements.txt
```
## Usage

### Configuration and Deployment

First, you need to deploy the two lambdas and the queue. To configure the deployment,
populate an `.env` file at the root of this repository with the parameters defined in `settings.py` and `lambdas/*/env.py`. These are defined using `pydantic-settings`. 

Once you configured your deployment, you can deploy the resources from the root of this repo :

```
cdk deploy --all --app "python deployment.py"
```

### Trigger the pipeline

Simply invoke the inventory lambda passing as a single input the `queue-url` resulting from the deployment. You can invoke it either through the CLI or on the console with a test run. 