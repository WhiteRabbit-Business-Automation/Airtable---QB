from pyairtable.orm import Model, fields as F
from ..core.config import AIRTABLE_TOKEN, AIRTABLE_BASE_ID

class LineItem(Model):
  line_description = F.TextField("Line Description")
  line_amount = F.TextField("Line Amount")
  quantity = F.TextField("Quantity")
  line_date = F.TextField("Line Date")
  total_current_changes = F.TextField("Total Current Changes")
  service_location_address = F.TextField("Service Location Address")
  bills_numbers = F.LinkField[str]("Bills #", "app.models.Bill.Bill")
  created_at = F.DatetimeField("Created")
  id = F.AutoNumberField("Id",readonly=True)
  
  class Meta: 
    base_id = AIRTABLE_BASE_ID
    table_name = "Line Items"
    api_key = AIRTABLE_TOKEN