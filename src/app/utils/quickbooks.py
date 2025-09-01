from sqlalchemy.orm import Session

from quickbooks.objects.vendor import Vendor
from quickbooks.objects.account import Account
from quickbooks.objects.customer import Customer
from quickbooks.objects.account import Account
from quickbooks.objects.department import Department

from ..database.models.QuickBooksToken import QboConnection
from ..core.exceptions import BusinessValidationError, NotFoundDomainError


# Get the default company ID from the database
def _get_default_company_id(db: Session) -> str:
    row = db.query(QboConnection).first()
    if not row:
        raise BusinessValidationError("No QuickBooks connection found in the system.")
    return row.realm_id

# Escape QuickBooks special characters in strings
def _escape_qb(value: str) -> str:
    if isinstance(value, str):
        return value.replace("'", "''") if value else value
    return str(value)

def _get_vendor(qb, vendor_id: str) -> Vendor:
    res = Vendor.where(f"Id = '{_escape_qb(vendor_id)}'", qb=qb)
    if not res:
      raise NotFoundDomainError(f"Vendor (Hauler) '{vendor_id}' not found in QuickBooks.")  
    return res[0]


def _get_customer_by_display_name(qb, display_name: str):
  # A display name of the customer comes like "XXXXXXX - A-####" 
  # the search has to find the part of the display name that
  # only contains "A-####" it has to ignore the name "XXXXXXX - " part
  search_term = display_name.split(" - ")[-1]
  query = f"DisplayName LIKE '%{_escape_qb(search_term)}%'"
  customers = Customer.where(query, qb=qb)
  if not customers:
      raise NotFoundDomainError(f"Customer with display name {display_name} not found.")
  return customers[0]

def get_department_from_service_account(qb, service_account_id: str) -> Department:
  #A departament has a name, the name comes like "XXXXX, service_account_id"
  # the search has to find the part of name that only contains the service_account_id
  #before the comma and the space
  departments = Department.where(f"Name LIKE '%{_escape_qb(service_account_id)}%'", qb=qb)
  if not departments:
      raise NotFoundDomainError(f"No department found for service account {service_account_id}")
  return departments[0]
