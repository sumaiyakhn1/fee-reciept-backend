from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sheet import read_all_tabs

app = FastAPI()

# CORS for your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Fee Receipt API running"}


@app.get("/search")
def search_receipts(query: str = Query(..., min_length=1)):
    query = query.lower()

    data = read_all_tabs()
    results = []

    for row in data:
        name = row.get("Student's Name", "").lower()
        id_ = row.get("ID", "").lower()
        mobile = row.get("Mobile No", "").lower()

        if query in name or query in id_ or query in mobile:
            results.append(row)

    return {"count": len(results), "results": results}
