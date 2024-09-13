from db.base import Base
from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String, Table,
                        Text)
from sqlalchemy.orm import relationship, validates
from ulid import ULID


class UniquenessError(Exception): ...

def ulid() -> str:
    return str(ULID())

book_authors = Table('book_authors', Base.metadata,
    Column('book_id', String, ForeignKey('books.id'), primary_key=True),
    Column('author_name', String, ForeignKey('authors.name'), primary_key=True)
)

book_categories = Table('book_categories', Base.metadata,
    Column('book_id', String, ForeignKey('books.id'), primary_key=True),
    Column('category_name', String, ForeignKey('categories.name'), primary_key=True)
)

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(String, primary_key=True, default=ulid)
    google_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False, index=True)
    publisher = Column(String)
    publishedDate = Column(String)
    description = Column(Text)
    pageCount = Column(Integer)
    maturityRating = Column(String)
    smallThumbnail = Column(String)
    thumbnail = Column(String)
    language = Column(String, index=True)
    
    authors = relationship('Author', secondary=book_authors, back_populates='books')
    categories = relationship('Category', secondary=book_categories, back_populates='books')
    reviews = relationship('Review', back_populates='book')
     

class Author(Base):
    __tablename__ = 'authors'
    
    name = Column(String, primary_key=True)
    books = relationship('Book', secondary=book_authors, back_populates='authors')


class Category(Base):
    __tablename__ = 'categories'
    
    name = Column(String, primary_key=True)
    books = relationship('Book', secondary=book_categories, back_populates='categories')
    

class Review(Base):
    __tablename__ = 'review'
    
    id = Column(String, primary_key=True, default=ulid)
    user_id = Column(String, nullable=False, index=True)
    book_id = Column(String, ForeignKey('books.id'), nullable=False)
    book = relationship('Book', back_populates='reviews')
    stars = Column(Integer, nullable=False)
    comment = Column(Text)
    actual = Column(Boolean, nullable=False, default=True)
    
    @validates("stars")
    def validate_stars(self, key, stars):
        if not (stars >= 1 and stars <= 5):
            raise ValueError(f'Invalid number of stars ({stars})')
        return stars
