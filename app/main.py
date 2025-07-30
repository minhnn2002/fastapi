from fastapi import FastAPI
from app.routers import content
from app.routers import frequency

app = FastAPI()

app.include_router(content.router)
# app.include_router(without_content.router)


@app.get("/")
def root():
    return {"message": "Hello World!"}
