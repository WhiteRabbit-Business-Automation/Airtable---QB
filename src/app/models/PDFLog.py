from pyairtable.orm import Model, fields as F
from ..core.config import AIRTABLE_TOKEN, AIRTABLE_BASE_ID

class PDFLog(Model):
  name = F.TextField("Name")
  pdf_file = F.UrlField("PDF")
  status = F.MultipleSelectField("Status")
  details = F.MultilineTextField("Details")
  created_time_field = F.CreatedTimeField("Created Time")
  created_date_field = F.CreatedTimeField("Created Datea")
  tech_details = F.MultilineTextField("Technical details")
  action = F.MultipleSelectField("Action")  
  
  class Meta:
    base_id = AIRTABLE_BASE_ID
    table_name = "PDF Log"
    api_key = AIRTABLE_TOKEN