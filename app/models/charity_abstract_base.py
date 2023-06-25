from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime, CheckConstraint

from app.core.db import Base


class CharityAbstractBase(Base):
    """Абстрактный класс-основа для моделей CharityProject и Donation."""
    __abstract__ = True
    __table_args__ = (
        CheckConstraint(
            'full_amount >= invested_amount', name='amount_ge_invested'
        ),
        CheckConstraint(
            'full_amount >= 1', name='check_amount_positive'
        ),
    )

    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.utcnow)
    close_date = Column(DateTime, nullable=True)
