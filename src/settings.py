from dotenv import load_dotenv, find_dotenv
import os

# localiza o arquivo de .env
dotenv_file = find_dotenv()

# Carrega o arquivo .env
load_dotenv(dotenv_file)

# Configurações da API
HOST = os.getenv("HOST", "127.0.0.1")
PORT = os.getenv("PORT", "8000")
RELOAD = os.getenv("RELOAD", True)

# Configuração banco de dados
DB_SGBD = os.getenv("DB_SGBD")
DB_NAME = os.getenv("DB_NAME")
#Caso seja diferente de sqlite
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# Ajusta STR_DATABASE conforme gerenciador escolhido
if DB_SGBD == 'sqlite':     #SQLite
    STR_DATABASE = f"sqlite:///{DB_NAME}.db"
elif DB_SGBD == 'mysql':    #MySQL
    import pymysql
    STR_DATABASE = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
elif DB_SGBD == 'mssql':    #msSQL
    import pymssql
    STR_DATABASE = f"mssql+pymyssql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8"
else:   #SQLite
    STR_DATABASE = f"sqlite:///apiDatabase.db"

# Vinicius de Liz da Conceição

# Commit atualizando o settings para novas conexões com os banco de dados