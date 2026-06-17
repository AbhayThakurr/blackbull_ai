import boto3
from functools import lru_cache
from app.config.settings import settings

@lru_cache()
def get_bedrock_client():
    """
    Initializes and returns a singleton Boto3 client for Amazon Bedrock Runtime.
    Using lru_cache ensures we don't recreate the client on every call.
    """
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
