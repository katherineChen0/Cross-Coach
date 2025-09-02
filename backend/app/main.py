from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.routes import api_router
from .db import engine
from .models import Base
from .core.scheduler import scheduler

app = FastAPI(title="CrossCoach API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # Start the background scheduler
    scheduler.start()

@app.on_event("shutdown")
def on_shutdown():
    # Shutdown the background scheduler
    scheduler.shutdown()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api") 