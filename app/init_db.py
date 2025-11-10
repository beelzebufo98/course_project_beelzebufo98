from app.db import Base, get_engine, get_session_local


def init_db():
    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database engine not initialized")
    Base.metadata.create_all(bind=engine)


def get_db():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
