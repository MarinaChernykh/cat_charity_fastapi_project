from sqlalchemy import Column, String, Text

from .charity_abstract_base import CharityAbstractBase


class CharityProject(CharityAbstractBase):
    """Содержит информацию о благотворительных проектах."""
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.__class__.__name__}: {self.name}'
