from app.database import get_db
from app.models.foto import Foto

def check_photos():
    db = next(get_db())
    photos = db.query(Foto).order_by(Foto.data_envio.desc()).limit(5).all()
    for p in photos:
        print(f'ID: {p.id}, URL: {p.url_foto}, Data: {p.data_envio}')
    db.close()

if __name__ == '__main__':
    check_photos()
