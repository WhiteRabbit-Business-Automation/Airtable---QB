from datetime import date
from pyairtable.orm import Model, fields as F
from ..core.config import AIRTABLE_TOKEN, AIRTABLE_BASE_ID
from pydantic import BaseModel

class Service(Model):
  name = F.TextField("Name")
  type = F.MultipleSelectField("Type")
  status = F.SelectField("Status")
  hauler = F.SingleLinkField("Hauler 🔎", "app.models.Hauler.Hauler")
  service_account_number = F.TextField("Service Acc #")
  expected_cost = F.TextField("Cost (expected) 💲")
  expected_price = F.TextField("Price (expected) 💲")
  service_start_date = F.DateField("Service Start Date")
  additional_notes = F.MultilineTextField("Additional Notes")
  agreement_expiration = F.DateField("Agreement Expiration")
  customer = F.SingleLinkField("Customer 🔎", "app.models.Customer.Customer")
  last_bill_date = F.LookupField[date]("Last Bill Date 🔎")
  last_bill_date_invoice_month = F.LookupField[date]("Last bill date 🔎 (Invoice Month)")
  last_invoice_due_to_customer_source = F.LookupField[date]("Last Invoice Due to customer source")
  hauler_terms = F.LookupField[int]("Hauler Terms")
  bills = F.LinkField[str]("Bills 🔎", "app.models.Bill.Bill")
  account_number = F.LookupField[str]("A# 🔎")
  parent_account = F.LookupField[str]("Parent Account 🔎")
  duplicate_delete = F.CheckboxField("Duplicate (delete)")
  
  class Meta:
      base_id = AIRTABLE_BASE_ID
      table_name = "Services"
      api_key = AIRTABLE_TOKEN
      
