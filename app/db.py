from sqlmodel import Session, create_engine
from urllib.parse import quote_plus
from app.config import settings

password = quote_plus(settings.DB_PASSWORD)
DATABASE_URL = (
    f"mysql+mysqlconnector://{settings.DB_USER}:"
    f"{password}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.DB_DATABASE}"
)

engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session
