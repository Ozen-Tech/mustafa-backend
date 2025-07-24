
import typer
from sqlalchemy.orm import Session
import click

# <<<< CORREÇÃO: As importações agora começam com 'app.' >>>>
from app.db.connection import get_db
from app.crud import usuario as crud_usuario
from app.schemas import usuario as schemas_usuario
from app.db import models

cli_app = typer.Typer()

@cli_app.command()
def create_user(
    nome: str = typer.Argument(..., help="Nome completo do usuário."),
    email: str = typer.Argument(..., help="E-mail de login."),
    password: str = typer.Argument(..., help="Senha para o novo usuário."),
    perfil: schemas_usuario.PerfilUsuario = typer.Argument(..., help="Perfil do usuário (ADMIN, GESTOR, ou OPERADOR)."),
    empresa_id: int = typer.Option(1, help="ID da empresa à qual o usuário pertence.")
):
    """
    Cria um novo usuário no sistema com os dados fornecidos como argumentos.
    """
    print("--- 🚀 Criando Novo Usuário (Não-Interativo) ---")
    db: Session = next(get_db())
    
    try:
        if crud_usuario.get_user_by_email(db, email=email):
            print(f"\n❌ Erro: O e-mail '{email}' já está em uso.")
            raise typer.Abort()

        user_in = schemas_usuario.UsuarioCreate(
            nome=nome,
            email=email,
            password=password,
            perfil=perfil.value,
            empresa_id=empresa_id,
        )

        user = crud_usuario.create_user(db=db, user_in=user_in, empresa_id=empresa_id)
        
        print("\n--- ✅ Sucesso! ---")
        print(f"Usuário '{user.nome}' criado com o e-mail '{user.email}' e perfil '{user.perfil}'.")

    except Exception as e:
        print(f"\nOcorreu um erro: {e}")
    finally:
        db.close()

@cli_app.command()
def list_users():
    """Lista todos os usuários cadastrados."""
    db: Session = next(get_db())
    try:
        users = db.query(models.Usuario).all()
        if not users:
            print("Nenhum usuário encontrado.")
            return

        print("\n--- 👥 Lista de Usuários ---")
        for user in users:
            print(f"- ID: {user.id}, Nome: {user.nome}, E-mail: {user.email}, Perfil: {user.perfil}, Ativo: {user.is_active}")
        print("-" * 20)

    finally:
        db.close()

if __name__ == "__main__":
    cli_app()
