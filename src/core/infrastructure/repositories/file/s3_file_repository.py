from src.core.domain.repositories.file_repository import FileRepository
from src.core.utils.decorators.service_error_handler import service_error_handler
from uuid import UUID
from typing import Optional
import io
import os
import boto3

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )

class S3FileRepository(FileRepository):
    __MODULE = "s3.service"
    def __init__(self, client, bucket_name: str):
        self.s3_client = client
        self.bucket_name = bucket_name

    @service_error_handler(__MODULE)
    async def upload(
        self, 
        file_bytes: bytes,
        filename: str,
        company_id: UUID,
        user_id: UUID
    ) -> str:
        s3_key = self.__build_key(user_id=user_id, company_id=company_id, filename=filename)
        
        file_obj = io.BytesIO(file_bytes)
        
        self.s3_client.upload_fileobj(file_obj, self.bucket_name, s3_key)

        file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"

        return file_url
    
    @service_error_handler(__MODULE)
    def delete_user_data(self, user_id: UUID) -> None:
        prefix = self.__build_key(user_id=user_id)
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        if "Contents" in response:
            for obj in response["Contents"]:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=obj["Key"])
        return "User data deleted"


    @service_error_handler(__MODULE)
    def delete_company_data(self, user_id: UUID, company_id: UUID) -> None:
        prefix = self.__build_key(user_id=user_id, company_id=company_id)
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        if "Contents" in response:
            for obj in response["Contents"]:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=obj["Key"])
        return "Company data deleted"

    @service_error_handler(__MODULE)
    def delete_document_data(self, 
        user_id: UUID,
        company_id: UUID,
        filename: str
       
    ) -> None:
        s3_key = self.__build_key(user_id=user_id, company_id=company_id,  filename=filename)
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)


    @staticmethod
    def __build_key(
        user_id: UUID, 
        company_id: Optional[UUID] = None, 
        filename: Optional[str] = None
    ) -> str:
    
        key_parts = [str(user_id)]
        
        if company_id:
            key_parts.extend(["companies", str(company_id)])
            
        if filename:
            key_parts.extend(["docs", filename])
            
        return "/".join(key_parts)
    
