from src.modules.state.state_models import ChatState
from src.core.services.redis_service import RedisService
from src.modules.chats.messages.messages_models import MessageCreate
from src.modules.chats.messages.messages_service import MessagesService
from  sqlalchemy.orm import Session
from uuid import UUID

class StateService: 
    __NUM_OF_MESSAGES = 16
    def __init__(self, redis_service: RedisService, messages_service: MessagesService):
        self.__redis_service = redis_service
        self.__messages_service = messages_service


    async def update_chat_state_history(self, state: ChatState, incoming_message: MessageCreate, outgoing_message: MessageCreate, num_of_messages: int = __NUM_OF_MESSAGES):
        session_key = self.__redis_service.get_agent_state_key(chat_id=incoming_message.chat_id)
        
        chat_history = state.chat_history

        chat_history.insert(0, incoming_message.model_dump(exclude="chat_id"))
        if len(chat_history) > num_of_messages:
            chat_history.pop()  

        chat_history.insert(0, outgoing_message.model_dump(exclude="chat_id"))
        if len(chat_history) > num_of_messages:
            chat_history.pop()  
        
        await self.__redis_service.set_session(session_key, state.model_dump(), expire_seconds=7200) #2 hours 

    
    async def ensure_chat_state(self, db: Session, chat_id: UUID, input: str, user_id: UUID, agent_id: UUID) -> ChatState:
        session_key = f"chat_session:{chat_id}"
        session = await self.__redis_service.get_session(session_key)
        if session:
            return ChatState(**session)
        
        # Not found: build from DB
        chat_history = self.__messages_service.collection(db, chat_id, num_of_messages=self.__NUM_OF_MESSAGES)
        state = ChatState(
            input=input,
            chat_id=chat_id, 
            chat_history=[msg.model_dump(exclude="chat_id") for msg in chat_history],
            user_id=user_id,
            agent_id=agent_id
        )

        await self.__redis_service.set_session(session_key, state.model_dump())
        return state