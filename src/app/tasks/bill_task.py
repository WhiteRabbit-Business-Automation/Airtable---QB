from app.core.celery_worker import celery
from app.services.bill_service import bill_service
from app.core.exceptions import BusinessValidationError, NotFoundDomainError, RetryableSystemError

@celery.task(bind=True, max_retries=3, default_retry_delay=180)
def process_bill_task(self, bill_id: str, company_id: str | None = None):
    import asyncio
    try:
        asyncio.run(bill_service(bill_id, company_id))
    except (BusinessValidationError, NotFoundDomainError) as e:
        # 4xx / no-retry: let fail clean (will be logged by the service)
        print(f"[Non-retryable] bill_id={bill_id} err={e}")
        raise
    except RetryableSystemError as e:
        # Temporary errors: yes retry
        print(f"[Retryable] bill_id={bill_id} err={e}")
        raise self.retry(exc=e)
    except Exception as e:
        # Unknowns: treat as retryable once (would improve with type classification)
        print(f"[Retryable-unknown] bill_id={bill_id} err={e}")
        raise self.retry(exc=e)
