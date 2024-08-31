import asyncio
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

# Crear una base de datos SQLite en memoria (puedes cambiar la URL para usar un archivo)
engine = create_async_engine("sqlite+aiosqlite:///pruebassss.sqlite", echo=True)

# Crear una sesión asíncrona
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Crear la base para los modelos
Base = declarative_base()

# Definir el modelo de usuario
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=False)
    email = Column(String, index=True, unique=False)

# Crear las tablas
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Crear un usuario
async def create_user(db, user: User):
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# Obtener un usuario
async def get_user(db: AsyncSession, user_id: int):
    return await db.get(User, user_id)

# Función principal
async def main():
    # Crear la base de datos
    await create_db()

    # Crear un nuevo usuario
    async with async_session() as db:
        user = User(name="John Doe", email="johndoe@example.com")
        user = await create_user(db, user)
        print(user)

# Ejecutar el código asíncrono
asyncio.run(main())