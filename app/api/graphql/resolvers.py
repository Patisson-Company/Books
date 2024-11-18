from typing import Optional

from _db_filling import filling_db
from ariadne import MutationType, QueryType
from config import logger
from db.models import Author, Book, Category, Review
from graphql import GraphQLResolveInfo
from patisson_graphql.selected_fields import selected_fields
from patisson_graphql.stmt_filter import Stmt
from patisson_request.errors import (ErrorCode, ErrorSchema, UniquenessError,
                                     ValidateError)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

query = QueryType()
mutation = MutationType()


@query.field("books")
async def books(_, info: GraphQLResolveInfo, 
                ids: Optional[list[str]] = None,
                titles: Optional[list[str]] = None,
                like_title: Optional[str] = None,
                publishers: Optional[list[str]] = None, 
                exact_publishedDate: Optional[str] = None,
                from_publishedDate: Optional[str] = None,
                before_publishedDate: Optional[str] = None,
                like_description: Optional[str] = None,
                exact_pageCount: Optional[int] = None,
                from_pageCount: Optional[int] = None,
                before_pageCount: Optional[int] = None,
                maturityRaiting: Optional[str] = None,
                languages: Optional[list[str]] = None,
                offset: Optional[int] = None,
                limit: Optional[int] = 10,
                search: Optional[list[str]] = None):
    db: AsyncSession = info.context["db"]
    if search: await filling_db(search, db)
    stmt = (
        Stmt(
            select(*selected_fields(info, Book))
            )
        .con_filter(Book.id, ids)
        .con_filter(Book.title, titles)
        .like_filter(Book.title, like_title)
        .con_filter(Book.publisher, publishers)
        .eq_filter(Book.publishedDate, exact_publishedDate)
        .gte_filter(Book.publishedDate, from_publishedDate)
        .lte_filter(Book.publishedDate, before_publishedDate)
        .like_filter(Book.description, like_description)
        .eq_filter(Book.pageCount, exact_pageCount)
        .gte_filter(Book.pageCount, from_pageCount)
        .lte_filter(Book.pageCount, before_pageCount)
        .eq_filter(Book.maturityRating, maturityRaiting)
        .con_filter(Book.language, languages)
        .offset(offset).limit(limit).ordered_by(Book.id)
    )
    logger.info(stmt.log())
    result = await db.execute(stmt())
    return result.fetchall()


@query.field("booksDeep")
async def books_deep(_, info: GraphQLResolveInfo, 
                ids: Optional[list[str]] = None,
                titles: Optional[list[str]] = None,
                like_title: Optional[str] = None,
                publishers: Optional[list[str]] = None, 
                exact_publishedDate: Optional[str] = None,
                from_publishedDate: Optional[str] = None,
                before_publishedDate: Optional[str] = None,
                like_description: Optional[str] = None,
                exact_pageCount: Optional[int] = None,
                from_pageCount: Optional[int] = None,
                before_pageCount: Optional[int] = None,
                maturityRaiting: Optional[str] = None,
                languages: Optional[list[str]] = None,
                authors: Optional[list[str]] = None,
                categories: Optional[list[str]] = None,
                offset: Optional[int] = None,
                limit: Optional[int] = 10,
                search: Optional[list[str]] = None):
    db: AsyncSession = info.context["db"]
    if search: await filling_db(search, db)
    stmt = (
        Stmt(
            select(Book)
            .options(
                joinedload(Book.authors),
                joinedload(Book.categories)
                )
            )
        .con_filter(Book.id, ids)
        .con_filter(Book.title, titles)
        .like_filter(Book.title, like_title)
        .con_filter(Book.publisher, publishers)
        .eq_filter(Book.publishedDate, exact_publishedDate)
        .gte_filter(Book.publishedDate, from_publishedDate)
        .lte_filter(Book.publishedDate, before_publishedDate)
        .like_filter(Book.description, like_description)
        .eq_filter(Book.pageCount, exact_pageCount)
        .gte_filter(Book.pageCount, from_pageCount)
        .lte_filter(Book.pageCount, before_pageCount)
        .eq_filter(Book.maturityRating, maturityRaiting)
        .con_filter(Book.language, languages)
        .con_model_filter(Book.authors, authors)
        .con_model_filter(Book.categories, categories)
        .offset(offset).limit(limit).ordered_by(Book.id)
    )
    logger.info(stmt.log())
    result = await db.execute(stmt())
    return result.scalars().unique().all()


