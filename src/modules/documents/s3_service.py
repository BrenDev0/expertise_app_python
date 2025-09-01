from fastapi import UploadFile
from src.core.decorators.service_error_handler import service_error_handler
from uuid import UUID

class S3Service:
    __MODULE = "s3.service"
    def __init__(self, client, bucket_name: str):
        self.s3_client = client
        self.bucket_name = bucket_name

    @service_error_handler(f"{__MODULE}")
    def upload(
        self, 
        file: UploadFile,
        company_id: UUID,
        user_id: UUID
    ) -> str:
        s3_key = self.__get_key(user_id=user_id, company_id=company_id, filename=file.filename)
        self.s3_client.upload_fileobj(file, self.bucket_name, s3_key)

        file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"

        return file_url
    
    @service_error_handler(f"{__MODULE}")
    def delete(self, 
        user_id: UUID,
        company_id: UUID,
        filename: str
    ) -> None:
        s3_key = self.__get_key(user_id=user_id, company_id=company_id, filename=filename)
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)

    @staticmethod
    def __send_to_agent_knowlege_base():
        pass

    @staticmethod
    def __get_key(user_id: UUID, company_id: UUID, filename: str) -> str:
        return f"{user_id}/companies/{company_id}/docs/{filename}"
    
