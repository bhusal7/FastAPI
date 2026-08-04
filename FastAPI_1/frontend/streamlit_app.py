import streamlit as st
import requests
from datetime import datetime, UTC

# ======================================
# CONFIG
# ======================================

st.set_page_config(page_title="Ecommerce Dashboard", page_icon="🛒", layout="wide")

API_URL = "http://127.0.0.1:8000"

# ======================================
# CSS
# ======================================

st.markdown(
    """
<style>

.stApp {
    background: #0f172a;
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.main-title {
    font-size: 60px;
    font-weight: bold;
    text-align: center;
    color: white;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 40px;
}

.card {
    background: #1e293b;
    padding: 25px;
    border-radius: 20px;
    margin-bottom: 20px;
    border: 1px solid #334155;
}

.price {
    color: #22c55e;
    font-size: 28px;
    font-weight: bold;
}

.tag {
    background: #334155;
    padding: 5px 12px;
    border-radius: 30px;
    margin-right: 5px;
}

hr {
    border-color: #334155;
}

</style>
""",
    unsafe_allow_html=True,
)

# ======================================
# HEADER
# ======================================

st.markdown(
    "<div class='main-title'>🛒 Ecommerce Dashboard</div>", unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>FastAPI + Streamlit Modern UI</div>", unsafe_allow_html=True
)

# ======================================
# SIDEBAR
# ======================================

st.sidebar.title("🔍 Filters")

search = st.sidebar.text_input("Search Product")

sort_order = st.sidebar.selectbox("Sort Price", ["None", "Low to High", "High to Low"])

limit = st.sidebar.slider("Limit", 1, 20, 10)

# ======================================
# API PARAMS
# ======================================

params = {"limit": limit, "offset": 0}

if search:
    params["name"] = search.lower()

if sort_order == "Low to High":
    params["sort_by_price"] = True
    params["order"] = "asc"

elif sort_order == "High to Low":
    params["sort_by_price"] = True
    params["order"] = "desc"

# ======================================
# FETCH PRODUCTS
# ======================================

st.subheader("📦 Products")

try:

    response = requests.get(f"{API_URL}/products", params=params)

    if response.status_code == 200:

        data = response.json()

        products = data["items"]

        st.success(f"Total Products: {data['total']}")

        cols = st.columns(2)

        for index, product in enumerate(products):

            with cols[index % 2]:

                tags_html = ""

                for tag in product.get("tags", []):
                    tags_html += f"<span class='tag'>{tag}</span>"

                st.markdown(
                    f"""
                <div class="card">

                <h2>{product['name']}</h2>

                <p>
                {product['brand']} • {product['category']}
                </p>

                <div class="price">
                ${product['final_price']}
                </div>

                <p>
                Discount: {product['discount']}%
                </p>

                <p>
                ⭐ {product['rating']}
                </p>

                <p>
                {product['description']}
                </p>

                <hr>

                <p>
                📦 Stock: {product['stock']}
                </p>

                <p>
                🚚 Delivery: {product['shipping']['estimated_delivery_days']} days
                </p>

                <p>
                🏪 Seller: {product['seller']['name']}
                </p>

                <p>
                📍 {product['seller']['location']}
                </p>

                <p>
                {tags_html}
                </p>

                <hr>

                <p>
                🆔 {product['id']}
                </p>

                </div>
                """,
                    unsafe_allow_html=True,
                )

    else:
        st.error(response.text)

except Exception as e:
    st.error(f"Backend Error: {e}")

# ======================================
# CREATE PRODUCT
# ======================================

st.divider()

st.subheader("➕ Create Product")

with st.form("create_product"):

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Name")
        brand = st.text_input("Brand")
        category = st.text_input("Category")
        sku = st.text_input("SKU", "WM-LOGI-123")
        price = st.number_input("Price", min_value=1.0)

    with col2:
        stock = st.number_input("Stock", min_value=0)
        discount = st.number_input("Discount", min_value=0.0)
        rating = st.number_input("Rating", 0.0, 5.0)
        currency = st.selectbox("Currency", ["USD", "NPR", "INR"])

    description = st.text_area("Description")

    create_btn = st.form_submit_button("Create Product")

    if create_btn:

        payload = {
            "id": "00000000-0000-0000-0000-000000000000",
            "sku": sku,
            "name": name,
            "category": category,
            "brand": brand,
            "price": price,
            "currency": currency,
            "stock": stock,
            "discount": discount,
            "rating": rating,
            "description": description,
            "seller": {
                "name": "MI Store",
                "email": "admin@mistore.in",
                "website": "https://mistore.in",
                "location": "Nepal",
                "verified": True,
            },
            "shipping": {"free_shipping": True, "estimated_delivery_days": 5},
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
            "is_active": True,
            "tags": ["new"],
            "image": {
                "url": "https://picsum.photos/300",
                "alt": "product image",
                "dimensions_cm": {"width": 10, "height": 10, "depth": 10},
            },
        }

        create_response = requests.post(f"{API_URL}/products", json=payload)

        if create_response.status_code in [200, 201]:
            st.success("✅ Product Created Successfully")
            st.rerun()

        else:
            st.error(create_response.text)

# ======================================
# UPDATE PRODUCT
# ======================================

st.divider()

st.subheader("✏️ Update Product")

with st.form("update_form"):

    product_id = st.text_input("Product UUID")

    update_price = st.number_input("New Price", min_value=0.0)

    update_stock = st.number_input("New Stock", min_value=0)

    update_discount = st.number_input("New Discount", min_value=0.0)

    update_btn = st.form_submit_button("Update Product")

    if update_btn:

        payload = {
            "price": update_price,
            "stock": update_stock,
            "discount": update_discount,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }

        res = requests.patch(f"{API_URL}/products/{product_id}", json=payload)

        if res.status_code == 200:
            st.success("✅ Product Updated")
            st.rerun()

        else:
            st.error(res.text)

# ======================================
# DELETE
# ======================================

st.divider()

st.subheader("🗑 Delete Product")

delete_id = st.text_input("Delete UUID")

if st.button("Delete"):

    delete_res = requests.delete(f"{API_URL}/products/{delete_id}")

    if delete_res.status_code == 200:
        st.success("Deleted Successfully")
        st.rerun()

    else:
        st.error(delete_res.text)
