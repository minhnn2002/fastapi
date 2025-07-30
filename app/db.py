from sqlmodel import Session, create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

load_dotenv()

password = quote_plus(os.getenv("DB_PASSWORD"))
DATABASE_URL = (
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:"
    f"{password}@{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"
)

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
