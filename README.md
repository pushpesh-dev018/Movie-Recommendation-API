<div align="center">

<img src="https://readme-typing-svg.herokuapp.com?font=Bebas+Neue&size=60&pause=1000&color=E50914&center=true&vCenter=true&width=600&height=80&lines=🎬+CINEMATCH;Movie+Recommender" alt="CineMatch" />

<h3>🎬 Discover · Save · Explore · Get AI-Powered Recommendations</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Claude_AI-191919?style=for-the-badge&logo=anthropic&logoColor=white"/>
  <img src="https://img.shields.io/badge/TMDB_API-01B4E4?style=for-the-badge&logo=themoviedatabase&logoColor=white"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live-brightgreen?style=flat-square"/>
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/PRs-Welcome-orange?style=flat-square"/>
  <img src="https://img.shields.io/badge/Made%20with-❤️-red?style=flat-square"/>
</p>

---

> **CineMatch** is a full-stack intelligent movie recommendation system that combines  
> **TF-IDF content similarity**, **TMDB live data**, and **Claude AI** to help you  
> find the perfect movie — every single time.

<br/>

[🚀 Live Demo](#-deployment) · [✨ Features](#-features) · [⚙️ Installation](#-local-setup) · [📸 Screenshots](#-screenshots) · [🤝 Contributing](#-contributing)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 AI-Powered
- **Claude AI Chat** — describe a mood or vibe, get perfect picks
- **AI Explanations** — understand *why* each movie is recommended
- **Smart Suggestions** — content-similarity via TF-IDF NLP model
- **Genre Discovery** — TMDB-powered genre matching

</td>
<td width="50%">

### 🎨 Beautiful UI
- **Netflix-style dark theme** with smooth animations
- **Hero banners** with backdrop images on every page
- **Responsive poster grid** — 3 to 8 columns
- **Dark / Light mode** toggle

</td>
</tr>
<tr>
<td width="50%">

### 🔐 User System
- **Login & Register** — secure SHA-256 password hashing
- **Per-user data** — watchlist, reviews & AI history
- **Guest mode** — no login required to explore
- **Session management** — data persists during your visit

</td>
<td width="50%">

### 🔍 Search & Discovery
- **🎤 Voice Search** — speak your query (Chrome/Edge)
- **Live autocomplete** — instant TMDB suggestions as you type
- **Advanced filters** — min rating ⭐ + release year range 📅
- **🎲 Random Picker** — let fate choose for you

</td>
</tr>
<tr>
<td width="50%">

### ★ Watchlist
- Save movies with one click
- Filter your saved list by rating/year
- Accessible from any page via sidebar

</td>
<td width="50%">

### 📝 Personal Reviews
- Star rating (0–5) per movie
- Free-text personal notes
- All reviews in a dedicated page

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CINEMATCH                            │
│                                                             │
│  ┌─────────────┐    HTTP     ┌──────────────────────────┐  │
│  │  Streamlit  │ ──────────► │   FastAPI Backend        │  │
│  │  Frontend   │             │                          │  │
│  │  (app.py)   │             │  ┌────────────────────┐  │  │
│  │             │             │  │  TF-IDF Engine     │  │  │
│  │  • Login    │             │  │  (df.pkl +         │  │  │
│  │  • Search   │             │  │   tfidf_matrix.pkl)│  │  │
│  │  • AI Chat  │             │  └────────────────────┘  │  │
│  │  • Watchlist│             │                          │  │
│  │  • Reviews  │             │  ┌────────────────────┐  │  │
│  └─────────────┘             │  │   TMDB API         │  │  │
│         │                    │  │   (posters, data)  │  │  │
│         │                    │  └────────────────────┘  │  │
│         │                    └──────────────────────────┘  │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │ Anthropic   │                                           │
│  │ Claude API  │  ← AI recommendations & explanations      │
│  └─────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Streamlit | UI, routing, state management |
| **Backend** | FastAPI + Uvicorn | REST API, recommendation endpoints |
| **ML Model** | Scikit-learn TF-IDF | Content-based similarity |
| **Movie Data** | TMDB API | Posters, metadata, genres, trailers |
| **AI Engine** | Anthropic Claude | Chat recommendations + explanations |
| **Language** | Python 3.10+ | Full stack |
| **Deployment** | Render + Streamlit Cloud | Production hosting |

---

## 📁 Project Structure

```
cinematch/
│
├── 🐍 app.py                  # Streamlit frontend (all pages & UI)
├── 🚀 main.py                 # FastAPI backend (API endpoints)
├── 📋 requirements.txt        # Python dependencies
├── 🔑 .env                    # Secret keys (never commit!)
├── 📖 README.md               # You are here
│
├── 🗄️ Pickle Files (ML Model)
│   ├── df.pkl                 # Movie dataset DataFrame
│   ├── indices.pkl            # Title → index mapping
│   ├── tfidf_matrix.pkl       # TF-IDF similarity matrix
│   └── tfidf.pkl              # TF-IDF vectorizer
│
└── 📄 DEPLOY.md               # Detailed deployment guide
```

---

## ⚙️ Local Setup

### Prerequisites

- Python 3.10+
- A TMDB API key → [Get free key](https://www.themoviedb.org/settings/api)
- An Anthropic API key → [Get key](https://console.anthropic.com) *(for AI features)*

### Step 1 — Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/cinematch.git
cd cinematch
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Set up environment variables

Create a `.env` file in the root directory:

```env
TMDB_API_KEY=your_tmdb_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Step 4 — Start the FastAPI backend

```bash
uvicorn main:app --reload --port 8000
```

### Step 5 — Start the Streamlit frontend

```bash
# In a new terminal
streamlit run app.py
```

🎉 Open **http://localhost:8501** in your browser!

---

## 🚀 Deployment

### Backend → Render (Free Tier)

| Step | Action |
|---|---|
| 1 | Push repo to GitHub |
| 2 | Go to [render.com](https://render.com) → New Web Service |
| 3 | Connect your GitHub repo |
| 4 | Build: `pip install -r requirements.txt` |
| 5 | Start: `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| 6 | Add `TMDB_API_KEY` in Environment Variables |

### Frontend → Streamlit Cloud (Free)

| Step | Action |
|---|---|
| 1 | Go to [share.streamlit.io](https://share.streamlit.io) |
| 2 | Connect GitHub → select `app.py` |
| 3 | Add secrets: `ANTHROPIC_API_KEY` + `TMDB_API_KEY` |
| 4 | Click **Deploy** 🚀 |

> 💡 After deploying the backend, update `API_BASE` in `app.py` with your Render URL.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/home` | Home feed (trending/popular/etc.) |
| `GET` | `/tmdb/search` | Search movies by keyword |
| `GET` | `/movie/id/{tmdb_id}` | Full movie details |
| `GET` | `/movie/search` | Bundle: details + TF-IDF + genre recs |
| `GET` | `/recommend/tfidf` | TF-IDF recommendations only |
| `GET` | `/recommend/genre` | Genre-based recommendations |

---

## 🧠 How the Recommendation Engine Works

```
User searches "Inception"
         │
         ▼
  ┌─────────────────┐
  │  TMDB Search    │ → Fetch movie details + poster
  └─────────────────┘
         │
         ▼
  ┌─────────────────┐
  │  TF-IDF Engine  │ → Vectorize movie's text features
  │                 │   (overview, genres, keywords, cast)
  │  cosine_sim =   │ → Compute similarity scores vs all movies
  │  matrix @ vec   │ → Return top-N most similar
  └─────────────────┘
         │
         ▼
  ┌─────────────────┐
  │  TMDB Enrichment│ → Attach poster + metadata to each result
  └─────────────────┘
         │
         ▼
  ┌─────────────────┐
  │  Claude AI      │ → Optional: explain WHY it's similar
  └─────────────────┘
         │
         ▼
    📽️ Results rendered in Streamlit grid
```

---

## 🎤 Voice Search

Voice search uses the **Web Speech API** built into modern browsers.

```
Click 🎤 → Browser asks for mic permission → Speak movie name → Auto-fills search box
```

> ✅ Supported: **Google Chrome**, **Microsoft Edge**  
> ❌ Not supported: Firefox, Safari

---

## 📸 Screenshots

| Page | Description |
|---|---|
| 🏠 **Home Feed** | Trending/popular movies with hero banner |
| 🔍 **Search Results** | Keyword search with autocomplete + voice |
| 📄 **Movie Details** | Full details, stats, trailer link, watchlist |
| 🤖 **AI Chat** | Chat with Claude for personalized picks |
| ★ **Watchlist** | All saved movies in one place |
| 📝 **My Reviews** | Personal ratings and notes |
| 🎲 **Random Picker** | Surprise movie suggestion |

---

## 🤝 Contributing

Contributions are welcome!

```bash
# Fork the repo, then:
git checkout -b feature/amazing-feature
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
# Open a Pull Request
```

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [TMDB](https://www.themoviedb.org/) — Movie data and images
- [Anthropic](https://www.anthropic.com/) — Claude AI engine
- [Streamlit](https://streamlit.io/) — Frontend framework
- [FastAPI](https://fastapi.tiangolo.com/) — Backend framework

---

<div align="center">

**Built with ❤️ and 🎬**

⭐ Star this repo if you found it useful!

</div>
