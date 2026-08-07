# 2.  post
#   Create Pydantic

# use of pydantic validation

from pydantic import BaseModel, Field, AnyUrl, EmailStr
from typing import Annotated, Literal, Optional, List
from uuid import UUID
from datetime import datetime,UTC

# for validation
from pydantic import field_validator, model_validator, computed_field


#  for image, dimension, seller ,shipping
# nested baseModel PYdantic
class Dimension(BaseModel):
    width: float
    height: float
    depth: float


class Image(BaseModel):
    url: AnyUrl = Field(
        ...,
        description="Image URL",
        example="https://example.com/images/mouse.jpg",
    )

    alt: str = Field(
        ...,
        description="Alternative text of image",
        example="Wireless ergonomic mouse",
    )
    dimensions_cm: Dimension = Field(
        ...,
        description="Dimensions of image in centimeters",
    )


class Seller(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=5,
            max_length=50,
            title="Seller Name",
            description="Name of the seller (2-60 chars) ",
            examples=["MI store, Apple store"],
        ),
    ]
    email: EmailStr

    @field_validator("email", mode="after")
    @classmethod
    def validate_seller_email_domain(cls, value: EmailStr):
        allowed_domains = [
            "mistore.in",
            "hpworld.in",
            "techstore.com",
            "keyboardhub.com",
            "sportzone.com",
            "mobileworld.com",
            "audiomart.com",
        ]

        domain = str(value).split("@")[-1].lower()
        if domain not in allowed_domains:
            raise ValueError(f" Seller email does not allowed: {domain} ")
        return value

    website: AnyUrl
    location: str = Field(examples=["Kapilvastu,Birpur"])
    verified: bool = Field(examples=["True or False"])


class Shipping(BaseModel):
    free_shipping: bool = Field(examples=["True or False"])
    estimated_delivery_days: int


# Main is this:
class Product(BaseModel):
    id: UUID

    sku: Annotated[
        str,
        Field(
            ...,
            min_length=5,
            max_length=20,
            title="Stock Keeping Unit",
            description="Unique product identifier (SKU)",
            examples=["WM-LOGI-001"],
        ),
    ]

    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=50,
            title="Product Name",
            description="Name of the product",
            examples=["Wireless Mouse"],
        ),
    ]

    category: Annotated[
        str,
        Field(
            min_length=3,
            max_length=30,
            title="Category",
            description="Category of the product",
            examples=["Electronics"],
        ),
    ]
    brand: Annotated[
        str,
        Field(
            min_length=2,
            max_length=30,
            title="Brand",
            description="Brand name of the product",
            examples=["LogiTech"],
        ),
    ]

    price: Annotated[
        float,
        Field(
            gt=0,
            title="Price",
            description="Price of the product",
            examples=[25.99],
        ),
    ]

    currency: Annotated[
        Literal["USD", "NPR", "INR"],
        Field(
            title="Currency",
            description="Currency type of the product",
            examples=["USD"],
        ),
    ]

    stock: Annotated[
        int,
        Field(
            ge=0,
            le=1000,
            title="Stock",
            description="Available stock quantity",
            examples=[120],
        ),
    ]

    discount: Annotated[
        float,
        Field(
            ge=0,
            le=100,
            title="Discount",
            description="Discount percentage applied to the product",
            examples=[10],
        ),
    ]

    rating: Annotated[
        float,
        Field(
            ge=0,
            le=5,
            title="Rating",
            description="Product rating out of 5",
            examples=[4.5],
        ),
    ]

    description: Annotated[
        str,
        Field(
            min_length=10,
            max_length=200,
            title="Description",
            description="Detailed information about the product",
            examples=["Ergonomic wireless mouse with USB receiver."],
        ),
    ]

    seller: Annotated[Seller, Field(..., description="Details of Seller")]

    shipping: Annotated[Shipping, Field(..., description="About Shipping")]

    created_at: Annotated[
        datetime,
        Field(
            title="Created At",
            description="Product creation date and time",
            examples=["2026-05-26T10:15:30Z"],
        ),
    ]

    updated_at: Annotated[
        datetime,
        Field(
            title="Updated At",
            description="Last updated date and time",
            examples=["2026-05-26T11:20:00Z"],
        ),
    ]

    is_active: Annotated[
        bool,
        Field(
            title="Active Status",
            description="Whether the product is active or not",
            examples=[True],
        ),
    ]

    tags: Annotated[
        Optional[List[str]],
        Field(default=None, max_length=10, description="Upto 10 tags"),
    ]

    image: Annotated[Image, Field(description="Product Image Object")]

    # making field

    # field validator works in only 1 field

    @field_validator("sku", mode="after")
    @classmethod
    def validate_sku_format(cls, value: str):
        if "-" not in value:
            raise ValueError("Sku must have '-")

        last = value.split("-")[-1]
        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("Sku must end with 3- digit sequence like -354")

        return value

    # but model_validator works in multiple field
    @model_validator(mode="after")
    @classmethod
    def validate_business_rules(cls, model: "Product"):
        if model.stock == 0 and model.is_active is True:
            raise ValueError("If stock is Zero Active must be false")

        if model.discount > 0 and model.rating == 0:
            raise ValueError("Discounted price must have the a rating (rating != 0) ")

        return model

    # computed field
    #  to find final price,
    # OP = Original Price
    # D = Discount %
    # FP = Final Price
    # FP = Original Price - Discount
    @computed_field  # it add a new field ,its decorator
    @property
    def final_price(self) -> float:
        return round(self.price * (1 - self.discount / 100), 2)

    @computed_field
    @property
    def volume(self) -> float:
        d = self.image.dimensions_cm
        return round(d.width * d.height * d.depth, 2)


# =========================
# UPDATE Pydantic
# =========================


