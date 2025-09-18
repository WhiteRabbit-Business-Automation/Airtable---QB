#PROD
# SERVICE_TYPE_TO_QB_ACCOUNT = {
#     "Trash": "122",  # Trash Removal (Exp.):Trash (Exp.) [COGS]
#     "Roll off (move to tempo or monthly)": "142",  # Rolloff (Exp.) [COGS]
#     "Roll off - Monthly": "142",
#     "Roll off - Temp": "142",
#     "Compactor": "122",
#     "Recycling": "122",   
#     "Misc": "122",        
# }

# Fallback de seguridad por si falta mapeo o la cuenta está inválida
# DEFAULT_EXPENSE_ACCOUNT_ID = "47"  # Ask My Accountant (Other Expense)
# DEFAULT_TRASH_EXPENSE_ACCOUNT_ID = "122"  # # Trash Removal (Exp.):Trash (Exp.) [COGS]

# #DEV
SERVICE_TYPE_TO_QB_ACCOUNT = {
    "Trash": "1150040001",
    "Roll off (move to tempo or monthly)": "1150040001",
    "Roll off - Monthly": "1150040001",
    "Roll off - Temp": "1150040001",
    "Compactor": "1150040001",
    "Recycling": "1150040001",
    "Misc": "14",  # Miscellaneous
}
# # # Fallback de seguridad por si falta mapeo o la cuenta está inválida
DEFAULT_TRASH_EXPENSE_ACCOUNT_ID = "1150040001"  # Trash Removal (Exp.):Trash (Exp.) [COGS]
