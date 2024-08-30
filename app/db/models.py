from db.base import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

book_authors = Table('book_authors', Base.metadata,
    Column('book_id', String, ForeignKey('books.id'), primary_key=True),
    Column('author', String, ForeignKey('authors.name'), primary_key=True)
)

book_categories = Table('book_categories', Base.metadata,
    Column('book_id', String, ForeignKey('books.id'), primary_key=True),
    Column('category', String, ForeignKey('categories.name'), primary_key=True)
)

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False, index=True)
    authors = relationship('Author', secondary=book_authors, back_populates='books')
    publisher = Column(String, nullable=False)
    publishedDate = Column(String, nullable=False)
    description = Column(Text)
    pageCount = Column(Integer)
    categories = relationship('Category', secondary=book_authors, back_populates='books')
    maturityRating = Column(String)
    smallThumbnail = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
    language = Column(String, nullable=False, index=True)
    
    
class Author(Base):
    __tablename__ = 'authors'
    
    name = Column(String, primary_key=True)
    books = relationship('Book', secondary=book_authors, back_populates='authors')
    

class Category(Base):
    __tablename__ = 'categories'
    
    name = Column(String, primary_key=True)
    books = relationship('Book', secondary=book_categories, back_populates='authors')