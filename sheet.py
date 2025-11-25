import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


# === READ ONE TAB ===
def read_sheet(tab_name: str):
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/"
        f"{SPREADSHEET_ID}/values/{tab_name}!A:Z?key={API_KEY}"
    )
    resp = requests.get(url).json()
    return resp.get("values", [])


# === GET TAB NAMES ===
def get_sheet_tabs():
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}?key={API_KEY}"
    resp = requests.get(url).json()
    sheets = resp.get("sheets", [])
    return [s["properties"]["title"] for s in sheets]


# === READ ALL TABS ===
def read_all_tabs():
    all_data = []
    tabs = get_sheet_tabs()

    for tab in tabs:
        rows = read_sheet(tab)
        if len(rows) < 2:
            continue

        headers = rows[0]
        for row in rows[1:]:
            entry = {}
            for i, header in enumerate(headers):
                entry[header] = row[i] if i < len(row) else ""

            entry["session"] = tab  # add session field
            all_data.append(entry)

    return all_data
