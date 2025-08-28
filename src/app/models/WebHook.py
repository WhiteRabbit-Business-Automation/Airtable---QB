from pydantic import BaseModel

class WebHook(BaseModel):
  id: str
  name: str