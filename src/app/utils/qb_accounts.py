SERVICE_TYPE_TO_QB_ACCOUNT = {
    "Trash": "122",  # Trash Removal (Exp.):Trash (Exp.) [COGS]
    "Roll off (move to tempo or monthly)": "142",  # Rolloff (Exp.) [COGS]
    "Roll off - Monthly": "142",
    "Roll off - Temp": "142",
    "Compactor": "122",
    "Recycling": "54",   # Cost of Goods Sold
    "Misc": "47",        # Ask My Accountant (Other Expense)
}

# Fallback de seguridad por si falta mapeo o la cuenta está inválida
DEFAULT_EXPENSE_ACCOUNT_ID = "47"  # Ask My Accountant (Other Expense)
