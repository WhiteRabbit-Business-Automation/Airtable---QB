import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from app.database.engine import SessionLocal
from app.database.models.QuickBooksToken import QboConnection
from app.security.fernet import decrypt

def main():
    db = SessionLocal()
    try:
        rows = db.query(QboConnection).all()
        if not rows:
            print("⚠️ No hay registros en la tabla qbo_connections.")
        for row in rows:
            print("Company ID:", row.company_id)
            print("Encrypted refresh token:", row.refresh_token)
            try:
                print("Decrypted token:", decrypt(row.refresh_token))
            except Exception as e:
                print("No se pudo descifrar:", e)
            print("Updated at:", row.updated_at)
            print("------")
    finally:
        db.close()

if __name__ == "__main__":
    main()
