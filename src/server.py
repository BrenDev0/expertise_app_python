from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from  src.modules.agents import agents_routes
from src.modules.chats import chats_routes 
from src.modules.companies import companies_routes
from src.modules.documents import documents_routes
from src.modules.employees import employees_routes
from src.modules.interactions import interactions_routes
from src.modules.invites import invites_routes
from src.modules.chats.messages import messages_routes
from src.modules.chats.participants import participants_routes
from src.modules.users import users_routes
from src.core.dependencies.configure_container import configure_container
from src.core.middleware.hmac_verification import verify_hmac

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
    return {"status": "ok"}

app.add_middleware(verify_hmac)

app.include_router(agents_routes.router)
app.include_router(chats_routes.router)
app.include_router(companies_routes.router)
app.include_router(documents_routes.router)
app.include_router(employees_routes.router)
app.include_router(interactions_routes.router)
app.include_router(invites_routes.router)
app.include_router(messages_routes.router)
app.include_router(participants_routes.router)
app.include_router(users_routes.router)


