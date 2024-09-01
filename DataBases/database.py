from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# para sqlite
SQLALCHEMY_DATABASE_URL = "sqlite:///productos.sqlite"
# para mysql
# SQLALCHEMY_DATABASE_URL ="mysql+mysqlclient://root:123456789@localhost:3306/GestorUno"



engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, pool_size=5
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
