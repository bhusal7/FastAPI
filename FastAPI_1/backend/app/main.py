from fastapi import FastAPI, Query, HTTPException, Path, Depends, Request
from app.service.products import (
    get_all_products,
    add_product,
    remove_product,
    patch_product,
    load_products,
)
from app.Schema.Product import Product, ProductUpdate
from uuid import uuid4, UUID
from datetime import datetime,UTC
from typing import Dict
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

load_dotenv()
app = FastAPI()


# for middleWare     , yo HTTP request huda chalcha
@app.middleware("http")
async def lifecycle(request: Request, call_next):

    print("Before Request")
    response = await call_next(request)
    # response["lifecycle"] = "was indide"

    print("After Request")
    return response


# for dependency
def common_logic():
    print("Hello World")
    return "Hello There"


#############
# CRUD      #
############
@app.get(
    "/", response_model=dict
)  # response model helps already abt what program return
def root(dep=Depends(common_logic)):  # use of depends

    DB_PATH = os.getenv("BASE-URL")  # to get env url
    # return {
    #     "message": "welcome to FastAPI",
    #     "dependency": dep,
    #     "data_path": DB_PATH,
    # }  # for env: 'data_path':DB_PATH

    #  -> if U dont use json response then do this but it u use then do: ,
    return JSONResponse(
        status_code=201,
        content={
            "message": "welcome to FastAPI",
            "dependency": dep,
            "data_path": DB_PATH,
        },
    )


@app.get("/products", response_model=Dict)
def list_products(
    dep=Depends(load_products),
    name: str = Query(
        default=None,
        max_length=50,
        min_length=1,
        description="Search by products name (case sensative) ",
        example="Wireless",
    ),
    sort_by_price: bool = Query(
        default=None,
        description="Sort products by Id ",
    ),
    order: str = Query(
        default="asc", description=" Sort order when sort_by_price = true(asc,desc) "
    ),
    # Pagination
    limit: int = Query(
        default=7, ge=1, le=100, description="Number of Items to return"
    ),
    # Offset
    offset: int = Query(default=0, ge=0, description="Pagination Offset"),
):

    # products = get_all_products()     # use this if you dont use Dependy
    products = dep  # use this when u use dependency

    if name:
        needle = name.strip().lower()
        products = [p for p in products if needle in p.get("name", "").lower()]

    if name and not products:
        raise HTTPException(
            status_code=404, detail=f"No product found matching name={name}"
        )

    if sort_by_price:
        reverse = order == "desc"
        products = sorted(products, key=lambda p: p.get("price", 0), reverse=reverse)

    total = len(products)

    # for limit , pagination
    # products = products[0:limit]

    # for offset with limit
    products = products[offset : offset + limit]

    return {"total": total, "limit": limit, "items": products}


@app.get("/products/{product_id}", response_model=Product)
def get_product_by_id(
    product_id: str = Path(
        ...,
        # ge=1,
        description="ID of the products",
        example="input integers (1,2,3.............)",
        # if there is string the id like  in json : id = '12' we write
        # max_length, min-length instead of ge, le : like:
        #  use this if id is string else not:
        max_length=12,
        min_length=12,
    )
):
    products = get_all_products()

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found!")


# @app.post("/products", status_code=201)
# def create_products(product: Product):
#     return product.model_dump(mode="json", by_alias=True)   # to convert dict data on json


# create
@app.post("/products", status_code=201)
def create_products(product: Product):
    product_dict = product.model_dump(mode="json")
    product_dict["id"] = str(uuid4())
    product_dict["created_at"] = datetime.utcnow().isoformat() + "Z"

    try:
        add_product(product_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return product.model_dump(
        mode="json", by_alias=True
    )  # to convert dict data on json


# delete
@app.delete("/products/{product_id}")
def delete_product(product_id: UUID = Path(..., description="Product UUID")):
    try:
        res = remove_product(str(product_id))
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


#  update/ patch/ put
@app.patch("/products/{product_id}")
def update_product(
    product_id: UUID = Path(..., description="Product UUID"),
    payload: ProductUpdate = ...,
):
    try:
        update_product = patch_product(
            str(product_id), payload.model_dump(mode="json", exclude_unset=True)
        )
        # return update_product
        return Product(**update_product)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
