from fastapi import FastAPI

from app.routers import categories
from app.routers import products

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в API интернет-магазина!"}

app.include_router(categories.router)
app.include_router(products.router)



