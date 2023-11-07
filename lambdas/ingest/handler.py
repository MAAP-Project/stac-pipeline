import json
from typing import Dict
import importlib

from env import IngestEnv
ingest_env = IngestEnv()

from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from requests import post as requests_post
from request_cognito_oauth_token.main import get_creds
create_item_function = importlib.import_module(ingest_env.stac_module).create_item

def ingest_item(item: Dict):
    print(f"ingesting {item}")
    creds = get_creds(ingest_env.cognito_secret_arn)
    response = requests_post(
        url=ingest_env.post_url, data=json.dumps(item), headers={"Authorization": f"bearer {creds.access_token}"}
    )
    try:
        response.raise_for_status()
    except Exception:
        print(response.text)
        raise
    print('done ingesting item')

@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context):
    print(f"processing event")
    for record in event.records:
        body = json.loads(record["body"])
        for task in body:
            stac_item = create_item_function(task, ingest_env.catalog_url).to_dict(transform_hrefs=False) # bool flag is critical, otherwise pystac makes requests to the catalog and we overwhelm it. 
            ingest_item(stac_item)
    print('done processing event')