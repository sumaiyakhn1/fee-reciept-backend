# main.py

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sheet import read_all_tabs


app = FastAPI()

# Allow frontend access
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


# -----------------------------------------------
#       SEARCH ENDPOINT (Name / AdmNo / Phone)
# -----------------------------------------------

@app.get("/search")
def search_receipts(query: str = Query(..., min_length=1)):

    q = query.lower()
    data = read_all_tabs()
    results = []

    for row in data:
        name = str(row.get("Student's Name", "")).lower()
        adm_no = str(row.get("Adm No", "")).lower()
        mobile = str(row.get("Mobile No", "")).lower()

        if q in name or q in adm_no or q in mobile:
            results.append(row)

    return {"count": len(results), "results": results}


# -----------------------------------------------
#      RECEIPT JSON FORMATTER (fee heads > 0)
# -----------------------------------------------

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


def amount_in_words(n: int):
    """Very simple number-to-words for receipts."""
    import num2words
    return num2words.num2words(n, to="currency", lang="en_IN")


@app.get("/receipt/{receipt_no}")
def get_receipt(receipt_no: str):

    all_rows = read_all_tabs()

    # Find matching row
    row = None
    for r in all_rows:
        if str(r.get("Receipt", "")).lower() == receipt_no.lower():
            row = r
            break

    if row is None:
        raise HTTPException(status_code=404, detail="Receipt not found")

    # Extract fee heads > 0
    fee_items = []
    total_amount = 0

    for head in FEE_HEAD_COLUMNS:
        raw_value = row.get(head, "").strip()
        if raw_value == "":
            continue

        try:
            numeric = float(raw_value.replace(",", ""))
        except:
            numeric = 0

        if numeric > 0:
            fee_items.append({
                "fee_head": head,
                "amount": numeric
            })
            total_amount += numeric

    # Final formatted receipt
    formatted = {
        "receipt_no": row.get("Receipt"),
        "session": row.get("session"),
        "date": row.get("Transaction Date"),
        "admission_no": row.get("Adm No"),
        "student_name": row.get("Student's Name"),
        "father_name": row.get("Father Name"),
        "mobile": row.get("Mobile No"),
        "course": row.get("Course"),
        "roll_no": row.get("Roll No"),

        # fee table
        "fee_items": fee_items,
        "total_fee_amount": total_amount,
        "total_fee_amount_words": amount_in_words(total_amount),

        # payment
        "paid_amount": row.get("Amount"),
        "method": row.get("Method"),
        "payment_details": row.get("Payment Details"),
        "remarks": row.get("Remarks"),

        # footer
        "user": row.get("User"),
    }

    return formatted
