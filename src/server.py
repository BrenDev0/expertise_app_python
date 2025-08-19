from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from  src.modules.agents import agents_routes
from src.modules.companies import companies_routes
from src.modules.employees import employees_routes
from src.modules.invites import invites_routes
from src.modules.users import users_routes
from src.core.dependencies.configure_container import configure_container

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

app.include_router(agents_routes.router)
app.include_router(companies_routes.router)
app.include_router(employees_routes.router)
app.include_router(invites_routes.router)
app.include_router(users_routes.router)


