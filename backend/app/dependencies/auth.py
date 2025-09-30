# app/dependencies/auth.py

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated

from app.services.auth_service import AuthService, get_auth_service
from app.models.user import FirebaseUser

logger = logging.getLogger(__name__)

# Configuração do esquema de autenticação Bearer
bearer_scheme = HTTPBearer()

async def get_current_user(
    auth_credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> FirebaseUser:
    """
    Dependência do FastAPI para obter o usuário autenticado por um token Bearer.
    """
    token = auth_credentials.credentials
    
    try:
        user = await auth_service.verify_id_token(token)
        logger.debug("Token de usuário verificado com sucesso")
        return user
    except ValueError as error:
        logger.warning(f"Falha na validação do token: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Erro inesperado na validação do token: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )