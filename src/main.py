from fastapi import FastAPI
from src.api import v1_router

app = FastAPI(root_path="/api")
app.include_router(v1_router)


@app.get("/health")
async def root():
    return {"message": "ok"}
