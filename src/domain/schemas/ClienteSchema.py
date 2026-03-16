from pydantic import BaseModel, ConfigDict
from typing import Optional

class ClienteCreate(BaseModel):
    nome: str
    cpf: str
    telefone: str

class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None

class ClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    cpf: str
    telefone: str



# Vinicius de Liz da Conceição

# Commit mudando arquivo entities para schemas, atualizando os arquivos adicionando Schemas na nomeação
# Commit atualizando o Create, Update e Response no Funcionario

