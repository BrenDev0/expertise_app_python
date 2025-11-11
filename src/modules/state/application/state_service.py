from uuid import UUID

from src.core.utils.decorators.service_error_handler import service_error_handler
from src.core.domain.repositories.session_respository import SessionRepository

from src.modules.state.domain.state_models import WorkerState
from src.modules.chats.domain.messages_models import MessagePublic
from src.modules.chats.domain.entities import Message
from src.modules.chats.application.messages_service import MessagesService

class StateService: 
    __MODULE = "state.service"
    __NUM_OF_MESSAGES = 16
    def __init__(self, repository: SessionRepository, messages_service: MessagesService):
        self.__repository = repository
        self.__messages_service = messages_service


    @service_error_handler(f"{__MODULE}.update_chat_state_history")
    def update_chat_state_history(
        self,
        chat_id: UUID,
        message: Message,
        num_of_messages: int = __NUM_OF_MESSAGES,
    ):
        session_key = self.__get_chat_state_key(chat_id=chat_id)
        
        session_data = self.__repository.get_session(session_key)

        if session_data:
            state = WorkerState(
                **session_data
            )
            
            chat_history = state.chat_history
            if message.text:
                chat_history.insert(0,  MessagePublic.model_validate(
                    message, 
                    from_attributes=True, by_name=True).model_dump(exclude={"chat_id", "sender", "message_id"}, by_alias=False)
                )

                if len(chat_history) > num_of_messages:
                    chat_history.pop()  

            
            self.__repository.set_session(session_key, state.model_dump_json(), expire_seconds=7200) #2 hours 

    @service_error_handler(f"{__MODULE}.ensure_chat_state")
    def ensure_chat_state(self, chat_id: UUID, input: str, user_id: UUID, company_id: UUID, voice: bool = False) -> WorkerState:
        session_key = self.__get_chat_state_key(chat_id=chat_id)
        session = self.__repository.get_session(session_key)
        if session:
            state = WorkerState(**session)
            state.input = input
            return state
        
        # Not found: build from DB
        chat_history = self.__messages_service.collection(key="chat_id", value=chat_id, num_of_messages=self.__NUM_OF_MESSAGES)
        state = WorkerState(
            input=input,
            chat_id=str(chat_id), 
            chat_history=[
                MessagePublic.model_validate(
                    msg, 
                    from_attributes=True, 
                    by_name=True).model_dump(exclude={"chat_id", "sender", "message_id"}, by_alias=False) 
                    for msg in chat_history if msg.text
            ],
            user_id=str(user_id),
            company_id=str(company_id),
            voice=voice
        )

        self.__repository.set_session(session_key, state.model_dump_json(), expire_seconds=7200) #2 hours 
        return state
    
    @staticmethod
    def __get_chat_state_key(chat_id: UUID):
        return f"chat_session:{chat_id}"