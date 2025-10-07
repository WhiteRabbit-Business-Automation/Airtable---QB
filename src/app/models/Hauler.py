from pyairtable.orm import Model, fields as F

from ..core.config import AIRTABLE_TOKEN, AIRTABLE_BASE_ID


class Hauler(Model):
  name = F.TextField("Name")
  email = F.EmailField("Email")
  phone = F.PhoneNumberField("Phone #")
  terms_days = F.NumberField("Terms (days)")
  customers = F.LinkField[str]("Customers 🔎", "app.models.Customer.Customer")
  number_customers = F.CountField("# Customers 🔎")
  name_lower_case = F.TextField("Name Lower case", readonly=True)
  hauler_ai_instruction = F.MultilineTextField("Hauler AI Instruction", readonly=True)
  instruction_notes = F.TextField("Instruction Notes", readonly=True)
  hauler_number = F.TextField("H#")


  class Meta:
    base_id = AIRTABLE_BASE_ID
    table_name = "Haulers"
    api_key = AIRTABLE_TOKEN
