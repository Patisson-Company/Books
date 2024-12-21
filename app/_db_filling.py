import asyncio
import random
import string
from asyncio import Queue
from itertools import chain
from typing import Optional, Sequence

import httpx
from config import SelfService
from db.base import get_session
from db.models import Author, Book, Category, Review
from faker import Faker
from patisson_request.graphql.queries import QUser
from patisson_request.service_routes import UsersRoute
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

URL = "https://www.googleapis.com/books/v1/volumes?q={}"
fake = Faker()


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


async def _add_review(user_id: str, book_id: str, stars: int,
                      comment: str, actual: bool = True) -> Review:
    async with get_session() as session:
        review = Review(
            user_id=user_id,
            book_id=book_id,
            stars=stars,
            comment=comment,
            actual=actual
        )
        session.add(review)
        await session.commit()
        return review


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


async def _filling_review(session: Optional[AsyncSession] = None):
    async def body(session: AsyncSession):
        users = await SelfService.post_request(
            *-UsersRoute.graphql.users(fields=[QUser.id], limit=0)
        )
        result = await session.execute(select(Book.id))
        books = result.scalars().unique().all()

        tasks = [
            _add_review(
                user_id=user.id,
                book_id=random.choice(books),
                stars=random.randint(1, 5),
                comment=fake.text(),
                actual=True if random.randint(1, 10) > 8 else False
            )
            for user in users.body.data.users if random.randint(0, 1) != 0
            for _ in range(random.randint(1, 5))
        ]

        await asyncio.gather(*tasks)

    if session:
        await body(session)
    else:
        async with get_session() as session:
            await body(session)


async def filling_db(queries: Sequence[str], session: Optional[AsyncSession] = None):
    queue = Queue()
    tasks = [_process_query(query, queue) for query in queries]
    db_task = asyncio.create_task(_add_books_to_db(queue, session))

    await asyncio.gather(*tasks)
    await queue.put(None)  # the requests are finished
    await db_task


async def main(queries: Sequence):
    await filling_db(queries)
    await _adding_books_by_authors()
    await _adding_books_by_categories()
    await _filling_review()


if __name__ == "__main__":
    english_alphabet = string.ascii_lowercase
    russian_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя'
    numbers = '0123456789'
    queries = list(chain(english_alphabet, russian_alphabet, numbers))
    asyncio.run(main(queries))
