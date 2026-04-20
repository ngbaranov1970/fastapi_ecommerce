from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_async_db

# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех товаров.
    """
    stmt = await db.scalars(select(ProductModel).where(ProductModel.is_active))
    products = stmt.all()
    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт новый товар.
    """
    # Проверка существования категории
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active)
    category = await db.scalars(stmt)
    category = category.first()
    if category is None:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    # Создание нового товара
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product
 


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    stmt_category = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active)
    category = await db.scalars(stmt_category)
    category = category.first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")

    stmt = select(ProductModel).where(ProductModel.category_id == category_id, ProductModel.is_active)
    products = await db.scalars(stmt)
    return products.all()


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    stmt_product = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active)
    product = await db.scalars(stmt_product)
    product = product.first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")
  
    return product


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет товар по его ID.
    """
    stmt_product = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active)
    db_product = await db.scalars(stmt_product)
    db_product = db_product.first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")
    
    stmt_category = select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active)
    category = await db.scalars(stmt_category)
    category = category.first()
    if category is None:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump())
    )

    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Удаляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active)
    db_product = await db.scalars(stmt)
    db_product = db_product.first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(is_active=False)
    )
    await db.commit()
    return {"status": "success", "message": "Product marked as inactive"}