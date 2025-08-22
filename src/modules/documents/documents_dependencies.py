import boto3
import os
from src.modules.documents.s3_service import S3Service

def configure_documents_dependencies():
    client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    
    bucket_name = os.getenv('S3_BUCKET_NAME')

    service = S3Service(
        client=client,
        bucket_name=bucket_name
    )