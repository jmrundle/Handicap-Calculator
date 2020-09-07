import boto3
from config import Config


def get_default_resource():
    return boto3.resource('dynamodb',
                          aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=Config.WS_SECRET_ACCESS_KEY,
                          region_name=Config.AWS_DEFAULT_REGION,
                          endpoint_url=Config.ENDPOINT_URL)


def create_tables(dynamo_db=None):
    if dynamo_db is None:
        dynamo_db = get_default_resource()

    courses = dynamo_db.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'course_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'city',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'state',
                'AttributeType': 'S'
            }
        ],
        TableName="courses",
        KeySchema=[
            {
                'AttributeName': 'course_id',
                'KeyType': 'HASH'
            }
        ]
    )

    tees = dynamo_db.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'course_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'city',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'state',
                'AttributeType': 'S'
            }
        ],
        TableName="courses",
        KeySchema=[
            {
                'AttributeName': 'tee_id',
                'KeyType': 'HASH'
            }
        ]
    )