# Dimension Update
class DimensionUpdate(BaseModel):
    width: Optional[float] = None
    height: Optional[float] = None
    depth: Optional[float] = None


# Image Update
class ImageUpdate(BaseModel):
    url: Optional[AnyUrl] = Field(
        default=None,
        description="Updated image URL",
        examples=["https://example.com/new-image.jpg"],
    )

    alt: Optional[str] = Field(
        default=None,
        description="Updated alt text",
        examples=["Updated wireless mouse image"],
    )

    dimensions_cm: Optional[DimensionUpdate] = Field(
        default=None,
        description="Updated dimensions",
    )


# Seller Update
class SellerUpdate(BaseModel):
    name: Optional[
        Annotated[
            str,
            Field(
                min_length=5,
                max_length=50,
                title="Seller Name",
                description="Updated seller name",
                examples=["MI Store"],
            ),
        ]
    ] = None

    email: Optional[EmailStr] = None

    @field_validator("email", mode="after")
    @classmethod
    def validate_seller_email_domain(cls, value):
        if value is None:
            return value

        allowed_domains = [
            "mistore.in",
            "hpworld.in",
            "techstore.com",
            "keyboardhub.com",
            "sportzone.com",
            "mobileworld.com",
            "audiomart.com",
        ]

        domain = str(value).split("@")[-1].lower()

        if domain not in allowed_domains:
            raise ValueError(f"Seller email domain not allowed: {domain}")

        return value

    website: Optional[AnyUrl] = None

    location: Optional[str] = Field(
        default=None,
        examples=["Kapilvastu, Birpur"],
    )

    verified: Optional[bool] = Field(
        default=None,
        examples=[True],
    )


# Shipping Update
class ShippingUpdate(BaseModel):
    free_shipping: Optional[bool] = Field(
        default=None,
        examples=[True],
    )

    estimated_delivery_days: Optional[int] = Field(
        default=None,
        ge=1,
        le=30,
        examples=[5],
    )


# =========================
# PRODUCT UPDATE MODEL
# =========================


class ProductUpdate(BaseModel):

    sku: Optional[
        Annotated[
            str,
            Field(
                min_length=5,
                max_length=20,
                title="Stock Keeping Unit",
                description="Updated SKU",
                examples=["WM-LOGI-001"],
            ),
        ]
    ] = None

    name: Optional[
        Annotated[
            str,
            Field(
                min_length=3,
                max_length=50,
                title="Product Name",
                description="Updated product name",
                examples=["Wireless Mouse"],
            ),
        ]
    ] = None

    category: Optional[
        Annotated[
            str,
            Field(
                min_length=3,
                max_length=30,
                title="Category",
                description="Updated category",
                examples=["Electronics"],
            ),
        ]
    ] = None

    brand: Optional[
        Annotated[
            str,
            Field(
                min_length=2,
                max_length=30,
                title="Brand",
                description="Updated brand",
                examples=["Logitech"],
            ),
        ]
    ] = None

    price: Optional[
        Annotated[
            float,
            Field(
                gt=0,
                title="Price",
                description="Updated price",
                examples=[29.99],
            ),
        ]
    ] = None

    currency: Optional[
        Annotated[
            Literal["USD", "NPR", "INR"],
            Field(
                title="Currency",
                description="Updated currency",
                examples=["USD"],
            ),
        ]
    ] = None

    stock: Optional[
        Annotated[
            int,
            Field(
                ge=0,
                le=1000,
                title="Stock",
                description="Updated stock quantity",
                examples=[50],
            ),
        ]
    ] = None

    discount: Optional[
        Annotated[
            float,
            Field(
                ge=0,
                le=100,
                title="Discount",
                description="Updated discount percentage",
                examples=[15],
            ),
        ]
    ] = None

    rating: Optional[
        Annotated[
            float,
            Field(
                ge=0,
                le=5,
                title="Rating",
                description="Updated rating",
                examples=[4.7],
            ),
        ]
    ] = None

    description: Optional[
        Annotated[
            str,
            Field(
                min_length=10,
                max_length=200,
                title="Description",
                description="Updated product description",
                examples=["Updated ergonomic wireless mouse"],
            ),
        ]
    ] = None

    seller: Optional[SellerUpdate] = Field(
        default=None,
        description="Updated seller details",
    )

    shipping: Optional[ShippingUpdate] = Field(
        default=None,
        description="Updated shipping details",
    )

    updated_at: Optional[
        Annotated[
            datetime,
            Field(
                title="Updated At",
                description="Last updated date",
                examples=["2026-05-26T11:20:00Z"],
            ),
        ]
    ] = None

    is_active: Optional[
        Annotated[
            bool,
            Field(
                title="Active Status",
                description="Updated active status",
                examples=[True],
            ),
        ]
    ] = None

    tags: Optional[
        Annotated[
            List[str],
            Field(
                max_length=10,
                description="Updated tags",
            ),
        ]
    ] = None

    image: Optional[ImageUpdate] = Field(
        default=None,
        description="Updated product image",
    )

    # =========================
    # FIELD VALIDATOR
    # =========================

    @field_validator("sku", mode="after")
    @classmethod
    def validate_sku_format(cls, value):

        if value is None:
            return value

        if "-" not in value:
            raise ValueError("SKU must contain '-'")

        last = value.split("-")[-1]

        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("SKU must end with 3 digit number like -354")

        return value

    # =========================
    # MODEL VALIDATOR
    # =========================

    @model_validator(mode="after")
    @classmethod
    def validate_business_rules(cls, model):

        if model.stock == 0 and model.is_active is True:
            raise ValueError("If stock is 0 then is_active must be False")

        if model.discount is not None and model.discount > 0 and model.rating == 0:
            raise ValueError("Discounted product must have rating")

        return model
