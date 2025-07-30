# app/dependencies/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated

from app.services.auth_service import AuthService, get_auth_service
from app.models.user import FirebaseUser


#    Ele instrui o Swagger a simplesmente pedir um "Bearer Token".
bearer_scheme = HTTPBearer()

# async def get_current_user(
#     auth_credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
#     auth_service: Annotated[AuthService, Depends(get_auth_service)]
# ) -> FirebaseUser:
#     """
#     Dependência do FastAPI para obter o usuário autenticado por um token Bearer.
#     """
#     # ✅ MUDANÇA 3: Extraímos a string do token do objeto de credenciais.
#     token = auth_credentials.credentials
#     try:
#         user = await auth_service.verify_id_token(token)
#         return user
#     except ValueError as error:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=str(error),
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     except Exception:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Não foi possível validar as credenciais!",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

# app/dependencies/auth.py

async def get_current_user(
    auth_credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> FirebaseUser:
    """
    Dependência do FastAPI para obter o usuário autenticado por um token Bearer.
    """
    token = auth_credentials.credentials
    
    # ✅ INÍCIO DO CÓDIGO DE DEBUG
    print("--- INICIANDO VERIFICAÇÃO DE TOKEN ---")
    print(f"Token recebido (primeiros 30 chars): {token[:30]}...")
    # ✅ FIM DO CÓDIGO DE DEBUG

    try:
        user = await auth_service.verify_id_token(token)
        print("--- VERIFICAÇÃO DE TOKEN BEM-SUCEDIDA ---") # Log de sucesso
        return user
    except ValueError as error:
        # Log detalhado do erro de valor
        print(f"!!! ERRO DE VALOR NA VALIDAÇÃO DO TOKEN: {error} !!!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # ✅ Log detalhado para QUALQUER outra exceção
        print(f"!!! EXCEÇÃO INESPERADA NA VALIDAÇÃO DO TOKEN: {type(e).__name__} - {e} !!!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais!",
            headers={"WWW-Authenticate": "Bearer"},
        )