from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class LoanApplication(BaseModel):
    name : str
    age : int 
    income : float
    loan_amount : float
    employment_years : int
    
@app.post("/predict")
def predict_loan(application : LoanApplication):
    
    # model login
    approved = (
        application.income > 50000 and
        application.employment_years > 2 and
        application.age >= 21
    )
    
    return {
        "application_name" : application.name,
        "loan_amount" : application.loan_amount,
        "decision" : "approved" if approved else "rejected",
        "review_income" : application.income
    }