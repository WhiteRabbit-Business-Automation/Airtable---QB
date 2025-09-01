from fastapi import APIRouter, HTTPException, status
from ...models import WebHook
from ...tasks.bill_task import process_bill_task
from kombu.exceptions import OperationalError  # error típico de broker

router = APIRouter()

@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def webhook_to_quickbooks(data: WebHook.WebHook):
    bill_id = data.id
    try:
        process_bill_task.delay(bill_id)
    except OperationalError as e:
        # Service unavailable Celery error
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail={"message": "Queue unavailable", "error": str(e)})
    return {"message": "Webhook received", "bill_id": bill_id, "status": "queued"}
