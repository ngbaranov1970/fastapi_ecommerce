from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.auth import get_current_seller

from app.schemas import Review as ReviewSchema, ReviewCreate
from app.db_depends import get_async_db
from app.service import update_product_rating

# Создаём маршрутизатор для отзывов
router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)

@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    """
    Создаёт новый отзыв, привязанный к текущему пользователю (только для 'buyer').
    После создания отзыва обновляет рейтинг товара.
    """
    # Проверяем, что товар существует и активен
    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == review.product_id, ProductModel.is_active == True)
    )
    if not product_result.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")
    
    if current_user.role != "buyer" or not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only buyers can create reviews")
    if review.grade < 1 or review.grade > 5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Rating must be between 1 and 5")
    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)  # Для получения id и is_active из базы

    # Обновляем рейтинг товара после добавления отзыва
    await update_product_rating(db, review.product_id)

    return db_review

@router.get("/", response_model=ReviewSchema)
async def get_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Получает список всех отзывов.
    """
    result = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))
    return result.all()