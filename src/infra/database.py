from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from settings import STR_DATABASE, ASYNC_STR_DATABASE
from sqlalchemy.orm import Session


# Cria o engine síncrono do banco de dados
engine = create_engine(STR_DATABASE, echo=True)

# Cria o engine assíncrono do banco de dados
async_engine = create_async_engine(ASYNC_STR_DATABASE, echo=True)

# Cria a sessão síncrona do banco de dados (mantida pela compatibilidade)
Session = sessionmaker(bind=engine, autocommit=False, autoflush=True)

# Cria a sessão assícrona do banco de dados
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

# Para trabalhar com tabelas
Base = declarative_base()

# Cria, caso não existam, as tabelas de todos os modelos que encontrar na aplicação (importados)
async def cria_tabelas():
    Base.metadata.create_all(engine)

# Dependência para injetar a sessão síncrona do banco de dados nas rotas
def get_db():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()

# Dependência para injetar a sessão assíncrona do banco de dados nas rotas
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()