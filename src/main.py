from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from errors.domain_errors import DomainError
from routes.analyze.analyze_routes import router as analyze_router
from routes.chat.chat_routes import router as chat_router
from routes.payment.payment_routes import router as payment_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(payment_router)
app.include_router(chat_router)


@app.exception_handler(DomainError)
async def domain_error_handler(
    request: Request,
    exc: DomainError,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.get("/")
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "message": "Intelligent text analyis API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
