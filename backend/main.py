import os
from pathlib import Path

import joblib
import pandas as pd
import requests
from fastapi import FastAPI

from schema import MovieInput

app = FastAPI(title="CINEMAI API")

BASE_DIR = Path(__file__).resolve().parent
model_path = BASE_DIR / "models" / "model.pkl"
model = joblib.load(model_path)

# Read the TMDB key from the environment (set in docker-compose / .env).
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "b96461ea6764277abd5cdee6d05bc204")

columns_genre = [
    'Action', 'Adult', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime',
    'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'Game-Show',
    'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
    'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Talk-Show',
    'Thriller', 'War', 'Western',
]

feature_order = [
    'numVotes',
    *columns_genre,
    'avg_actor_score',
    'writer_avg_score',
    'director_avg_score',
]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/trending")
def get_trending():
    url = "https://api.themoviedb.org/3/trending/movie/day"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params, timeout=10)
    return response.json()


@app.post("/predict")
def predict(movie: MovieInput):
    movie.genre = movie.genre.strip().lower().replace("_", "-").capitalize()
    movie.avg_actor_score = float(movie.avg_actor_score)
    movie.director_avg_score = float(movie.director_avg_score)
    movie.writer_avg_score = float(movie.writer_avg_score)
    movie.numVotes = float(movie.numVotes)

    if not (0 <= movie.avg_actor_score <= 10):
        return {"error": "Actor score must be between 0 and 10"}
    if not (0 <= movie.writer_avg_score <= 10):
        return {"error": "Writer score must be between 0 and 10"}
    if not (0 <= movie.director_avg_score <= 10):
        return {"error": "Director score must be between 0 and 10"}
    if movie.numVotes < 0:
        return {"error": "Votes must be positive"}
    if movie.genre not in columns_genre:
        return {"error": "invalid genre"}

    features = []
    for col in feature_order:
        if col == 'numVotes':
            features.append(movie.numVotes)
        elif col == 'avg_actor_score':
            features.append(movie.avg_actor_score)
        elif col == 'writer_avg_score':
            features.append(movie.writer_avg_score)
        elif col == 'director_avg_score':
            features.append(movie.director_avg_score)
        elif col in columns_genre:
            features.append(1 if col == movie.genre else 0)

    df = pd.DataFrame([features], columns=feature_order)
    prediction = model.predict(df)[0]

    return {
        "prediction": int(prediction),
        "label": "Good Movie" if prediction == 1 else "Bad Movie",
    }
