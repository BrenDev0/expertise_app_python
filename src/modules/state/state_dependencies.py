from  src.core.dependencies.container import Container
from src.modules.state.state_service import StateService
from src.core.services.redis_service import RedisService

def configure_state_dependencies(redis_service: RedisService):
    messages_service = Container.resolve("messages_service")
    service = StateService(
        redis_service=redis_service,
        messages_service=messages_service
    )

    Container.register("state_service", service)