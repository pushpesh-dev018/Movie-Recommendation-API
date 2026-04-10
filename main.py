import os
import pickle
from typing import Optional, List

import numpy as np
import pandas as pd
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# =========================
# ENV
# =========================
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

if not TMDB_API_KEY:
    raise RuntimeError("❌ TMDB_API_KEY missing. Add in .env file")

# =========================
# FASTAPI APP
# =========================
app = FastAPI(title="Movie Recommendation API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ✅ FIXED
    allow_credentials=True,
    allow_methods=["*"],   # ✅ FIXED
    allow_headers=["*"],
)

# =========================
# LOAD FILE PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # ✅ FIXED

DF_PATH = os.path.join(BASE_DIR, "df.pkl")
INDICES_PATH = os.path.join(BASE_DIR, "indices.pkl")
TFIDF_MATRIX_PATH = os.path.join(BASE_DIR, "tfidf_matrix.pkl")

df = None
indices = None
tfidf_matrix = None
TITLE_TO_IDX = {}

# =========================
# MODELS
# =========================
class MovieDetails(BaseModel):
    tmdb_id: int
    title: str
    overview: Optional[str]
    release_date: Optional[str]
    poster_url: Optional[str]
    backdrop_url: Optional[str]
    genres: List[dict]

# =========================
# UTILS
# =========================
def make_img(path):
    return f"{TMDB_IMG}{path}" if path else None


async def tmdb_get(url, params):
    params["api_key"] = TMDB_API_KEY
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{TMDB_BASE}{url}", params=params)

    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="TMDB error")

    return res.json()


def normalize(title):
    return str(title).lower().strip()

# =========================
# LOAD MODEL
# =========================
@app.on_event("startup")
def load_files():
    global df, indices, tfidf_matrix, TITLE_TO_IDX

    with open(DF_PATH, "rb") as f:
        df = pickle.load(f)

    with open(INDICES_PATH, "rb") as f:
        indices = pickle.load(f)

    with open(TFIDF_MATRIX_PATH, "rb") as f:
        tfidf_matrix = pickle.load(f)

    for k, v in indices.items():
        TITLE_TO_IDX[normalize(k)] = int(v)

# =========================
# ROUTES
# =========================

@app.get("/")
def home():
    return {"message": "Movie API Running 🚀"}

# 🔍 SEARCH
@app.get("/tmdb/search")
async def search_movie(query: str):
    return await tmdb_get("/search/movie", {"query": query})

# 🎬 DETAILS
@app.get("/movie/id/{movie_id}", response_model=MovieDetails)
async def movie_details(movie_id: int):
    data = await tmdb_get(f"/movie/{movie_id}", {})

    return MovieDetails(
        tmdb_id=data["id"],
        title=data["title"],
        overview=data.get("overview"),
        release_date=data.get("release_date"),
        poster_url=make_img(data.get("poster_path")),
        backdrop_url=make_img(data.get("backdrop_path")),
        genres=data.get("genres", [])
    )

# 🏠 HOME
@app.get("/home")
async def home_movies(category: str = "popular"):
    data = await tmdb_get(f"/movie/{category}", {})

    return [
        {
            "tmdb_id": m["id"],
            "title": m["title"],
            "poster_url": make_img(m.get("poster_path"))
        }
        for m in data["results"][:24]
    ]

# 🤖 TFIDF
def recommend(title, top_n=10):
    idx = TITLE_TO_IDX.get(normalize(title))
    if idx is None:
        return []

    scores = (tfidf_matrix @ tfidf_matrix[idx].T).toarray().ravel()
    indices_sorted = np.argsort(-scores)

    results = []
    for i in indices_sorted:
        if i == idx:
            continue
        results.append(df.iloc[i]["title"])
        if len(results) >= top_n:
            break

    return results

# 🎯 HYBRID
@app.get("/movie/search")
async def hybrid(query: str):
    data = await tmdb_get("/search/movie", {"query": query})

    if not data["results"]:
        raise HTTPException(status_code=404, detail="Movie not found")

    movie = data["results"][0]
    movie_id = movie["id"]

    tfidf_titles = recommend(movie["title"], 10)

    tfidf_movies = []
    for t in tfidf_titles:
        m = await tmdb_get("/search/movie", {"query": t})
        if m["results"]:
            r = m["results"][0]
            tfidf_movies.append({
                "tmdb_id": r["id"],
                "title": r["title"],
                "poster_url": make_img(r.get("poster_path"))
            })

    details = await tmdb_get(f"/movie/{movie_id}", {})
    genre_id = details["genres"][0]["id"] if details["genres"] else None

    genre_movies = []
    if genre_id:
        g = await tmdb_get("/discover/movie", {"with_genres": genre_id})
        for x in g["results"][:10]:
            genre_movies.append({
                "tmdb_id": x["id"],
                "title": x["title"],
                "poster_url": make_img(x.get("poster_path"))
            })

    return {
        "movie": movie["title"],
        "tfidf_recommendations": tfidf_movies,
        "genre_recommendations": genre_movies
    }

# ✅ NEW SIMPLE RECOMMEND
@app.get("/recommend")
async def recommend_api(movie: str):
    return await hybrid(movie)

# 💬 CHATBOT
@app.get("/chatbot")
async def chatbot(query: str):
    q = query.lower()

    if "action" in q:
        return {"response": "🔥 Try: Avengers, John Wick, Mad Max"}
    elif "romantic" in q or "love" in q:
        return {"response": "❤️ Try: Titanic, The Notebook, La La Land"}
    elif "comedy" in q:
        return {"response": "😂 Try: Hangover, Deadpool, Superbad"}
    elif "horror" in q:
        return {"response": "👻 Try: Conjuring, Annabelle, Insidious"}
    elif "sci-fi" in q:
        return {"response": "🚀 Try: Interstellar, Inception, Matrix"}
    else:
        return {"response": "🤖 Try asking: action, comedy, romantic, horror"}