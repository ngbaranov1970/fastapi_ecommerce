from fastapi import FastAPI

from app.routers import categories, products, users, reviews 
 
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в API интернет-магазина!"}

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)


