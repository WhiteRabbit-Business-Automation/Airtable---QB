from pyairtable.orm import Model, fields as F
from app.core.config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID

class LineItem(Model):
  line_description = F.TextField("Line Description")
  line_amount = F.NumberField("Line Amount")
  quantity = F.TextField("Quantity")
  line_date = F.TextField("Line Date")
  total_current_changes = F.TextField("Total Current Changes")
  service_location_address = F.TextField("Service Location Address")
  bills_numbers = F.SingleLinkField[str]("Bills Numbers", "Bill.Bill")
  created_at = F.DatetimeField("Created")
  id = F.AutoNumberField("Id",readonly=True)
  
  class Meta: 
    base_id = AIRTABLE_BASE_ID
    table_name = "Line Items"
    api_key = AIRTABLE_API_KEY