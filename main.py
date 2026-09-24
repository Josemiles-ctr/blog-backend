from fastapi import FastAPI
import uvicorn

app = FastAPI(summary="My blog Backend Server")

@app.get("/")
def welcome():
    return {"message": "Welcome, The Server is Running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    