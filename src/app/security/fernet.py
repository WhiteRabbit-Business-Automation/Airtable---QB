import os
from cryptography.fernet import Fernet

FERNET_KEY = os.getenv("QBO_FERNET_KEY") 
if not FERNET_KEY:
    raise RuntimeError("Missing QBO_FERNET_KEY env var")

fernet = Fernet(FERNET_KEY.encode())

def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode("utf-8")).decode("utf-8")

def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode("utf-8")).decode("utf-8")
