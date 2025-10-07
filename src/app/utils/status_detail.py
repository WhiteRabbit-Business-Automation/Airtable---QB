#Example Status Detail
# ----------- START: Logged at 2025-01-29 16:01:07 -----------

# Process: PDF to AirTable  

# Name: Problem updating record in AirTable  

# Dropped File Link: https://drive.google.com/file/d/18-fL8fE5WpvDHPCvoQIKfGySxB8LDJNJ/view?usp=drivesdk  

# Status: Previous/Latest Bill Record Not Found

# Details:  

# There was a problem updating the dropped bill 0320-004595675.



# Actions:  

# Drop the file again, if the error persist call your system Admin.


# ----------- END: Logged at 2025-01-29 16:01:07 -----------

from dataclasses import dataclass, field


@dataclass
class StatusDetail:
  logg_at: str
  file_link: str
  status: str
  detail: str
  
  actions: list[str] = field(default_factory=list)
  process: str = "Airtable to Quickbooks"

  def __str__(self) -> str:
    actions_str = "\n\t".join(f"{i + 1}. {action} " for i, action in enumerate(self.actions)) if self.actions else ""
    return (
      f" ----------- START: Started at {self.logg_at} -----------\n\n"
      f"** Process: {self.process}  **\n\n"
      f"** File: {self.file_link}  **\n\n"
      f"** ⚠️ Issue: {self.status}**\n\n"
      f"** What this means:  **\n\n"
      f"** {self.detail}**\n\n"
      f"** Next steps for you:  **\n\n"
      f"{actions_str}**\n\n"
      f" ----------- END: Finished at {self.logg_at} -----------**"
    )
  