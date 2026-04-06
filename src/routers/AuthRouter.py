from fastapi import APIRouter, Depends, HTTPException, status, Request
from services.AuditoriaService import AuditoriaService
from sqlalchemy.orm import Session
from datetime import timedelta

from domain.schemas.AuthSchema import LoginRequest, TokenResponse, RefreshTokenRequest, FuncionarioAuth

from infra.orm.FuncionarioModel import FuncionarioDB
from infra.database import get_db
from infra.security import verify_password, create_access_token, create_refresh_token, verify_refresh_token
from infra.dependencies import get_current_activate_user
from infra.rate_limit import limiter, get_rate_limit

# SlowAPI
from slowapi.errors import RateLimitExceeded

from settings import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter()

@router.post("/auth/login", response_model=TokenResponse, tags=["Autenticação"], summary="Login de funcionário - pública - retorn acess e refresh token")
@limiter.limit(get_rate_limit("critical"))
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Realiza login do funcionário e retorno access token e refresh token

    - **cpf**: CPF do funcionário                   - **senha**: Senha do funcionário

    Retorno: - access_token: Token de curta duração (15 minutos)    - refresh_token: Token de longa duração (7 dias)
    """
    try:
        # Busca funcionário pelo CPF
        funcionario = db.query(FuncionarioDB).filter(FuncionarioDB.cpf == login_data.cpf).first()

        if not funcionario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="CPF ou senha inválidos", headers={"WWW-Authenticate": "Bearer"}, )
        
        # Verifica se a senha está correta
        if not verify_password(login_data.senha, funcionario.senha):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="CPF ou senha inválidos", headers={"WWW-Authenticate": "Bearer"}, )
        
        # Cria o access token JWT (curta duração)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": funcionario.cpf, #subject = CPF
                "id": funcionario.id,   # ID do funcionario
                "grupo": funcionario.grupo
            },
            expires_delta=access_token_expires
        )

        # Cria o refresh token JWT (longa duração)
        refresh_token = create_refresh_token(
            data={
                "sub": funcionario.cpf, #subject = CPF
                "id": funcionario.id,   # ID do funcionario
                "grupo": funcionario.grupo   
            }
        )

        # Registrar auditoria de login
        AuditoriaService.registrar_acao(
            db=db,
            funcionario_id=funcionario.id,
            acao="LOGIN",
            recurso="AUTH",
            request=request
        )

        # parei no slide 27

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60, # em segundos
            refresh_expires_in=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60 # em segundos
        )
    except RateLimitExceeded:
        raise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao realizar login: {str(e)}")

@router.post("/auth/refresh", response_model=TokenResponse, tags=["Autenticação"], summary="Refresh token - pública - renova access token")
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Renova o access token usando um refresh token válido

    - **refresh_token**: Refresh token válido retornado no login

    Retorno novo access token e refresh token
    """
    try:
        # Verifica e decodifica o refresh token
        payload = verify_refresh_token(refresh_data.refresh_token)

        # Busca funcionário para garantir que ainda existe
        cpf = payload.get("sub")
        funcionario = db.query(FuncionarioDB).filter(FuncionarioDB.cpf == cpf).first()

        if not funcionario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Funcionário não encontrado", headers={"WWW-Authenticate": "Bearer"}, )
        
        # Cria novo access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": funcionario.cpf, #subject = CPF
                "id": funcionario.id,   # ID do funcionario
                "grupo": funcionario.grupo
            },
            expires_delta=access_token_expires
        )

        # Cria novo refresh token
        new_refresh_token = create_refresh_token(
            data={
                "sub": funcionario.cpf, #subject = CPF
                "id": funcionario.id,   # ID do funcionario
                "grupo": funcionario.grupo
            }
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60, # em segundos
            refresh_expires_in=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60 # em segundos
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Erro ao renovar token: {str(e)}", headers={"WWW-Authenticate": "Bearer"}, )
    
@router.get("/auth/me", response_model=FuncionarioAuth, tags=["Autenticação"], summary="Dados do usuário atual - protegida por autenticação")
async def get_current_user_info(current_user: FuncionarioAuth = Depends(get_current_activate_user)):
    """
    Retorna informações do usuário autenticado atual
    Requer header: Authorization: Bearer <access_token>
    """

    return current_user

@router.post("/auth/logout", tags=["Autenticação"], summary="Logout - pública")
async def logout():
    """
    Endpoint para logout (client-side)

    Na prática, o logout é implementado no cliente removendo tokens
    Este endpoint existe apenas para completude da API
    """
    return {"message": "Logout realizado com sucesso"}