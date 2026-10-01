from fastapi import FastAPI
import uvicorn

from src.infrastructure.database.session import init_db
from src.presentation.api.routes import blogs_router

app = FastAPI(summary="My blog Backend Server")

init_db()

app.include_router(blogs_router)


@app.get("/")
def welcome():
    return {"message": "Welcome, The Server is Running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)