@query.field("authors")
async def authors(_, info: GraphQLResolveInfo,
                  names: Optional[list[str]] = None,
                  like_names: Optional[str] = None,
                  offset: Optional[int] = None,
                  limit: Optional[int] = 10,
                  search: Optional[list[str]] = None):
    db: AsyncSession = info.context["db"]
    if search: await filling_db(search, db)
    stmt = (
        Stmt(
            select(Author)
            .options(
                joinedload(Author.books)
                )
            )
        .con_filter(Author.name, names)
        .like_filter(Author.name, like_names)
        .offset(offset).limit(limit).ordered_by(Book.id)
    )
    logger.info(stmt.log())
    result = await db.execute(stmt())
    return result.scalars().unique().all()


@query.field("categories")
async def categories(_, info: GraphQLResolveInfo,
                  names: Optional[list[str]] = None,
                  like_name: Optional[str] = None,
                  offset: Optional[int] = None,
                  limit: Optional[int] = 10,
                  search: Optional[list[str]] = None):
    db: AsyncSession = info.context["db"]
    if search: await filling_db(search, db)
    stmt = (
        Stmt(
            select(Category)
            .options(
                joinedload(Category.books)
                )
            )
        .con_filter(Category.name, names)
        .like_filter(Author.name, like_name)
        .offset(offset).limit(limit).ordered_by(Book.id)
    )
    logger.info(stmt.log())
    result = await db.execute(stmt())
    return result.scalars().unique().all()


@query.field("reviews")
async def reviews(_, info: GraphQLResolveInfo, 
                ids: Optional[list[str]] = None,
                user_ids: Optional[list[str]] = None,
                from_stars: Optional[int] = None,
                before_stars: Optional[int] = None,
                comment: Optional[str] = None,
                actual: Optional[bool] = True,
                offset: Optional[int] = None,
                limit: Optional[int] = 10):
    db: AsyncSession = info.context["db"]
    stmt = (
        Stmt(
            select(*selected_fields(info, Review))
            )
        .con_filter(Review.id, ids)
        .con_filter(Review.user_id, user_ids)
        .gte_filter(Review.stars, from_stars)
        .lte_filter(Review.stars, before_stars)
        .like_filter(Review.comment, comment)
        .con_filter(Review.actual, [actual])
        .offset(offset).limit(limit).ordered_by(Book.id)
    )
    logger.info(stmt.log())
    result = await db.execute(stmt())
    return result.fetchall()


@query.field("reviewsDeep")
async def reviews_deep(_, info: GraphQLResolveInfo, 
                ids: Optional[list[str]] = None,
                user_ids: Optional[list[str]] = None,
                from_stars: Optional[int] = None,
                before_stars: Optional[int] = None,
                comment: Optional[str] = None,
                books: Optional[list[str]] = None,
                actual: Optional[bool] = True,
                offset: Optional[int] = None,
                limit: Optional[int] = 10):
    db: AsyncSession = info.context["db"]
    stmt = (
        Stmt(
            select(Review)
            )
        .con_filter(Review.id, ids)
        .con_filter(Review.user_id, user_ids)
        .gte_filter(Review.stars, from_stars)
        .lte_filter(Review.stars, before_stars)
        .like_filter(Review.comment, comment)
        .con_model_filter(Review.book, books)
        .con_filter(Review.actual, [actual])
        .offset(offset).limit(limit).ordered_by(Book.id)
    )
    logger.info(stmt.log())
    result = await db.execute(stmt())
    return result.scalars().unique().all()


@mutation.field("createReview")
async def create_review(_, info: GraphQLResolveInfo, 
                        user_id: str, book_id: str, stars: int, 
                        comment: Optional[str] = None):
    db: AsyncSession = info.context["db"]
    try:
        new_review = Review(user_id=user_id, book_id=book_id, 
                            stars=stars, comment=comment)
        
        # checking the uniqueness of the review
        stmt = (
            Stmt(
                select(Review)
                )
            .con_filter(Review.user_id, [user_id])
            .con_filter(Review.book_id, [book_id])
            .con_filter(Review.actual, [True])
        )
        result = await db.execute(stmt())
        if result.scalars().all():
            raise UniquenessError
        
        logger.info(stmt.log())
        db.add(new_review)
        await db.commit()
        return {"success": True}
    
    except IntegrityError:
        await db.rollback()
        error = ErrorSchema(
            error=ErrorCode.INVALID_PARAMETERS,
            extra=f'The book ({book_id}) was not found'
        )
        logger.info(error)
        return {"success": False, 
                "errors": error.model_dump()}
        
    except SQLAlchemyError as e:
        await db.rollback()
        error = ErrorSchema(
            error=ErrorCode.INVALID_PARAMETERS,
            extra=str(e)
        )
        logger.info(error)
        return {"success": False, "errors": error.model_dump()}

    except UniquenessError:
        error = ErrorSchema(
            error=ErrorCode.INVALID_PARAMETERS,
            extra=f'a review on this book ({book_id}) from this user ({user_id}) already exists'
        )
        logger.info(error)
        return {"success": False, "errors": error.model_dump()}

    except ValidateError as e:
        error = ErrorSchema(
            error=ErrorCode.VALIDATE_ERROR,
            extra=str(e)
        )
        logger.info(error)
        return {"success": False, "errors": error.model_dump()}
        

