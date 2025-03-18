API_KEY = "YgAFdpucFrVEbfNkx7w4m"
API_KEY_NAME = "Mongo-DB-Example"

from fastapi import Security, HTTPException, Header

def get_api_key(x_api_key: str = Header(None)):
	if x_api_key != API_KEY:
		raise HTTPException(status_code=401, detail="Invalid API Key")
	return x_api_key

from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId
from typing import List

app = FastAPI()

# MongoDB connection details
MONGO_URI = "mongodb+srv://tyler:Dtshr82VxF0U8drN@cluster0.iiclk.mongodb.net/?retryWrites=true&w=majority&ssl=true&tlsAllowInvalidCertificates=true&appName=Cluster0"
DB_NAME = "sample_mflix"  # Change to your actual database name

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
movies_collection = db["movies"]  # Example collection

# Helper function to convert MongoDB document to JSON
def movie_serializer(movie) -> dict:
    return {
        "id": str(movie["_id"]),
        "title": movie["title"],
        "year": movie.get("year", None),
        "genre": movie.get("genre", []),
        "rating": movie.get("rating", None),
    }

@app.get("/")
def home():
    return {"message": "FastAPI + MongoDB is running!"}

@app.get("/movies", response_model=List[dict])
def get_movies(api_key: str = Security(get_api_key)):
    """Fetch all movies from the database."""
    movies = list(movies_collection.find().limit(10))  # Limit for testing
    return [movie_serializer(movie) for movie in movies]

@app.get("/movies/{movie_id}")
def get_movie(movie_id: str):
    """Fetch a single movie by ID."""
    movie = movies_collection.find_one({"_id": ObjectId(movie_id)})
    if movie:
        return movie_serializer(movie)
    return {"error": "Movie not found"}

@app.post("/movies")
def add_movie(movie: dict):
    """Add a new movie to the database."""
    new_movie = movies_collection.insert_one(movie)
    return {"inserted_id": str(new_movie.inserted_id)}

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: str):
    """Delete a movie by ID."""
    result = movies_collection.delete_one({"_id": ObjectId(movie_id)})
    if result.deleted_count:
        return {"message": "Movie deleted"}
    return {"error": "Movie not found"}
