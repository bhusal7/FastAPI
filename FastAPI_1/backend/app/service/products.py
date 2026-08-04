import json
from pathlib import Path
from typing import List, Dict

# use for get the data
DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"


def load_products() -> List[Dict]:
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_all_products() -> List[Dict]:
    return load_products()


#  for to save updated products data into JSON file
# used when product is added, updated, or deleted


# for creating new json
def save_product(products: List[List]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
        # it keeps data in json way


def add_product(product: Dict) -> Dict:
    products = get_all_products()
    if any(p["sku"] == product["sku"] for p in products):
        raise ValueError("SKU already exists")
    products.append(product)
    save_product(products)
    return product


#  for deleting
def remove_product(id: str):
    products = get_all_products()

    for idx, p in enumerate(products):
        if p["id"] == str(id):
            deleted = products.pop(idx)
            save_product(products)  # delete garesi save the garne paryo bache ko

            return {"message": "Product deleted successfully", "data": deleted}


 # for update
# def patch_product(product_id: str, update_data: dict):
#     products = get_all_products()

    # for index, product in enumerate(products):
    #     if product['id'] == product_id:
    #         for key, value in update_data.items():  # it convertsdict into list
    #             if value is None:
    #                 continue

    #         if isinstance(value, dict) and isinstance(product.get(key), dict):
    #             product[key].update(value)
    #         else:
    #             product[key] = value
                
    #     products[index] = product
    #     save_product(products)
    #     return product
    
    # raise ValueError("Product not Found")




def patch_product(product_id: str, payload: dict):

    products = get_all_products()

    for product in products:

        if product["id"] == product_id:

            # recursive update function
            def deep_update(old_data, new_data):

                for key, value in new_data.items():

                    if (
                        isinstance(value, dict)
                        and key in old_data
                        and isinstance(old_data[key], dict)
                    ):

                        deep_update(old_data[key], value)

                    else:
                        old_data[key] = value

            deep_update(product, payload)

            # =========================
            # manually update computed fields
            # =========================

            # final_price
            product["final_price"] = round(
                product["price"] * (1 - product["discount"] / 100),
                2
            )

            # volume
            d = product["image"]["dimensions_cm"]

            product["volume"] = round(
                d["width"] * d["height"] * d["depth"],
                2
            )

            save_product(products)

            return product

    raise ValueError("Product not found")





