import boto3
import os
from fastapi import UploadFile
from src.core.decorators.service_error_handler import service_error_handler
from uuid import UUID

class S3Service:
    __MODULE = "s3.service"
    def __init__(self, client, bucket_name: str):
        ######## for typing only:::: use client arg in prod ##########
        self.s3_client = boto3.client(
            's3'
        )
       ########################################################################
        self.bucket_name = bucket_name

    @service_error_handler(f"{__MODULE}.upload")
    def upload(
        self, 
        file: UploadFile,
        s3_key: str
    ) -> str:
        self.s3_client.upload_fileobj(file, self.bucket_name, s3_key)

        file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"

        return file_url
    
    @staticmethod
    def send_to_agent_knowlege_base():
        pass
    
    @staticmethod
    def get_knowlege_base_key(company_id: UUID, agent_id: UUID, filename: str):
        return f"{company_id}/knowlege_base/{agent_id}/{filename}"