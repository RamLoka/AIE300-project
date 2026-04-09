# AIE300-project

Simple API built with FastAPI that manages in memory items

GitHub link: https://github.com/RamLoka/AIE300-project

---

## Installation

1. Clone the repository:

git clone https://github.com/RamLoka/AIE300-project
cd AIE300-project

2. Create virtual environment 

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

3. Install dependencies 

pip install -r requirements.

## Running the server

Start the FastAPI server

uvicorn main:app --reload

API URL: http://127.0.0.1:8000
Interactive Swagger UI: http://127.0.0.1:8000/docs

## API Endpoints

Method	Endpoint	Description				Status Code
GET		/items		Get all items			200
GET		/items/{id}	Get a single item by ID	200 / 404
POST	/items		Create a new item		201
PUT		/items/{id}	Update an existing item	200 / 404
DELETE	/items/{id}	Delete an item by ID	200 / 404