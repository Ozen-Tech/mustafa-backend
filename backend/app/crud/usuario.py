from sqlalchemy.orm import Session, selectinload
from app.db import models
from app.schemas import usuario as schemas_usuario

# Importa as funções de segurança necessárias do local correto.
from app.core.hashing import get_password_hash, verify_password

def get_user_by_whatsapp(db: Session, whatsapp_number: str) -> models.Usuario | None:
    """Busca um usuário pelo número de WhatsApp."""
    return db.query(models.Usuario).filter(models.Usuario.whatsapp_number == whatsapp_number).first()

def get_user_by_email(db: Session, email: str) -> models.Usuario | None:
    """Busca um usuário pelo e-mail."""
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def create_user(db: Session, user_in: schemas_usuario.UsuarioCreate, empresa_id: int) -> models.Usuario:
    """Cria um novo usuário no banco de dados."""
    hashed_password = get_password_hash(user_in.password)
    
    db_user = models.Usuario(
        email=user_in.email,
        hashed_password=hashed_password,
        nome=user_in.nome,
        empresa_id=empresa_id,
        perfil=user_in.perfil,
        whatsapp_number=user_in.whatsapp_number
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> models.Usuario | None:
    """
    Autentica um usuário. Retorna o objeto do usuário se as credenciais forem válidas,
    caso contrário, retorna None.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_users_by_empresa(db: Session, empresa_id: int):
    """Retorna todos os usuários de uma empresa."""
    return (
        db.query(models.Usuario)
        .options(selectinload(models.Usuario.contratos))
        .filter(models.Usuario.empresa_id == empresa_id)
        .order_by(models.Usuario.nome)
        .all()
    )

def update_user(db: Session, user_id: int, user_in: schemas_usuario.UsuarioUpdate) -> models.Usuario | None:
    """Atualiza um usuário existente."""
    db_user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not db_user:
        return None

    update_data = user_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user