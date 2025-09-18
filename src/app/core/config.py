import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


APP_NAME = os.getenv("APP_NAME", "N/N")
APP_VERSION = os.getenv("APP_VERSION", "0.0")


AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

QUICKBOOKS_CLIENT_ID = os.environ["QUICKBOOKS_CLIENT_ID"]
QUICKBOOKS_CLIENT_SECRET = os.environ["QUICKBOOKS_CLIENT_SECRET"]
QUICKBOOKS_COMPANY_ID = os.environ["QUICKBOOKS_COMPANY_ID"]
QUICKBOOKS_REDIRECT_URI = os.environ["QUICKBOOKS_REDIRECT_URI"]
QUICKBOOKS_ENV = os.environ["QUICKBOOKS_ENV"] 

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./attoqb.db")

REDIS_URL = os.getenv("REDIS_URL", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

PORT = int(os.getenv("PORT", "8080"))
