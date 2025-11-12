from src.core.dependencies.container import Container
from src.core.utils.logs.logger import Logger
from src.core.services.email_service import EmailService

def configure_container():
    logger = Logger()
    Container.register("logger", logger)

    email_service = EmailService()
    Container.register("email_service", email_service)