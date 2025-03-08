import os

# CSV File Path
CSV_FILE = "airdrops.csv"

# Conversation States
(AIRDROP_NAME, STATUS, TYPE, TUYUL, NOTES, RESULT, EDIT_SELECT, EDIT_FIELD, EDIT_VALUE) = range(9)

# Options
STATUS_OPTIONS = [["Dalam proses", "Selesai", "Pending"]]
TYPE_OPTIONS = [["Mini App", "Others", "Premint", "Testnet", "Waitlist"]]
TUYUL_OPTIONS = [["✅ Yes", "❌ No"]]

# List of Tuyul Accounts
TUYUL_ACCOUNTS = [f"Tuyul {i}" for i in range(1, 8)]  # Tuyul1 - Tuyul7

# Command options
COMMAND_OPTIONS = [["/add", "/edit", "/remove", "/progress"]]

# Edit field options
EDIT_FIELD_OPTIONS = [["Status", "Type", "Notes", "Result"] + TUYUL_ACCOUNTS]
