# 🎬 CINEMAI — Know Before You Watch

CINEMAI is a machine-learning web app that predicts whether a movie is likely to be **good or bad** before you watch it, and shows the films **trending right now** from TMDB.

A `RandomForestClassifier` trained on IMDb datasets scores a movie from its genre, vote count, and the historical track records of its actors, writers, and director.

---

## ✨ Features

- **Movie Predictor** — enter a genre, vote count, and actor/writer/director scores; get an instant *Good Movie* / *Bad Movie* verdict from the trained model.
- **Trending Movies** — live daily trending list pulled from the TMDB API.
- **Clean two-service architecture** — a static frontend served by nginx, and a separate FastAPI JSON API, both containerized with Docker.

---

## 🏗️ Architecture

```
Browser
  │
  ▼
nginx (frontend container, port 3000)
  ├── serves static HTML / CSS / JS
  └── /api/*  ──reverse proxy──►  FastAPI (backend container, port 8000)
                                     ├── POST /predict   → ML prediction
                                     └── GET  /trending  → TMDB data
```

The frontend talks to the backend through nginx's `/api/` proxy, so there is **no CORS setup and no hardcoded hostnames** — everything is same-origin.

---

## 📁 Project Structure

```
movie_project/
├── app/                      # Frontend (nginx)
│   ├── Dockerfile
│   ├── nginx.conf            # Serves static files + proxies /api/ to backend
│   └── static/
│       ├── index.html        # Landing page
│       ├── predictor.html    # Prediction form
│       ├── trending.html     # Trending movies list
│       ├── script.js         # Predictor logic (calls /api/predict)
│       ├── trending.js       # Trending logic (calls /api/trending)
│       └── style.css
│
├── backend/ 
|   ├── dataset                # Backend (FastAPI)
│   ├── Dockerfile
│   ├── main.py               # API: /predict, /trending, /health
│   ├── schema.py             # Pydantic request model
│   ├── requirements.txt
│   ├── models/
│   │   └── model.pkl         # Trained RandomForest model
│   └── src/
│       ├── preprocessor.py   # Data cleaning & feature engineering
│       └── train.py          # Model training script
│                 # IMDb .tsv datasets (not committed)               # Exploratory training notebook
├── output/                   # Model evaluation plots
├── docker-compose.yml
└── .env                      # TMDB_API_KEY (not committed)
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- A [TMDB API key](https://www.themoviedb.org/settings/api) (free)
- The trained model file `backend/models/model.pkl`

> ⚠️ **The trained model and the IMDb dataset are NOT included in this repo** — they are far too large for GitHub (the model is ~2.7 GB, the dataset ~6 GB). You must generate the model yourself before the backend will start. See [The Model → Generating the model](#-the-model) below.

### 1. create a venv:
```python -m venv venv ``` 
### 2. activate the env:
``` source \venv\Script\activate```
### 3. create models folder:

create the folder ``` models``` inside the backend folder

### 4. install python dependencies:
```pip install -r backend/requirements.txt ```
### 5. train the model:
``` cd backend/src
    python train.py 
```
### 6. Configure API_key:
create```.env``` file in the project root
``` TMDB_API_KEY=your_tmdb_api_key_here ```
### 7. Run with Docker Compose
``` docker compose up --build ```

## 🔌 API Reference

The backend is a JSON API (reachable through nginx at `/api/...`).

### `GET /health`
Health check. Returns `{"status": "ok"}`.

### `GET /trending`
Returns the current day's trending movies from TMDB.

### `POST /predict`
Predicts whether a movie is good or bad.

**Request body:**

```json
{
  "numVotes": 5000,
  "genre": "Drama",
  "avg_actor_score": 7.2,
  "writer_avg_score": 6.8,
  "director_avg_score": 7.5
}
```

**Response:**

```json
{
  "prediction": 1,
  "label": "Good Movie"
}
```

Interactive API docs are available at **http://localhost:8000/docs** when the backend port is exposed.

---

## 🧠 The Model

- **Algorithm:** `RandomForestClassifier` (scikit-learn), 500 trees, `class_weight="balanced"`.
- **Target:** a movie is labelled *Good* when its IMDb `averageRating` ≥ 6.5.
- **Features:** vote count, one-hot encoded genre (28 genres), and engineered "track record" scores for the cast, writers, and director (each combining their average rating with how many titles they've worked on).
- **Data:** IMDb non-commercial datasets (`title.basics`, `title.ratings`, `title.crew`, `title.principals`, `name.basics`).

### Generating the model

Because the model file is not in the repo, you have to build it once before running the app:

1. **Download the IMDb datasets** from [datasets.imdbws.com](https://datasets.imdbws.com/) and place them under `dataset/` so the structure matches:

   ```
   dataset/
   ├── name.basics.tsv/name.basics.tsv
   ├── title.basics.tsv/title.basics.tsv
   ├── title.crew.tsv/title.crew.tsv
   ├── title.principals.tsv/title.principals.tsv
   └── title.ratings.tsv/title.ratings.tsv
   ```
This regenerates `backend/models/model.pkl` (required by the backend) and evaluation plots in `output/`. Once `model.pkl` exists, you can start the app with `docker compose up --build`.

> **Note:** the model is pinned to `scikit-learn==1.7.2` in `requirements.txt`. If you retrain with a different version, keep the version consistent so the saved model loads without warnings.

---

## 🛠️ Development

The frontend's static files and nginx config are mounted as volumes in `docker-compose.yml`, so **edits to HTML/CSS/JS show up on a browser refresh** — no rebuild needed.

- Static file change → just refresh the browser (Ctrl+Shift+R).
- `nginx.conf` change → `docker compose restart frontend`.
- Backend code change → `docker compose up --build`.

For production, remove the `volumes:` block from the `frontend` service so the image stays self-contained.

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML, CSS, vanilla JavaScript, nginx |
| Backend | FastAPI, Uvicorn |
| ML | scikit-learn, pandas, NumPy |
| Data | IMDb datasets, TMDB API |
| Infra | Docker, Docker Compose |

---

## 🔐 Security Notes

- Keep your `TMDB_API_KEY` in `.env` (already git-ignored) — never commit it.
- If a key has ever been committed, rotate it at the [TMDB settings page](https://www.themoviedb.org/settings/api).
