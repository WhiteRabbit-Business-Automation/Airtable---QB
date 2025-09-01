from pyairtable.orm import Model, fields as F

from ..core.config import AIRTABLE_TOKEN, AIRTABLE_BASE_ID

class Customer(Model):
  sf_name = F.TextField("SF Customer Name")
  account_number = F.TextField("A#")
  parent_account = F.TextField("Parent Account")
  past_due_months = F.TextField("Past Due Months")
  last_invoice_to_customer = F.DateField("Last Invoice to Customer 🔎")
  service = F.LinkField[str]("Service 🔎","app.models.Service.Service")
  bills = F.LinkField("Bills 🔎","app.models.Bill.Bill")
  
  class Meta:
    base_id = AIRTABLE_BASE_ID
    table_name = "Customers"
    api_key = AIRTABLE_TOKEN
