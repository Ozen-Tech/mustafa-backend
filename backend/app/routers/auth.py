# backend/app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from app.db.connection import get_db
from app.db import models
from app.schemas import usuario as schemas_usuario
from app.crud import usuario as crud_usuario
from app.dependencies import create_access_token, get_current_user

router = APIRouter(
    # Movido o prefixo para o main.py para maior clareza
    tags=["Usuários e Autenticação"]
)

@router.post("/token", response_model=schemas_usuario.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud_usuario.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# << ATUALIZADO >> Rota para criar um usuário. Agora ela retorna o usuário completo com ID.
@router.post("", response_model=schemas_usuario.Usuario, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_in: schemas_usuario.UsuarioCreate, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user) # Protegido, apenas usuários logados podem criar outros
):
    # Regra de negócio: Apenas Admins podem criar outros usuários
    if current_user.perfil != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas administradores podem criar novos usuários.")

    db_user = crud_usuario.get_user_by_email(db=db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já registrado."
        )
    
    # << ATUALIZADO >> Associa o novo usuário à mesma empresa do admin que o está criando
    user_in.empresa_id = current_user.empresa_id
    
    return crud_usuario.create_user(db=db, user_in=user_in)


@router.get("/me", response_model=schemas_usuario.Usuario)
def read_users_me(current_user: models.Usuario = Depends(get_current_user)):
    """Retorna os dados do usuário atualmente logado."""
    return current_user


@router.get("", response_model=List[schemas_usuario.Usuario], summary="Lista todos os usuários da empresa")
def read_users(
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    """Retorna uma lista de usuários da empresa do usuário logado."""
    users_db = crud_usuario.get_users_by_empresa(db, empresa_id=current_user.empresa_id)
    # << ATUALIZADO >> Precisamos construir a resposta com a URL de acesso completa para os contratos
    response_list = []
    for user in users_db:
        user_schema = schemas_usuario.Usuario.model_validate(user)
        user_schema.contratos = [
            schemas_usuario.ContratoInfo(
                id=c.id,
                nome_arquivo_original=c.nome_arquivo_original,
                url_acesso=f"/arquivos-contratos/{c.nome_arquivo_servidor}"
            )
            for c in user.contratos
        ]
        response_list.append(user_schema)
    return response_list


@router.put("/{user_id}", response_model=schemas_usuario.Usuario, summary="Atualiza um usuário")
def update_user_details(
    user_id: int, 
    user_in: schemas_usuario.UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza as informações de um usuário."""
    if current_user.perfil != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas administradores podem editar usuários.")

    db_user = crud_usuario.update_user(db, user_id=user_id, user_in=user_in)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Retornar o schema completo após a atualização
    return schemas_usuario.Usuario.model_validate(db_user)