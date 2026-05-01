from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship  # New
from sqlalchemy import ForeignKey

from app.database import Base

if TYPE_CHECKING:
    from app.models.products import Product
    from app.models.users import User

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    comment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)  # New
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)  # New

    product: Mapped["Product"] = relationship("Product", back_populates="reviews")  # New
    user: Mapped["User"] = relationship("User", back_populates="reviews")  # New