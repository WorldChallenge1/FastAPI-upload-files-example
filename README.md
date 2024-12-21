# FastAPI File Upload Example

This project demonstrates how to upload files using FastAPI, save them on the server, and store metadata in a SQLite database. The application also allows retrieving the uploaded files through a specific endpoint.

## Features

* Upload multiple files (images in this example) along with product details (name and price).
* Store metadata about the uploaded files and products in a SQLite database.
* Retrieve uploaded files using their filenames.

---

## How It Works

### File Upload Directory

The uploaded files are saved in the `./uploaded_files` directory. If the directory does not exist, it is created automatically when the application starts.

### Database

The application uses SQLite for storing data. It includes two tables:
1. `products`: Stores product details (id, name, price).
2. `images`: Stores metadata about uploaded images (id, filename, product_id).

### Endpoints

#### 1. Create Product ( `POST /products/` )

* Accepts product details (`name` and `price`) as form data and a list of files for upload.
* Saves the files (images in this example) to the server and stores their metadata in the database.
* Returns the product details along with URLs to access the uploaded files.

#### 2. Retrieve File ( `GET /files/{filename}` )

* Fetches the file by its filename and returns it as a response.
* Guesses the file's media type based on its extension.
* Returns a 404 error if the file does not exist.

---

## Setup

### Using pip

#### 1. Install Dependencies

Make sure you have Python installed. Then, install the required dependencies:

```bash
pip install fastapi uvicorn sqlalchemy pydantic
```

#### 2. Run the Application

Start the FastAPI application with the following command:

```bash
uvicorn app.main:app --reload
```

### Using uv

#### 1. Install Dependencies and run the application

```bash
uv run uvicorn app.main:app --reload
```

The application will be available at [http://localhost:8000](http://localhost:8000).

## Usage

### 1. Test with Swagger UI

Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to access the interactive API documentation. Use the Swagger UI to test the endpoints.

### 2. Example curl Usage

You can also use curl to test the `POST /products/` endpoint. Here's an example:

```bash
curl -X 'POST' \
  'http://localhost:8000/products/?name=Apple&price=4.99' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@/full/path/to/image1.png;type=image/png' \
  -F 'files=@/full/path/to/image2.png;type=image/png'
```

Replace `/full/path/to/image1.png` and `/full/path/to/image2.png` with the actual paths to the files you want to upload.

### 3. Retrieve Uploaded Files

To retrieve a file, use the `GET /files/{filename}` endpoint. For example:

```bash
curl -X 'GET' 'http://localhost:8000/files/image1.png' --output image1.png
```

This will download the file named `image1.png` to the current directory.

---

## Project Structure

```
.
├── main.py                # Main application code
├── uploaded_files/        # Directory to store uploaded files (created automatically)
└── test.db                # SQLite database file (created automatically)
```

---

## Notes

* Ensure that the filenames of uploaded files are unique to avoid overwriting existing files.
* The server attempts to guess the media type of the uploaded files using their extensions and serves them accordingly. If the type cannot be determined, it defaults to `application/octet-stream`.
* Modify the code if your use case involves more complex validation or additional file handling logic.
