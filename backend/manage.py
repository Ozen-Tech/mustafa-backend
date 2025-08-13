
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

@cli_app.command()
def fix_photos():
    """
    Corrige as URLs das fotos existentes que possuem URLs locais problemáticas.
    """
    print("🔧 Iniciando correção de fotos existentes...")
    db: Session = next(get_db())
    
    try:
        # Buscar fotos com URLs locais problemáticas
        fotos_problematicas = db.query(models.FotoPromotor).filter(
            models.FotoPromotor.url_foto.like('%localhost%')
        ).all()
        
        if not fotos_problematicas:
            print("✅ Nenhuma foto problemática encontrada!")
            return
        
        print(f"⚠️  Encontradas {len(fotos_problematicas)} fotos com URLs problemáticas")
        
        # URL de placeholder para fotos indisponíveis
        placeholder_url = "https://via.placeholder.com/400x300/e2e8f0/64748b?text=Foto+Temporariamente+Indisponivel"
        
        fotos_corrigidas = 0
        
        for foto in fotos_problematicas:
            try:
                print(f"🔄 Corrigindo foto ID {foto.id}...")
                
                # Atualizar para placeholder
                foto.url_foto = placeholder_url
                foto.nome_arquivo_servidor = f"placeholder_{foto.id}_{foto.data_envio.strftime('%Y%m%d')}"
                
                fotos_corrigidas += 1
                
            except Exception as e:
                print(f"❌ Erro ao corrigir foto ID {foto.id}: {str(e)}")
                continue
        
        # Salvar todas as alterações
        db.commit()
        
        print(f"\n✅ {fotos_corrigidas} fotos corrigidas com sucesso!")
        print("💡 As fotos agora mostram um placeholder até serem reenviadas")
        print("📱 Oriente os promotores a reenviarem fotos importantes via WhatsApp")
        
    except Exception as e:
        print(f"❌ Erro geral na correção: {str(e)}")
        db.rollback()
    
    finally:
        db.close()

@cli_app.command()
def photo_stats():
    """
    Mostra estatísticas das fotos no banco de dados.
    """
    print("📊 Estatísticas das Fotos")
    db: Session = next(get_db())
    
    try:
        total = db.query(models.FotoPromotor).count()
        problematicas = db.query(models.FotoPromotor).filter(
            models.FotoPromotor.url_foto.like('%localhost%')
        ).count()
        cloudinary = db.query(models.FotoPromotor).filter(
            models.FotoPromotor.url_foto.like('%cloudinary%')
        ).count()
        placeholders = db.query(models.FotoPromotor).filter(
            models.FotoPromotor.url_foto.like('%placeholder%')
        ).count()
        
        print(f"📸 Total de fotos: {total}")
        print(f"⚠️  URLs problemáticas: {problematicas}")
        print(f"☁️  URLs Cloudinary: {cloudinary}")
        print(f"🖼️  Placeholders: {placeholders}")
        
        if problematicas > 0:
            print(f"\n💡 Execute 'python manage.py fix-photos' para corrigir {problematicas} fotos")
        else:
            print("\n✅ Todas as fotos estão OK!")
            
    except Exception as e:
        print(f"❌ Erro ao buscar estatísticas: {str(e)}")
    
    finally:
        db.close()

@cli_app.command()
def check_files():
    """Verifica se os arquivos de foto ainda existem no servidor"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from check_existing_files import check_files as check_existing_files_func
        check_existing_files_func()
        
    except ImportError as e:
        print(f"❌ Erro ao importar verificador: {e}")
    except Exception as e:
        print(f"❌ Erro durante a verificação: {e}")
        import traceback
        traceback.print_exc()

@cli_app.command()
def recover_photos():
    """Tenta recuperar TODAS as fotos existentes fazendo upload para Cloudinary"""
    print("🚀 Iniciando recuperação completa de fotos...")
    print("⚠️  ATENÇÃO: Este processo pode demorar vários minutos!")
    
    try:
        # Importar e executar o serviço de recuperação
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from recover_all_photos import PhotoRecoveryService
        
        recovery_service = PhotoRecoveryService()
        recovery_service.recover_all_photos()
        
    except ImportError as e:
        print(f"❌ Erro ao importar serviço de recuperação: {e}")
        print("   Certifique-se de que o arquivo recover_all_photos.py existe")
    except Exception as e:
        print(f"❌ Erro durante a recuperação: {e}")
        import traceback
        traceback.print_exc()

@cli_app.command()
def recover_for_gallery():
    """Tenta recuperar fotos especificamente para a galeria"""
    print("🖼️ Iniciando recuperação de fotos para galeria...")
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from recover_photos_for_gallery import GalleryPhotoRecovery
        
        service = GalleryPhotoRecovery()
        service.recover_all_for_gallery()
        
    except ImportError as e:
        print(f"❌ Erro ao importar GalleryPhotoRecovery: {e}")
        print("   Certifique-se de que o arquivo recover_photos_for_gallery.py existe")
    except Exception as e:
        print(f"❌ Erro durante a recuperação para galeria: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    cli_app()
