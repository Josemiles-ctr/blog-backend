from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse

from src.presentation.api.routes import blogs_router

app = FastAPI(summary="My blog Backend Server")

app.include_router(blogs_router)

# Resolved from this file rather than the working directory, so serving the page
# does not depend on where uvicorn happened to be started.
INDEX_HTML = Path(__file__).parent / "src" / "presentation" / "api" / "static" / "index.html"


@app.get("/")
def welcome():
    return FileResponse(INDEX_HTML)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)