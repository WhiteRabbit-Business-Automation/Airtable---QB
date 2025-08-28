from fastapi import APIRouter, HTTPException, status

from app.models import  WebHook


from app.tasks.bill_task import process_bill_task

router = APIRouter()

@router.post("/webhook")
async def webhook_to_quickbooks(data: WebHook.WebHook, status_code= status.HTTP_200_OK):
  bill_id = data.id
  process_bill_task.delay(bill_id)
  return {"message": "Webhook received"}