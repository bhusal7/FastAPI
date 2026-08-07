from fastapi import FastAPI, Depends
from database import SessionLocal, engine
import database_models
from models import Product
from database_models import ProductModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=['*']
)

# database_models.Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup():
    try:
        database_models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        print("DB connection failed:", e)


products = [
    Product(id=1, name="Phone", description="A SmartPhone", price=684, quantity=34),
    Product(id=2, name="Laptop", description="A Laptop", price=854542, quantity=4),
    Product(id=3, name="Pen", description="A Pen", price=20, quantity=33),
    Product(id=10, name="Table", description="A Table", price=304, quantity=45),
]


# dependency injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#  for database postsql
def init_db():
    db = SessionLocal()

    # to fetch , using count for query
    count = db.query(database_models.ProductModel).count
    if count == 0:
        for product in products:
            db.add(database_models.ProductModel(**product.model_dump()))

        db.commit()
        db.close()


@app.get("/")
def greet():

    return "Hello World"


@app.get("/products/")
def get_all_products(db: Session = Depends(get_db)):

    # connect the database
    # db = SessionLocal()
    # # query
    # db.query(ProductModel).all()
    db_product = db.query(database_models.ProductModel).all()
    return db_product


@app.get("/products/{id}")
def get_all_products(id: int, db: Session = Depends(get_db)):
    # for product in products:
    #     if product.id == id:
    #         return product
    # return "product not found"
    db_product = (
        db.query(database_models.ProductModel)
        .filter(database_models.ProductModel.id == id)
        .first()
    )
    if db_product:
        return db_product
    return "product not found"


# @app.post("/products/")
# def post_product(product: Product):
#     products.append(product)
#     return product
@app.post("/products/")
def post_product(product: Product, db: Session = Depends(get_db)):
    db.add(database_models.ProductModel(**product.model_dump()))
    db.commit()
    return product


# @app.patch("/products/{id}")
# def update_product(id: int, updated_product: Product):
#     for product in products:
#         if product.id == id:
#             product.name = updated_product.name
#             product.description = updated_product.description
#             product.price = updated_product.price
#             product.quantity = updated_product.quantity
#             return "product update successfully"
#     return "no product found"


@app.patch("/products/{id}")
def update_product(id: int, updated_product: Product, db: Session = Depends(get_db)):
    db_product = (
        db.query(database_models.ProductModel)
        .filter(database_models.ProductModel.id == id)
        .first()
    )
    if db_product:
        db_product.name = updated_product.name
        db_product.description = updated_product.description
        db_product.price = updated_product.price
        db_product.quantity = updated_product.quantity
        db.commit()
        return "product update successfully"
    else:
        return "no product found"


# @app.delete("/products/{id}")
# def delete_product(id: int):
#     for i, product in enumerate(products):
#         if product.id == id:
#             products.pop(i)
#             return "product delete successfully"
#     return "no product found"


@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = (
        db.query(database_models.ProductModel)
        .filter(database_models.ProductModel.id == id)
        .first()
    )
    if db_product:
        db.delete(db_product)
        db.commit()
        return "product delete successfully"

    else:
        return "no product found"
