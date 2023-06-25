from sqlalchemy import Column, Integer, ForeignKey, Text

from .charity_abstract_base import CharityAbstractBase


class Donation(CharityAbstractBase):
    """Содержит информацию о пожертвованиях."""
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)

    def __str__(self):
        return f'{self.full_amount} - {self.create_date}'

    def __repr__(self):
        return (
            f'{self.__class__.__name__}: '
            f'{self.full_amount} - {self.create_date}'
        )
