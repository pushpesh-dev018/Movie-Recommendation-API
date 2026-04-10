import requests
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = "https://movie-rec-466x.onrender.com"
# API_BASE = "http://127.0.0.1:8000"

TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="🎬 Movie AI", page_icon="🎬", layout="wide")

# =============================
# ULTRA UI STYLE
# =============================
st.markdown("""
<style>
.block-container { padding-top: 1rem; max-width: 1400px; }

.movie-title {
    font-size: 0.9rem;
    font-weight: 600;
    height: 2.3rem;
    overflow: hidden;
}

.card {
    border-radius: 18px;
    padding: 10px;
    background: #111;
    transition: 0.3s;
}
.card:hover {
    transform: scale(1.05);
}

.stButton>button {
    border-radius: 10px;
    background: linear-gradient(90deg,#ff416c,#ff4b2b);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =============================
# STATE
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"

if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

# =============================
# NAVIGATION
# =============================
def goto_home():
    st.session_state.view = "home"
    st.session_state.selected_tmdb_id = None
    st.rerun()

def goto_details(id):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = id
    st.rerun()

# =============================
# API CALL
# =============================
@st.cache_data(ttl=30)
def api(path, params=None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=20)
        return r.json()
    except:
        return None

# =============================
# ✅ FIXED GRID UI
# =============================
def grid(movies, cols=6, key_prefix="grid"):
    if not movies:
        st.warning("No Movies Found 😢")
        return

    rows = (len(movies)+cols-1)//cols
    idx = 0

    for r in range(rows):
        cols_ui = st.columns(cols)

        for c in range(cols):
            if idx >= len(movies):
                break

            m = movies[idx]
            idx += 1

            with cols_ui[c]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                if m.get("poster_url"):
                    # ✅ FIXED (no deprecated warning)
                    st.image(m["poster_url"], width="stretch")

                if st.button(
                    "🎬 Open",
                    key=f"{key_prefix}_{r}_{c}_{idx}_{m.get('tmdb_id')}"
                ):
                    goto_details(m.get("tmdb_id"))

                st.markdown(
                    f"<div class='movie-title'>{m.get('title')}</div>",
                    unsafe_allow_html=True
                )

                st.markdown("</div>", unsafe_allow_html=True)

# =============================
# ✅ FIXED PARSE FUNCTION
# =============================
def parse(data):
    movies = []

    if not data:
        return movies

    # Case 1: TMDB format
    if isinstance(data, dict) and "results" in data:
        for m in data["results"]:
            if not m.get("title") or not m.get("id"):
                continue

            movies.append({
                "tmdb_id": m["id"],
                "title": m["title"],
                "poster_url": f"{TMDB_IMG}{m['poster_path']}" if m.get("poster_path") else None
            })

    # Case 2: already list
    elif isinstance(data, list):
        movies = data

    return movies

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.title("🎬 Menu")

    if st.button("🏠 Home"):
        goto_home()

    st.markdown("---")

    cols = st.slider("Grid", 4, 8, 6)

    st.markdown("---")
    st.markdown("## 🤖 AI Assistant")

    user_q = st.text_input("Ask: action movies, love...")

    if st.button("Ask AI"):
        res = requests.get(f"{API_BASE}/chatbot", params={"query": user_q})
        if res.status_code == 200:
            st.success(res.json()["response"])

# =============================
# HEADER
# =============================
st.title("🎬 Movie Recommendation System")
st.caption("Search → Explore → AI Recommendations")

# =============================
# HOME
# =============================
if st.session_state.view == "home":

    query = st.text_input("Search Movie...")

    if query and len(query.strip()) > 1:
        data = api("/tmdb/search", {"query": query})

        if data:
            movies = parse(data)

            if movies:
                grid(movies[:24], cols, key_prefix="search")
            else:
                st.warning("No result found 😢 Try another movie")

        else:
            st.error("API Error")

    else:
        st.markdown("### 🔥 Trending")

        data = api("/home", {"category": "popular"})

        if data:
            grid(data, cols, key_prefix="home")

# =============================
# DETAILS
# =============================
elif st.session_state.view == "details":

    id = st.session_state.selected_tmdb_id

    if st.button("⬅ Back"):
        goto_home()

    data = api(f"/movie/id/{id}")

    if not data:
        st.error("Failed")
        st.stop()

    c1, c2 = st.columns([1,2])

    with c1:
        if data.get("poster_url"):
            st.image(data["poster_url"], width=300)

    with c2:
        st.subheader(data.get("title"))
        st.caption(data.get("release_date"))

        genres = ", ".join([g["name"] for g in data.get("genres", [])])
        st.caption(genres)

        st.write(data.get("overview"))

    # =============================
    # RECOMMENDATIONS
    # =============================
    st.markdown("## 🔥 Recommendations")

    bundle = api("/movie/search", {"query": data.get("title")})

    if bundle:

        # TFIDF
        tfidf = []
        for x in bundle.get("tfidf_recommendations", []):
            tm = x.get("tmdb") or {}
            if tm.get("tmdb_id"):
                tfidf.append({
                    "tmdb_id": tm["tmdb_id"],
                    "title": tm["title"],
                    "poster_url": tm["poster_url"]
                })

        if tfidf:
            st.markdown("### 🤖 Similar Movies")
            grid(tfidf, cols, key_prefix="tfidf")

        # GENRE
        genre = bundle.get("genre_recommendations", [])
        if genre:
            st.markdown("### 🎭 Same Genre")
            grid(genre, cols, key_prefix="genre")

    else:
        st.warning("No recommendations available")
