from pydantic import ValidationError
from sqlalchemy.orm import Session
from quickbooks.objects.bill import Bill as QbBill
from quickbooks.objects import Account
from ..models.Bill import Bill as BillModel
from ..schemas.Bill import BillBase as BillSchema, BillStatus
from ..shared.quickbooks import get_qbo_client
from ..utils.qb_accounts import DEFAULT_EXPENSE_ACCOUNT_ID, SERVICE_TYPE_TO_QB_ACCOUNT
from ..utils.quickbooks import _get_customer_by_display_name, _get_default_company_id, _get_vendor, get_department_from_service_account
from ..database.engine import SessionLocal
from ..core.exceptions import BusinessValidationError, NotFoundDomainError, RetryableSystemError

async def bill_service(bill_id: str, company_id: str | None = None):
    db: Session | None = None
    bill: BillModel | None = None

    try:
        db = SessionLocal()

        # 1) Get bill
        try:
            bill = BillModel.from_id(bill_id)
        except Exception as e:
            raise NotFoundDomainError(f"Bill with id {bill_id} not found: {e}")

        # 2) Build schema
        bill_schema = BillSchema(
            bill_number=bill.bill_number,
            status=bill.status,
            pdf_link=bill.pdf_link,
            bill_date=bill.bill_date,
            due=bill.due,
            hauler_id=bill.hauler.hauler_number if bill.hauler else 0,
            account_number=bill.customer.account_number if bill.customer else "",
            service_type=bill.service.type[0] if bill.service else "",
            total_amount=bill.bill_amount,
            customer_account=bill.customer.account_number,
            service_account=bill.service_account[0] if bill.service_account else "",
        )

        # 3) Get QBO client
        if not company_id:
            company_id = _get_default_company_id(db)
        qb = get_qbo_client(realm_id=company_id, db=db)

        # 4) Business validations
        if not bill_schema.hauler_id:
            raise BusinessValidationError("Bill does not have a Hauler associated")
        hauler = _get_vendor(qb, bill_schema.hauler_id)

        if not bill_schema.customer_account:
            raise BusinessValidationError("Bill does not have a Customer associated")
        customer = _get_customer_by_display_name(qb, bill_schema.customer_account)
        

        # 5) Get expense account
        expense_account_id = SERVICE_TYPE_TO_QB_ACCOUNT.get(bill_schema.service_type) or DEFAULT_EXPENSE_ACCOUNT_ID
        if not expense_account_id:
            raise BusinessValidationError(
                f"No QuickBooks account mapping found for service type '{bill_schema.service_type}'",
                payload={"service_type": bill_schema.service_type},
            )

        
        expense_account = Account.get(expense_account_id, qb=qb)
        if expense_account is None:
            raise BusinessValidationError(
                f"Account id '{expense_account_id}' not found in QuickBooks",
                payload={"account_id": expense_account_id},
            )

        location = get_department_from_service_account(qb, bill_schema.service_account)
        if not location:
            raise BusinessValidationError(
                f"No department found for service account '{bill_schema.service_account}'",
                payload={"service_account": bill_schema.service_account},
            )
        

        # 6) Get QBO bill
        qbo_bill = QbBill()
        qbo_bill.DocNumber = bill_schema.bill_number
        qbo_bill.VendorRef = {"value": hauler.Id}
        # Asegura formato YYYY-MM-DD (por si bill_date es datetime)
        qbo_bill.TxnDate = bill_schema.bill_date.strftime("%Y-%m-%d")
        qbo_bill.DueDate = bill_schema.due.strftime("%Y-%m-%d")
        qbo_bill.PrivateNote = f"{bill_schema.pdf_link}"
        qbo_bill.DepartmentRef = {"value": location.Id}

        # Description : Convert BillAddr to human-readable string
        desc = getattr(customer, "DisplayName", "") or ""
        addr = getattr(customer, "BillAddr", None)
        if addr:
            parts = [getattr(addr, "Line1", None), getattr(addr, "City", None), getattr(addr, "CountrySubDivisionCode", None)]
            as_text = ", ".join([p for p in parts if p])
            if as_text:
                desc = as_text

        qbo_bill.Line = [{
            "DetailType": "AccountBasedExpenseLineDetail",
            "Amount": float(bill_schema.total_amount),
            "Description": desc,
            "AccountBasedExpenseLineDetail": {
                "AccountRef": {"value": expense_account.Id, "name": expense_account.Name},
                "CustomerRef": {"value": customer.Id}
            },
        }]

        # 7) Save to QBO
        try:
            qbo_bill.save(qb=qb)
        except Exception as e:
            msg = str(e)
            # simple heuristic
            if "429" in msg or "500" in msg or "503" in msg or "timeout" in msg.lower():
                raise RetryableSystemError(f"QBO transient error: {msg}")
            raise BusinessValidationError(f"QBO validation error: {msg}")

    except ValidationError as e:
        if bill:
            bill.status = "Issue sending to QB"
            bill.status_detail = f"400: ValidationError | {e.json()}"
            bill.save()
        raise BusinessValidationError("Pydantic validation error", payload={"errors": e.errors()})

    except (BusinessValidationError, NotFoundDomainError, RetryableSystemError) as e:
        if bill:
            bill.status = "Issue sending to QB"
            bill.status_detail = e.to_airtable_detail()
            bill.save()
        raise

    except Exception as e:
        if bill:
            bill.status = "Issue sending to QB"
            bill.status_detail = f"500: {e}"
            bill.save()
        # Deja que el worker decida reintentar
        raise
    else:
        bill.status_detail = ""
        bill.status = BillStatus.BILL_IN_QB.value
        bill.save()