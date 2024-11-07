import asyncio
import string
from asyncio import Queue
from itertools import chain
from typing import Optional, Sequence

import httpx
from db.base import get_session
from db.models import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from config import SelfService

URL = "https://www.googleapis.com/books/v1/volumes?q={}"


async def _add_author(session: AsyncSession, name: str):
    author = await session.get(Author, name)
    if not author:
        author = Author(name=name)
        session.add(author)
        await session.commit()
    return author


async def _add_category(session: AsyncSession, name: str):
    category = await session.get(Category, name)
    if not category:
        category = Category(name=name)
        session.add(category)
        await session.commit()
    return category


async def _add_book(session: AsyncSession, book_data: dict):
    try:
        volume_info: dict = book_data.get("volumeInfo", {})
        book_id = book_data.get("id")
        existing_book = await session.execute(select(Book).filter_by(google_id=book_id))
        if existing_book.scalars().first():
            return

        book = Book(
            google_id=book_id,
            title=volume_info.get("title"),
            publisher=volume_info.get("publisher"),
            publishedDate=volume_info.get("publishedDate"),
            description=volume_info.get("description"),
            pageCount=volume_info.get("pageCount"),
            maturityRating=volume_info.get("maturityRating"),
            smallThumbnail=volume_info.get("imageLinks", {}).get("smallThumbnail"),
            thumbnail=volume_info.get("imageLinks", {}).get("thumbnail"),
            language=volume_info.get("language")
        )
        
        for author_name in volume_info.get("authors", []):
            author = await _add_author(session, author_name)
            book.authors.append(author)
        
        for category_name in volume_info.get("categories", []):
            category = await _add_category(session, category_name)
            book.categories.append(category)
        
        session.add(book)
        
        await session.commit()
    except IntegrityError:
        pass


async def _fetch_books_data(client: httpx.AsyncClient, query: str):
    books_data = []
    response = await client.get(URL.format(query))
    if response.status_code == 200:
        result = response.json()
        if 'items' in result:
            books_data.extend(result['items'])
    return books_data


async def _process_query(query: str, queue: Queue) -> None:
    async with httpx.AsyncClient() as client:
        books_data = await _fetch_books_data(client, query)
        for book_data in books_data:
            await queue.put(book_data)
            
            
async def _add_books_to_db(queue: Queue, session: Optional[AsyncSession] = None):
    async def body(session: AsyncSession):
        while True:
            book_data = await queue.get()
            if book_data is None: 
                break
            await _add_book(session, book_data)
            queue.task_done()
            
    if session:
        await body(session)  
    else:
        async with get_session() as session:
            await body(session)


async def _adding_books_by_authors(session: Optional[AsyncSession] = None):
    async with get_session() as session:
        result = await session.execute(select(Author.name))
        authors = result.scalars().unique().all()
        await filling_db([f'inauthor:{author}' for author in authors])
        

async def _adding_books_by_categories(session: Optional[AsyncSession] = None):
    async with get_session() as session:
        result = await session.execute(select(Category.name))
        categories = result.scalars().unique().all()
        await filling_db([f'subject:{category}' for category in categories])
        

async def filling_db(queries: Sequence[str], session: Optional[AsyncSession] = None):
    queue = Queue()
    tasks = [_process_query(query, queue) for query in queries]
    db_task = asyncio.create_task(_add_books_to_db(queue, session))
    
    await asyncio.gather(*tasks)
    await queue.put(None)  # the requests are finished
    await db_task


async def filling_review(session: Optional[AsyncSession] = None):
    async def body(session: AsyncSession):
        ...
            
    if session:
        await body(session)  
    else:
        async with get_session() as session:
            await body(session)


async def main(queries: Sequence):
    await filling_db(queries)
    await _adding_books_by_authors()
    await _adding_books_by_categories()
    await filling_review()
    
    
if __name__ == "__main__":
    english_alphabet = string.ascii_lowercase
    russian_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя'
    numbers = '0123456789'
    queries = list(chain(english_alphabet, russian_alphabet, numbers))
    asyncio.run(main(queries))
    