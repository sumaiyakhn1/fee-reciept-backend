# main.py

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sheet import read_all_tabs
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Fee Receipt API Running"}


# ------------------------------------------------
# VISITOR COUNTER (START FROM 95)
# ------------------------------------------------

COUNTER_FILE = "counter.txt"

def read_counter():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("95")  # start from 95
        return 95

    with open(COUNTER_FILE, "r") as f:
        try:
            return int(f.read().strip() or 95)
        except:
            return 95

def write_counter(val):
    with open(COUNTER_FILE, "w") as f:
        f.write(str(val))

@app.get("/visit")
def visit_counter():
    count = read_counter() + 1
    write_counter(count)
    return {"visitors": count}


# -------------------------
# SEARCH (name, adm, phone)
# -------------------------
@app.get("/search")
def search_receipts(query: str = Query(..., min_length=1)):
    q = query.lower()
    data = read_all_tabs()
    results = []

    for row in data:
        name = str(row.get("Student's Name", "")).lower()
        adm = str(row.get("Adm No", "")).lower()
        phone = str(row.get("Mobile No", "")).lower()

        if q in name or q in adm or q in phone:
            results.append(row)

    return {"count": len(results), "results": results}


# -------------------------------------
#  FEE HEADS TO EXTRACT
# -------------------------------------
FEE_HEAD_COLUMNS = [
    "DEVELOPMENT CHARGE",
    "TUITION FEE",
    "SMART CLASS, ACTIVITY CHARGE",
    "COMPUTER FEE",
    "PRACTICAL CHARGES",
    "Transport Fee",
    "Board Examination. Fee",
    "Admission Fee (Non Refundable)",
    "Registration Fee (Non Refundable)",
    "Prospectus Fee",
    "Hostel",
]

def amount_in_words(num):
    import num2words
    return num2words.num2words(num, lang="en_IN").upper() + " ONLY"


# -------------------------------------
#  FORMAT RECEIPT FROM A ROW
# -------------------------------------
def format_receipt(row):

    fee_items = []
    total_amount = 0

    for head in FEE_HEAD_COLUMNS:
        raw = str(row.get(head, "")).strip()
        if raw == "":
            continue

        try:
            val = float(raw.replace(",", ""))
        except:
            val = 0

        if val > 0:
            fee_items.append({"fee_head": head, "amount": val})
            total_amount += val

    return {
        "receipt_no": row.get("Receipt"),
        "admission_no": row.get("Adm No"),
        "student_name": row.get("Student's Name"),
        "father_name": row.get("Father Name"),
        "mobile": row.get("Mobile No"),
        "aadhar": row.get("Student Aadhar No"),
        "address": row.get("Address"),
        "course": row.get("Course"),
        "roll_no": row.get("Roll No"),
        "status": row.get("Academic Status"),
        "caste": row.get("Caste Category"),
        "session": row.get("session"),
        "date": row.get("Transaction Date"),

        "fee_items": fee_items,
        "fee_total": total_amount,
        "fee_total_words": amount_in_words(total_amount),

        "paid_amount": row.get("Amount"),
        "method": row.get("Method"),
        "payment_details": row.get("Payment Details"),
        "remarks": row.get("Remarks"),

        "user": row.get("User"),
    }


# -------------------------------------
# VIEW RECEIPT BY ADMISSION NO
# -------------------------------------
@app.get("/receipt/adm/{adm_no}")
def receipt_by_adm(adm_no: str):

    data = read_all_tabs()

    row = None
    for r in data:
        if str(r.get("Adm No", "")).strip() == adm_no.strip():
            row = r
    if not row:
        raise HTTPException(404, "Receipt not found")

    return format_receipt(row)
