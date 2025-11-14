from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.modules.agents.interface import agents_routes
from src.modules.chats.interface import chats_routes 
from src.modules.companies.interface import companies_routes
from src.modules.documents.interface import documents_routes
from src.modules.employees.interface import employees_routes
from src.modules.interactions.interface import interactions_routes
from src.modules.invites.interface import invites_routes
from src.modules.chats.interface import messages_routes
from src.modules.users.interface import users_routes
from src.core.dependencies.configure_container import configure_container

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger("httpx").setLevel(logging.WARNING) 
logging.getLogger("httpcore").setLevel(logging.WARNING) 

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_container()  
    yield

app = FastAPI(lifespan=lifespan)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://expertise-ai-tan.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Internal"])
async def health():
    """
    ## Health check 
    This endpoints verifies server status.
    """
    return {"status": "expertise ok"}

app.include_router(agents_routes.router)
app.include_router(chats_routes.router)
app.include_router(companies_routes.router)
app.include_router(documents_routes.router)
app.include_router(employees_routes.router)
app.include_router(interactions_routes.router)
app.include_router(invites_routes.router)
app.include_router(messages_routes.router)
app.include_router(users_routes.router)


