from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated # Importe Annotated para anotações de tipo modernas

# Assumindo que essas importações estão definidas corretamente
# em seus respectivos arquivos: app/services/auth_service.py e app/models/user.py
from app.services.auth_service import AuthService, get_auth_service
from app.models.user import FirebaseUser

# O OAuth2PasswordBearer é a forma mais comum e recomendada
# para autenticação via token Bearer no FastAPI.
# 'tokenUrl="/token"' indica o endpoint onde o cliente deve enviar
# credenciais (geralmente username e password) para obter um token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def get_current_user(
    # Use Annotated para clareza e metadados de tipo.
    # O FastAPI automaticamente tenta extrair o token do cabeçalho
    # Authorization: Bearer <token>. Se não encontrar ou o formato estiver errado,
    # ele já levanta uma HTTPException 401 por conta do Depends(oauth2_scheme).
    token: Annotated[str, Depends(oauth2_scheme)],
    # Injeta a instância do seu serviço de autenticação.
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> FirebaseUser:
    """
    Dependência do FastAPI para obter o usuário autenticado por um token.

    Esta função é projetada para ser usada em rotas protegidas. Ela
    extrai o token de autorização, verifica sua validade usando o
    AuthService e retorna o objeto FirebaseUser correspondente.

    Raises:
        HTTPException:
            - status.HTTP_401_UNAUTHORIZED se o token for inválido, expirado,
              ou se houver qualquer problema na validação.
    """
    try:
        # Tenta verificar o token usando seu serviço de autenticação.
        # O 'auth_service.verify_id_token' deve retornar um objeto FirebaseUser
        # se o token for válido.
        user = await auth_service.verify_id_token(token)
        return user
    except ValueError as error:
        # Captura erros específicos de validação do token (ex: token malformado,
        # assinatura inválida, etc.) levantados pelo seu AuthService.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error), # Mensagem de erro mais específica do AuthService
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        # Captura qualquer outra exceção inesperada que possa ocorrer
        # durante o processo de validação do token.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais!",
            headers={"WWW-Authenticate": "Bearer"},
        )