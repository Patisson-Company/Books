import asyncio
import string
from asyncio import Queue
from itertools import chain

import aiohttp
from db.base import get_session
from db.models import *
from sqlalchemy.ext.asyncio import AsyncSession

URL = "https://www.googleapis.com/books/v1/volumes?q={}"


async def add_author(session: AsyncSession, name: str):
    author = await session.get(Author, name)
    if not author:
        author = Author(name=name)
        session.add(author)
        await session.commit()
    return author


async def add_category(session: AsyncSession, name: str):
    category = await session.get(Category, name)
    if not category:
        category = Category(name=name)
        session.add(category)
        await session.commit()
    return category


async def add_book(session: AsyncSession, book_data: dict):
    volume_info = book_data.get("volumeInfo", {})
    book_id = book_data.get("id")
    existing_book = await session.get(Book, book_id)
    if existing_book:
        return

    book = Book(
        id=book_id,
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
        author = await add_author(session, author_name)
        book.authors.append(author)
    
    for category_name in volume_info.get("categories", []):
        category = await add_category(session, category_name)
        book.categories.append(category)
    
    session.add(book)
    await session.commit()


async def fetch_books_data(session: aiohttp.ClientSession, query: str):
    books_data = []
    async with session.get(URL.format(query)) as response:
        if response.status == 200:
            result = await response.json()
            if 'items' in result:
                books_data.extend(result['items'])
    return books_data


async def process_query(query: str, queue: Queue):
    async with aiohttp.ClientSession() as client_session:
        books_data = await fetch_books_data(client_session, query)
        for book_data in books_data:
            await queue.put(book_data)
            
            
async def add_books_to_db(queue: Queue):
    async with get_session() as session:
        while True:
            book_data = await queue.get()
            if book_data is None: 
                break
            await add_book(session, book_data)
            queue.task_done()


async def main(queries: list[str]):
    queue = Queue()
    
    tasks = [process_query(query, queue) for query in queries]
    db_task = asyncio.create_task(add_books_to_db(queue))
    await asyncio.gather(*tasks)

    await queue.put(None)  # the requests are finished
    await db_task


if __name__ == "__main__":
    english_alphabet = string.ascii_lowercase
    russian_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя'
    queries = list(chain(english_alphabet, russian_alphabet))
    asyncio.run(main(queries))