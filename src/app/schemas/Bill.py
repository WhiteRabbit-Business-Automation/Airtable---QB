from __future__ import annotations
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, HttpUrl, StringConstraints, conint, field_validator, StrictInt 

class BillStatus(str, Enum):
  DONE = "Done"
  LEAVE = "Leave"
  SEND_BILL_TO_QB = "Send bill to QB"
  ISSUE_SENDING_TO_QB = "Issue sending to QB"
  BILL_IN_QB = "Bill in QB"
  SEND_INVOICE_TO_SF = "Send invoice to SF"
  ISSUE_SENDING_TO_SF = "Issue sending to SF"
  INVOICE_IN_SF = "Invoice in SF"
  
class ServiceType(str, Enum):
  TRASH = "Trash"
  ROLL_OFF = "Roll Off (move to temp or monthly)"
  ROLL_OFF_MONTH = "Roll off - Monthly"
  ROLL_OFF_TEMP = "Roll off - Temp"
  COMPACTOR = "Compactor"
  RECYCLING = "Recycling"
  MISC = "Misc"
  
class BillBase(BaseModel):
  bill_number : Annotated[str, StringConstraints(min_length=1, max_length=50)]
  status: BillStatus
  pdf_link : Annotated[HttpUrl, StringConstraints(min_length=1)]
  bill_date: date
  due: date
  hauler_id : Annotated[int, StrictInt]
  account_number: Annotated[str, StringConstraints(min_length=1, max_length=50)]  
  service_account: Annotated[str, StringConstraints(min_length=1, max_length=50)]
  service_type: Annotated[ServiceType, StringConstraints(min_length=1, max_length=50)]
  service_name: Annotated[str, StringConstraints(min_length=1, max_length=250)]
  total_amount : Annotated[Decimal, conint(gt=0)]
  customer_account: Annotated[str, StringConstraints(min_length=1, max_length=50)]
  sales_term: Annotated[int, StrictInt]


  #Due date comes with mm/dd/yyyy format instead of dd/mm/yyyy
  @field_validator("due", mode="before")
  @classmethod
  def format_due(cls, v):
      if not isinstance(v, str):
          return v
      try:
          month, day, year = map(int, v.split("/"))
          return date(year, month, day)
      except ValueError:
          raise ValueError("Invalid due date format")