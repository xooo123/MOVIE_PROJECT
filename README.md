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
 
The app runs as **two separate Docker containers** orchestrated by Docker Compose:
 
```
                         Host machine
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│   Browser ──http://localhost:3000──►  ┌──────────────────┐    │
│                                       │  frontend (nginx)│    │
│                                       │   container :80  │    │
│                                       └────────┬─────────┘    │
│                            serves static files │              │
│                            /api/* reverse-proxy│              │
│                                                ▼              │
│                                       ┌──────────────────┐    │
│                                       │ backend (FastAPI)│    │
│                                       │  container :8000 │    │
│                                       │  loads model.pkl │    │
│                                       └────────┬─────────┘    │
│                                                │              │
└────────────────────────────────────────────────┼─────────────┘
                                                  ▼
                                       TMDB API (themoviedb.org)
```
 
**How a request flows:**
 
1. The browser loads the static site (HTML/CSS/JS) from the **nginx** container on port `3000`.
2. When the user predicts a movie or views trending films, the JS calls a **relative** URL like `/api/predict`.
3. nginx matches `/api/` and **reverse-proxies** the request across Docker's internal network to the **FastAPI** container at `http://backend:8000` (the `/api/` prefix is stripped, so `/api/predict` → `/predict`).
4. FastAPI runs the prediction (`model.pkl`) or fetches trending data from TMDB, and returns JSON back through nginx to the browser.
**Why this design:**
 
- **Separation of concerns** — the frontend (nginx, static files) and backend (Python API) are independent containers that can be built, scaled, and deployed separately.
- **No CORS, no hardcoded hosts** — because the browser only ever talks to one origin (`localhost:3000`) and nginx forwards `/api/` internally, there's no cross-origin setup and nothing to change between local and production.
- The two containers find each other by **service name** (`backend`) on the Compose network — no IP addresses involved.
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
├── backend/                  # Backend (FastAPI)
│   ├── Dockerfile
│   ├── main.py               # API: /predict, /trending, /health
│   ├── schema.py             # Pydantic request model
│   ├── requirements.txt
│   ├── models/
│   │   └── model.pkl         # Trained RandomForest model
│   └── src/
│       ├── preprocessor.py   # Data cleaning & feature engineering
│       └── train.py          # Model training script
│
├── dataset/                  # IMDb .tsv datasets (not committed)             # Exploratory training notebook
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
 
### 1. Configure your API key
 
Create a `.env` file in the project root:
 
```env
TMDB_API_KEY=your_tmdb_api_key_here
```
 
### 2. Run with Docker Compose
 
```bash
docker compose up --build
```
 
### 3. Open the app
 
Visit **http://localhost:3000**
 
| URL | What it does |
|-----|--------------|
| `http://localhost:3000/` | Landing page |
| `http://localhost:3000/predictor` | Movie predictor form |
| `http://localhost:3000/trending` | Trending movies |
 
---
 
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
 
2. **Install the Python dependencies** and run the training script:
```bash
   pip install -r backend/requirements.txt
   cd backend/src
   python train.py
```
 
This regenerates `backend/models/model.pkl` (required by the backend) and evaluation plots in `output/`. Once `model.pkl` exists, you can start the app with `docker compose up --build`.
 
> **Note:** the model is pinned to `scikit-learn==1.7.2` in `requirements.txt`. If you retrain with a different version, keep the version consistent so the saved model loads without warnings.
 
---
 
## ⌨️ Commands Reference
 
All commands are run from the **project root** (where `docker-compose.yml` lives).
 
### Running the app
 
```bash
# Build the images and start both containers (foreground, shows logs)
docker compose up --build
 
# Start in the background (detached)
docker compose up --build -d
 
# Stop and remove the containers
docker compose down
 
# Stop containers AND delete the built images (force a fully clean rebuild)
docker compose down --rmi local
```
 ### Applying changes
 
| What you changed | Command to apply it |
|------------------|---------------------|
| HTML / CSS / JS (in `app/static/`) | Just refresh the browser (Ctrl+Shift+R) — mounted as a volume |
| `nginx.conf` | `docker compose restart frontend` |
| Backend Python code | `docker compose up --build backend` |
| `requirements.txt` | `docker compose up --build backend` |
 
> The frontend's `static/` folder and `nginx.conf` are mounted as volumes in `docker-compose.yml`, so most frontend edits need no rebuild. For production, remove the `volumes:` block from the `frontend` service so the image is fully self-contained.
 
### Training the model
 
```bash
pip install -r backend/requirements.txt
cd backend/src
python train.py        # regenerates backend/models/model.pkl
```
 
### Running the backend without Docker (optional)
 
```bash
cd backend
pip install -r requirements.txt
# PowerShell: set the API key for this session
$env:TMDB_API_KEY="your_tmdb_api_key_here"
uvicorn main:app --reload      # serves the API on http://localhost:8000
```
 
> Note: run this way, the backend serves **only the JSON API**. `GET /` returns 404 by design — use `/docs`, `/health`, or `/trending`. The website itself comes from the nginx container.
 
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