from src.core.dependencies.container import Container
from src.core.services.data_handling_service import DataHandlingService
from src.core.services.email_service import EmailService
from src.core.services.encryption_service import EncryptionService
from src.core.services.hashing_service import HashingService
from src.core.services.http_service import HttpService
from src.core.logs.logger import Logger
from src.core.middleware.middleware_service import MiddlewareService
from src.core.services.request_validation_service import RequestValidationService
from src.core.services.webtoken_service import WebTokenService
from src.modules.users.users_dependencies import configure_users_dependencies
from src.modules.companies.companies_dependencies import configure_companies_dependencies
from src.modules.invites.invites_dependencies import configure_invites_dependencies
from src.modules.employees.employees_dependencies import configure_employee_dependencies
from src.modules.agents.agents_dependencies import configure_agents_dependencies

def configure_container():
    ## core ##   
    
    # Independent #
    email_service = EmailService()
    Container.register("email_service", email_service)

    encryption_service = EncryptionService()
    Container.register("encryption_service", encryption_service)

    hashing_service = HashingService()
    Container.register("hashing_service", hashing_service)

    logger = Logger()
    Container.register("logger", logger)

    request_validation_service = RequestValidationService()
    Container.register("request_validation_service", request_validation_service)

    webtoken_service = WebTokenService()
    Container.register("webtoken_service", webtoken_service)


    # Dependent # Must configure all independent instances above this line #
    data_handler = DataHandlingService(
        encryption_service=encryption_service,
        hashing_service=hashing_service
    )
    Container.register("data_handler", data_handler)

    http_service = HttpService(
        logger=logger,
        encryption_service=encryption_service,
        hashing_service=hashing_service,
        request_validation_service=request_validation_service,
        webtoken_service=webtoken_service
    )
    Container.register("http_service", http_service)

    middleware_service = MiddlewareService(
        http_service=http_service
    )
    Container.register("middleware_service", middleware_service)

    ## Module # Must configure core dependencies above this line ##

    # single domain # 
    configure_agents_dependencies(
        http_service=http_service
    )

    configure_companies_dependencies(
        http_service=http_service
    )

    configure_invites_dependencies(
        http_service=http_service,
        data_handler=data_handler,
        email_service=email_service
    )

    configure_users_dependencies(
        http_service=http_service,
        data_handling_service=data_handler
    )


    # multi domain # must configure single domain dependencies above this line #
    configure_employee_dependencies(http_service=http_service)





