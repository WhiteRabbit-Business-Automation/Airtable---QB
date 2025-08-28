from fastapi import HTTPException
from app.core.celery_worker import celery
from app.services.bill_service import bill_service

@celery.task(bind=True, max_retries=3)
def process_bill_task(self, bill_id: str):
    import asyncio
    try:
        # Run the async function in a new event loop
        asyncio.run(bill_service(bill_id))
    except Exception as e:
        print(f"Error processing bill {bill_id}: {e}")
        self.retry(exc=e)
