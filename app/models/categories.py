from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship  # New

from app.database import Base

if TYPE_CHECKING:
    from app.models.products import Product

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")  # New
    parent: Mapped["Category | None"] = relationship("Category", back_populates="children", remote_side="Category.id")
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")