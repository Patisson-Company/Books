from typing import Optional

from api.graphql._selected_fields import selected_fields
from api.graphql._stmt_filters import Stmt
from ariadne import QueryType
from db.models import Author, Book, Category
from graphql import GraphQLResolveInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

query = QueryType()


@query.field("books")
async def books(_, info: GraphQLResolveInfo, 
                id: Optional[list[str]] = None,
                publisher: Optional[list[str]] = None, 
                exact_publishedDate: Optional[str] = None,
                from_publishedDate: Optional[str] = None,
                before_publishedDate: Optional[str] = None,
                exact_pageCount: Optional[int] = None,
                from_pageCount: Optional[int] = None,
                before_pageCount: Optional[int] = None,
                maturityRaiting: Optional[str] = None,
                language: Optional[list[str]] = None,
                limit: Optional[int] = 10):
    db: AsyncSession = info.context["db"]
    stmt = (
        Stmt(
            select(*selected_fields(info, Book))
            )
        .con_filter(Book.id, id)
        .con_filter(Book.publisher, publisher)
        .eq_filter(Book.publishedDate, exact_publishedDate)
        .gte_filter(Book.publishedDate, from_publishedDate)
        .lte_filter(Book.publishedDate, before_publishedDate)
        .eq_filter(Book.pageCount, exact_pageCount)
        .gte_filter(Book.pageCount, from_pageCount)
        .lte_filter(Book.pageCount, before_pageCount)
        .eq_filter(Book.maturityRating, maturityRaiting)
        .con_filter(Book.language, language)
        .limit(limit)
    )
    result = await db.execute(stmt())
    return result.fetchall()


@query.field("booksDeep")
async def books_deep(_, info: GraphQLResolveInfo, 
                ids: Optional[list[str]] = None,
                publishers: Optional[list[str]] = None, 
                exact_publishedDate: Optional[str] = None,
                from_publishedDate: Optional[str] = None,
                before_publishedDate: Optional[str] = None,
                exact_pageCount: Optional[int] = None,
                from_pageCount: Optional[int] = None,
                before_pageCount: Optional[int] = None,
                maturityRaiting: Optional[str] = None,
                languages: Optional[list[str]] = None,
                authors: Optional[list[str]] = None,
                categories: Optional[list[str]] = None,
                limit: Optional[int] = 10):
    db: AsyncSession = info.context["db"]
    stmt = (
        Stmt(
            select(Book)
            .options(
                joinedload(Book.authors),
                joinedload(Book.categories)
                )
            )
        .con_filter(Book.id, ids)
        .con_filter(Book.publisher, publishers)
        .eq_filter(Book.publishedDate, exact_publishedDate)
        .gte_filter(Book.publishedDate, from_publishedDate)
        .lte_filter(Book.publishedDate, before_publishedDate)
        .eq_filter(Book.pageCount, exact_pageCount)
        .gte_filter(Book.pageCount, from_pageCount)
        .lte_filter(Book.pageCount, before_pageCount)
        .eq_filter(Book.maturityRating, maturityRaiting)
        .con_filter(Book.language, languages)
        .con_model_filter(Book.authors, authors)
        .con_model_filter(Book.categories, categories)
        .limit(limit)
    )
    result = await db.execute(stmt())
    return result.scalars().unique().all()


@query.field("authors")
async def authors(_, info: GraphQLResolveInfo,
                  names: Optional[list[str]] = None,
                  limit: Optional[int] = 10):
    db: AsyncSession = info.context["db"]
    stmt = (
        Stmt(
            select(Author)
            .options(
                joinedload(Author.books)
                )
            )
        .con_filter(Author.name, names)
        .limit(limit)
    )
    result = await db.execute(stmt())
    return result.scalars().unique().all()


@query.field("categories")
async def categories(_, info: GraphQLResolveInfo,
                  names: Optional[list[str]] = None,
                  limit: Optional[int] = 10):
    db: AsyncSession = info.context["db"]
    stmt = (
        Stmt(
            select(Category)
            .options(
                joinedload(Category.books)
                )
            )
        .con_filter(Category.name, names)
        .limit(limit)
    )
    result = await db.execute(stmt())
    return result.scalars().unique().all()


resolvers = [query]