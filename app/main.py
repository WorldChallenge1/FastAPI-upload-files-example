import os

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import Column, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

# Directory to save uploaded files
UPLOAD_DIRECTORY = "./uploaded_files"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Database setup
DATABASE_URL = "sqlite:///./test.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# SQLAlchemy models
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    images = relationship("Image", back_populates="product")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    product = relationship("Product", back_populates="images")


# Create database tables
Base.metadata.create_all(bind=engine)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic models for request and response
class ProductRequest(BaseModel):
    name: str = Form(...)
    price: float = Form(...)


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    images: list[str]


app = FastAPI()


@app.post(
    "/products/", status_code=status.HTTP_201_CREATED, response_model=ProductResponse
)
async def create_product(
    request: Request,
    product: ProductRequest = Depends(),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    # Create a new product in the database
    new_product = Product(name=product.name, price=product.price)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    image_urls = []
    for file in files:
        # Save each file to the upload directory
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)  # type: ignore
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Save image metadata to the database
        image_record = Image(filename=file.filename, product_id=new_product.id)
        db.add(image_record)

        # Create a URL for the image
        base_url = str(request.base_url).rstrip("/")
        image_url = f"{base_url}/files/{file.filename}"
        image_urls.append(image_url)

    db.commit()

    return ProductResponse(
        id=new_product.id,  # type: ignore
        name=new_product.name,  # type: ignore
        price=new_product.price,  # type: ignore
        images=image_urls,
    )


@app.get("/files/{filename}")
async def get_file(filename: str):
    # Create the full path to the file
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)

    # Check if the file exists
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Return the file as a response
    return FileResponse(path=file_path, filename=filename, media_type="image/jpeg")
