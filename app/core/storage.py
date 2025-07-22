import boto3
from app.core.config import settings
from botocore.exceptions import ClientError
import os
from loguru import logger
s3 = boto3.client(
    service_name="s3",
    endpoint_url=settings.s3_endpoint,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
)

def upload_to_storage(file_path: str, s3_key: str):
    s3.upload_file(file_path, settings.s3_bucket, s3_key)


def create_bucket(bucket_name):
    try:
        logger.info("Creating buket")
        s3.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            # Bucket does not exist, create it
            try:
                s3.create_bucket(Bucket=bucket_name)
            except ClientError as ce:
                # If bucket exists (race condition), ignore
                if ce.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
                    raise
        elif error_code == '403':
            # Forbidden, bucket exists but you don’t have access — raise or handle accordingly
            raise
        else:
            raise

create_bucket(settings.s3_bucket)