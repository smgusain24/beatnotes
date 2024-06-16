import json
from config.app_logger import logger
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
from dotenv import load_dotenv
load_dotenv()


def get_secret():
    try:
        os_secrets = json.loads(os.environ.get('SECRETS'))
        secret_name = os_secrets.get('AWS_SECRET_NAME')
        region_name = os_secrets.get('AWS_REGION_NAME')
        aws_access_key = os_secrets.get('AWS_ACCESS_KEY')
        aws_secret_key = os_secrets.get('AWS_SECRET_KEY')
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            print(e)
            raise Exception(e)
        except NoCredentialsError as e:
            print(e)
            raise Exception(e)

        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except Exception as e:
        logger.error(e, exc_onfp=True, stack_info=True)


secrets = get_secret()


