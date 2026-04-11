from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
     SQLALCHEMY_DATABASE_URL,
     echo=False,  ## EM PROD NUNCA USAR ECHO=TRUE, EM DEV PODE USAR PARA DEBUG
     pool_size=0,
     max_overflow=0,
     pool_pre_ping=True,
     pool_recycle=300,
     pool_timeout=30,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

Base = declarative_base()


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
