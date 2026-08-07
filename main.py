from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"messages":"My first API is working"}


@app.get("/about")
def about():
    return {"project":"loan risk model","verson":"1.0"}


@app.get("/customer")
def get_customer(customer_id:int):
    return {
        "customer_id": customer_id,
        "name":"Ram",
        "status":"active"
    }