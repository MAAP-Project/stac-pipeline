import json
from typing import List
import pandas as pd
import boto3
from env import InventoryEnv

inventory_env = InventoryEnv()

def list_tasks(inventory_s3_path: str) -> List:
    print('listing tasks')
    paths = list(pd.read_csv(inventory_s3_path)[inventory_env.file_key])
    print('done listing tasks')
    return paths

def handler(event, context):
    queue_url = event['queue_url']
    sqs_client = boto3.client("sqs")
    for task in list_tasks(inventory_env.file_location):
        sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps({'task':task}))
