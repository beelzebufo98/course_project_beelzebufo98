import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_database_url() -> str:
    is_test = "PYTEST_CURRENT_TEST" in os.environ or os.getenv("IS_TEST", "0") == "1"
    if is_test:
        return os.getenv("TEST_DATABASE_URL")
    return os.getenv("DATABASE_URL")


def get_engine():
    global _engine
    if _engine is None:
        url = get_database_url()
        if not url:
            print("No DATABASE_URL or TEST_DATABASE_URL yet — engine will init later")
            return None
        print(f"Using database: {url}")
        _engine = create_engine(url)
    return _engine


def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        if engine is None:
            raise RuntimeError("Cannot initialize SessionLocal — engine is None")
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal
