from src.core.dependencies.container import Container
from src.core.services.email_service import EmailService

def configure_container():


    email_service = EmailService()
    Container.register("email_service", email_service)