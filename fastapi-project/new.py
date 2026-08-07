from fastapi import FastAPI

app = FastAPI()

all_customers = [
    {"id":101, "name":"Ram", "city":"Btl", "risk":"low"},
    {"id":102, "name":"Shyam", "city":"ktm", "risk":"medium"},
    {"id":103, "name":"Om", "city":"kpl", "risk":"high"},
    {"id":104, "name":"Krsna", "city":"pkr", "risk":"low"},
    {"id":105, "name":"Hari", "city":"Btl", "risk":"low"},
]

@app.get("/customers")
def get_customers(city: str, risk: str):
    filtered = [
        c
        for c in all_customers
        if c["city"] == city and c["risk"] == risk
    ]

    return {
        "city": city,
        "risk": risk,
        "count": len(filtered),
        "result": filtered
    }