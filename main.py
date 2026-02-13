from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.organizations import router


app = FastAPI(
    title="TEST REST API",
    description="Справочник организаций с геопоиском и древовидным каталогом деятельности",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "TEST REST API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
