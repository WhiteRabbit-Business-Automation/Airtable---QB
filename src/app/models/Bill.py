from pyairtable.orm import Model, fields as F
from app.core.config import AIRTABLE_TOKEN, AIRTABLE_BASE_ID

class Bill(Model):
  bill_number = F.TextField("Bill #")
  status = F.SelectField("Status")
  pdf_file = F.AttachmentsField("PDF file")
  pdf_link = F.TextField("PDF Link")
  bill_date = F.DateField("Bill date")
  due = F.TextField("Due")
  service = F.SingleLinkField("Service 🔎", "app.models.Service.Service")
  contaminated = F.NumberField("Contaminated")
  overage = F.NumberField("Overage")
  flags = F.MultipleSelectField("Flags")
  flag_updates = F.MultilineTextField("Flag Updates")
  additional_notes = F.MultilineTextField("Additional notes 🔎")
  bill_amount = F.CurrencyField("Bill amount")
  adjustment = F.CurrencyField("Adjustment")
  calculation = F.CurrencyField("Calculation")
  cost = F.LookupField[float]("Cost 🔎")
  price = F.LookupField[float]("Price 🔎")
  hauler = F.SingleLinkField("Hauler 🔎", "app.models.Hauler.Hauler")
  service_account = F.LookupField[str]("Service Account 🔎")  
  line_items = F.LinkField[str]("Line Items", "LineItem.LineItem")
  invoice_month = F.DatetimeField("Invoice Month")
  terms = F.NumberField("Terms")
  issue_status = F.SelectField("Issue Status")
  last_bill_date = F.LookupField[str]("Last Bill Date 🔎")
  customer = F.SingleLinkField("Customer 🔎", "app.models.Customer.Customer")
  parent_account = F.LookupField[str]("Parent Account 🔎")
  status_service = F.LookupField[str]("Status (from Service) 🔎")
  status_detail = F.TextField("Status detail")
  
  class Meta:
    base_id = AIRTABLE_BASE_ID
    table_name = "Bills"
    api_key = AIRTABLE_TOKEN
