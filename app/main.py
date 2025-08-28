from fastapi import FastAPI
from app.routers import content
from app.routers import frequency
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "message": "Error",
            "data": None,
            "error": True,
            "error_message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "page": None,
            "limit": None,
            "total": None
        }
    )

app.include_router(content.router)
app.include_router(frequency.router)


@app.get("/")
def root():
    return {"message": "Hello World!"}
