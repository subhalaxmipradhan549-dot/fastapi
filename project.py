from fastapi import FastAPI, status, Query
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# MSSQL Connection

DATABASE_URL = (
    "mssql+pyodbc://LAPTOP-ADUVE4JV/BookDB?"
    "driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

# Create Engine

engine = create_engine(DATABASE_URL)

# Create Session

SessionLocal = sessionmaker(bind=engine)

# Base Class

Base = declarative_base()

# Database Table Model

class BookTable(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    publish_date = Column(String, nullable=False)

# Create Table

Base.metadata.create_all(bind=engine)

# FastAPI App

app = FastAPI(title="Book Management API")

# Pydantic Models

class Book(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    author: str = Field(min_length=2, max_length=100)
    publish_date: str

class BookUpdate(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    author: str = Field(min_length=2, max_length=100)
    publish_date: str

# GET All Books with Pagination

@app.get("/book", tags=["Books"])
def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(5, ge=1)
):

    db = SessionLocal()

    try:

        books = db.query(BookTable)\
                  .order_by(BookTable.id)\
                  .offset(skip)\
                  .limit(limit)\
                  .all()

        return {
            "status": "success",
            "count": len(books),
            "data": jsonable_encoder(books)
        }

    finally:
        db.close()

# GET Book By ID

@app.get("/book/{book_id}", tags=["Books"])
def get_book_by_id(book_id: int):

    db = SessionLocal()

    try:

        book = db.query(BookTable).filter(
            BookTable.id == book_id
        ).first()

        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        return {
            "status": "success",
            "data": jsonable_encoder(book)
        }

    finally:
        db.close()

# SEARCH BOOK BY AUTHOR

@app.get("/search/", tags=["Books"])
def search_book(author: str):

    db = SessionLocal()

    try:

        books = db.query(BookTable).filter(
            BookTable.author.contains(author)
        ).all()

        if not books:
            raise HTTPException(
                status_code=404,
                detail="No books found"
            )

        return {
            "status": "success",
            "results": jsonable_encoder(books)
        }

    finally:
        db.close()

# ADD New Book

@app.post(
    "/book",
    status_code=status.HTTP_201_CREATED,
    tags=["Books"]
)
def add_book(book: Book):

    db = SessionLocal()

    try:

        new_book = BookTable(
            title=book.title,
            author=book.author,
            publish_date=book.publish_date
        )

        db.add(new_book)

        db.commit()

        db.refresh(new_book)

        return {
            "status": "success",
            "message": "Book added successfully",
            "data": jsonable_encoder(new_book)
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()

# UPDATE Book

@app.put("/book/{book_id}", tags=["Books"])
def update_book(book_id: int, book_update: BookUpdate):

    db = SessionLocal()

    try:

        book = db.query(BookTable).filter(
            BookTable.id == book_id
        ).first()

        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        book.title = book_update.title
        book.author = book_update.author
        book.publish_date = book_update.publish_date

        db.commit()

        db.refresh(book)

        return {
            "status": "success",
            "message": "Book updated successfully",
            "data": jsonable_encoder(book)
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()

# DELETE Book

@app.delete("/book/{book_id}", tags=["Books"])
def delete_book(book_id: int):

    db = SessionLocal()

    try:

        book = db.query(BookTable).filter(
            BookTable.id == book_id
        ).first()

        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        db.delete(book)

        db.commit()

        return {
            "status": "success",
            "message": "Book deleted successfully"
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()

