from fastapi import FastAPI

from app.routers import categories

app = FastAPI()

app.include_router(categories.router)

# Run the application using: uvicorn app.main:app --reload
