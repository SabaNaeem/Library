import os
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Load environment variables from .env file
load_dotenv()

SQLALCHEMY_DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

try:
    # Create the SQLAlchemy engine and sessionmaker
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)

    # Create a base class for declarative class definitions
    Base = declarative_base()

except Exception as e:
    print(f"Error connecting to database: {e}")
    raise

# inspector = inspect(engine)
#
# # Get table names
# tables = inspector.get_table_names()
#
# # Print table names
# print("Tables in the database:")
# for table in tables:
#     print(table)

@contextmanager
def session_scope():
    """
    A context manager for handling database sessions.

    Returns:
        Yields a database session object that is automatically committed on
        success, rolled back on exception, and closed when done.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

