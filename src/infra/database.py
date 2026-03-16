from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import STR_DATABASE
from sqlalchemy.orm import Session


# Cria o engine do banco de dados
engine = create_engine(STR_DATABASE, echo=True)

# Cria a sessão do banco de dados
Session = sessionmaker(bind=engine, autocommit=False, autoflush=True)

# Para trabalhar com tabelas
Base = declarative_base()

# Cria, caso não existam, as tabelas de todos os modelos que encontrar na aplicação (importados)
async def cria_tabelas():
    Base.metadata.create_all(engine)

# Dependência para injetar a sessão do banco de dados nas rotas
def get_db():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()

# Commit da infraestrutura do banco de dados, com sessão