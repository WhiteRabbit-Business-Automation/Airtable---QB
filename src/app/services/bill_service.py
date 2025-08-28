from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session
from quickbooks.objects.bill import Bill as QbBill

from app.models.Bill import Bill as BillModel
from app.schemas.Bill import BillBase as BillSchema
from app.schemas.Bill import BillStatus
from app.shared.quickbooks import get_qbo_client

from app.utils.qb_accounts import SERVICE_TYPE_TO_QB_ACCOUNT
from app.utils.quickbooks import _get_customer_by_display_name , _get_default_company_id, _get_vendor, get_department_from_service_account
from app.database.engine import SessionLocal

from quickbooks.objects import Account

async def bill_service(bill_id : str, company_id: str | None = None):
  
  db: Session | None = None
  
  try:

    db = SessionLocal()

    try:
      # Find the bill from airtable
      bill = BillModel.from_id(bill_id)
    except Exception as e: #Talk about this error case with Jamie
      raise HTTPException(status_code=404, detail=f"Bill with id {bill_id} not found: {str(e)}")
    
    #Create the schema base on the info obtained
    bill_schema = BillSchema(
      bill_number=bill.bill_number,
      status=bill.status,
      pdf_link=bill.pdf_link,
      bill_date=bill.bill_date,
      due=bill.due,
      hauler_id= bill.hauler.hauler_number if bill.hauler else 0, 
      account_number=bill.customer.account_number if bill.customer else "",
      service_type=bill.service.type[0] if bill.service else "",
      total_amount=bill.bill_amount,
      customer_account=bill.customer.account_number,
      service_account=bill.service_account[0] if bill.service_account else "", #To search location 
    )
    
    if not company_id:
      company_id = _get_default_company_id(db)
      
    qb = get_qbo_client(company_id=company_id, db=db)
    
    #Find the Hauler with the HaulerId
    if not bill_schema.hauler_id:
      raise HTTPException(status_code=400, detail="Bill does not have a Hauler associated")

    hauler = _get_vendor(qb, bill_schema.hauler_id)

    #Find customer
    
    if not bill_schema.customer_account:
      raise HTTPException(status_code=400, detail="Bill does not have a Customer associated")
    
    customer = _get_customer_by_display_name(qb, bill_schema.customer_account)

    #Find expense account

    expense_account_id = SERVICE_TYPE_TO_QB_ACCOUNT.get(bill_schema.service_type)

    if not expense_account_id:
      raise HTTPException(status_code=400, detail=f"No QuickBooks account mapping found for service type '{bill_schema.service_type}'")

    expense_account = Account.get(expense_account_id, qb=qb)
    if expense_account.AccountType not in ["Expense", "Cost of Goods Sold"]:
        raise HTTPException(
            status_code=400,
            detail=f"Account {expense_account.Name} is not a valid expense account"
        )

    #location = get_department_from_service_account(qb, bill_schema.service_account[0])

    # Prepare the Bill object for QuickBooks API
    
    #Ask for APAccount
    qbo_bill = QbBill()
    qbo_bill.DocNumber = bill_schema.bill_number
    qbo_bill.VendorRef = {"value": hauler.Id}  # Assign the Hauler (Vendor)
    qbo_bill.TxnDate = bill_schema.bill_date.isoformat()
    qbo_bill.DueDate = bill_schema.due.isoformat()
    qbo_bill.PrivateNote = f"{bill_schema.pdf_link}"
    #qbo_bill.DepartmentRef = {"value": location.Id} if location else None

    # Ensure line items
    qbo_bill.Line = [{
        "DetailType": "AccountBasedExpenseLineDetail",
        "Amount": float(bill_schema.total_amount),
        "Description": f"{customer.BillAddr}",
        "AccountBasedExpenseLineDetail": {
            "AccountRef": {"value": expense_account.Id, "name": expense_account.Name},  # Use the correct account reference
            "CustomerRef": {"value": customer.Id, "name": customer.DisplayName}  # Assign the Customer reference
        },
    }]
    
    #Save bill
    qbo_bill.save(qb=qb)
    
  except ValidationError as e:
    #Create list with error msg
    error_messages = [f"Error in field {error['loc']}: {error['msg']}" for error in e.errors()]
    bill.status = "Issue sending to QB"
    bill.status_detail = "\n".join(error_messages)
    bill.save()
    print(f"Data validation error: {e.json()}")
    raise HTTPException(status_code=500, detail=str(e))
  except Exception as e:
    bill.status = "Issue sending to QB"
    bill.status_detail = str(e)
    bill.save()
    print(f"Error processing bill: {e}")
    raise HTTPException(status_code=500, detail=str(e))

  bill.status_detail = ""
  bill.status = BillStatus.BILL_IN_QB.value
  bill.save()