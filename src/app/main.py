import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .api.routes.bills import router as router_bills
from .api.routes.qbo import router as router_quickbooks
from .core.config import APP_NAME, APP_VERSION

from app.database.engine import Base, engine
from app.database import models


Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(router_bills, prefix="/bills")
app.include_router(router_quickbooks, prefix="/qbo")

router = APIRouter()

@router.get("/")
async def root():
  return JSONResponse(content={
    "app": APP_NAME,
    "version": APP_VERSION,
    "status": "running"
  })

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)