@mutation.field("updateReview")
async def update_review(_, info: GraphQLResolveInfo, 
                        user_id: str, book_id: str, stars: int, 
                        comment: Optional[str] = None):
    db: AsyncSession = info.context["db"]
    try:
        new_review = Review(user_id=user_id, book_id=book_id, 
                            stars=stars, comment=comment)
        
        stmt = (
            Stmt(
                select(Review)
                )
            .con_filter(Review.user_id, [user_id])
            .con_filter(Review.book_id, [book_id])
            .con_filter(Review.actual, [True])
        )
        result = await db.execute(stmt())
        not_actual_review = result.scalar_one_or_none()
        if not not_actual_review:
            raise UniquenessError
        not_actual_review.actual = False
        
        db.add(new_review)        
        await db.commit()
        return {"success": True}
    
    except IntegrityError:
        await db.rollback()
        error = ErrorSchema(
            error=ErrorCode.INVALID_PARAMETERS,
            extra=f'The book ({book_id}) was not found'
        )
        logger.info(error)
        return {"success": False, "errors": error.model_dump()}

    except SQLAlchemyError as e:
        await db.rollback()
        error = ErrorSchema(
            error=ErrorCode.INVALID_PARAMETERS,
            extra=str(e)
        )
        logger.info(error)
        return {"success": False, "errors": error.model_dump()}

    except UniquenessError:
        error = ErrorSchema(
            error=ErrorCode.INVALID_PARAMETERS,
            extra=f'a review on this book ({book_id}) from this user ({user_id}) does not exist or is not active'
        )
        logger.info(error)
        return {"success": False, "errors": error.model_dump()}

    except ValidateError as e:
        error = ErrorSchema(
            error=ErrorCode.VALIDATE_ERROR,
            extra=str(e)
        )
        logger.info(error)
        return {"success": False, "errors": error.model_dump()}
        

@mutation.field("deleteReview")
async def delete_review(_, info: GraphQLResolveInfo, 
                        user_id: str, book_id: str,):
    db: AsyncSession = info.context["db"]
    try:        
        stmt = (
            Stmt(
                select(Review)
                )
            .con_filter(Review.user_id, [user_id])
            .con_filter(Review.book_id, [book_id])
            .con_filter(Review.actual, [True])
        )
        result = await db.execute(stmt())
        not_actual_review = result.scalar_one_or_none()
        if not not_actual_review:
            raise UniquenessError
        not_actual_review.actual = False
        await db.commit()
        return {"success": True}
    
    except IntegrityError:
        await db.rollback()
        error = ErrorSchema(
            error=ErrorCode.INVALID_PARAMETERS,
            extra=f'The book ({book_id}) was not found'
        )
        logger.info(error)
        return {"success": False, "errors": [error.model_dump()]}

    except SQLAlchemyError as e:
        await db.rollback()
        error = ErrorSchema(
            error=ErrorCode.INVALID_PARAMETERS,
            extra=str(e)
        )
        logger.info(error)
        return {"success": False, "errors": [error.model_dump()]}

    except UniquenessError:
        error = ErrorSchema(
            error=ErrorCode.INVALID_PARAMETERS,
            extra=f'a review on this book ({book_id}) from this user ({user_id}) does not exist or is not active'
        )
        logger.info(error)
        return {"success": False, "errors": [error.model_dump()]}

    except ValidateError as e:
        error = ErrorSchema(
            error=ErrorCode.VALIDATE_ERROR,
            extra=str(e)
        )
        logger.info(error)
        return {"success": False, "errors": [error.model_dump()]}


resolvers = [query, mutation]