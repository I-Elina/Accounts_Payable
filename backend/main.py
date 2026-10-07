from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.errors import ApiError, api_error_handler
from backend.routers import (
    audit,
    chat,
    config_api,
    health,
    invoices,
    report,
    reviews,
    stats,
    uploads,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and schema on startup
    init_db()
    yield


app = FastAPI(
    title="Cache Me If You Can API",
    description="Accounts Payable Exception Pile Assistant Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware (Frontend runs on port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom ApiError Handler
app.add_exception_handler(ApiError, api_error_handler)

# Include Routers
app.include_router(health.router)
app.include_router(uploads.router)
app.include_router(invoices.router)
app.include_router(reviews.router)
app.include_router(stats.router)
app.include_router(audit.router)
app.include_router(chat.router)
app.include_router(report.router)
app.include_router(config_api.router)


@app.get("/")
def root():
    return {
        "message": "Cache Me If You Can Backend API is live",
        "docs": "/docs",
        "health": "/api/health",
    }
