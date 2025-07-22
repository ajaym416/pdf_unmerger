from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.storage import create_bucket
from app.core.config import settings

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    #conly for testing change this on production
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
def on_startup():
    try:
        create_bucket(settings.s3_bucket)
    except:
        pass
    
