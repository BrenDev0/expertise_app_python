from src.core.dependencies.container import Container
from src.modules.interactions.interactions_controller import InteractionsController
from src.modules.interactions.interactions_service import InteractionsService
from src.core.services.http_service import HttpService



def configure_interactions_dependencies(http_service):
    service = InteractionsService()
    
    messaging_service = Container.resolve("messages_service")
    state_service = Container.resolve("state_service")
    
    controller = InteractionsController(
        http_service=http_service,
        interactions_service=service,
        messaging_service=messaging_service,
        state_service=state_service
    )

    Container.register("interactions_service", service)
    Container.register("interactions_controller", controller)