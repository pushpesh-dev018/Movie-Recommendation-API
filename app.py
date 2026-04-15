"""
CineMatch – Movie Recommender
==============================
Features:
  • Login / Register system (local session-based)
  • Voice Search (Web Speech API via HTML component)
  • Random Movie Picker
  • Personal Movie Notes / Reviews
  • Watchlist / Favorites
  • Filters (rating + year range)
  • Dark / Light Mode
  • Trailer Button
  • Ratings & popularity bars

Requirements (pip install):
    streamlit requests python-dotenv
"""

import hashlib
import os
import random

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
API_BASE       = "https://movie-rec-466x.onrender.com"
TMDB_IMG       = "https://image.tmdb.org/t/p/w500"
YOUTUBE_SEARCH = "https://www.youtube.com/results?search_query="

st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")

# ─────────────────────────────────────────────
# SIMPLE USER STORE  (in-memory; swap for DB in prod)
# ─────────────────────────────────────────────
if "users_db" not in st.session_state:
    st.session_state.users_db = {}

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username: str, password: str) -> tuple[bool, str]:
    if not username or not password:
        return False, "Username and password required."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    if username in st.session_state.users_db:
        return False, "Username already exists."
    st.session_state.users_db[username] = {
        "password_hash": _hash(password),
        "watchlist": {},
        "notes": {},
    }
    return True, "Account created!"

def login_user(username: str, password: str) -> tuple[bool, str]:
    db = st.session_state.users_db
    if username not in db:
        return False, "User not found."
    if db[username]["password_hash"] != _hash(password):
        return False, "Wrong password."
    return True, "Welcome back!"

def current_user():
    return st.session_state.get("logged_in_user")

def user_data() -> dict:
    u = current_user()
    if u and u in st.session_state.users_db:
        return st.session_state.users_db[u]
    if "guest_data" not in st.session_state:
        st.session_state.guest_data = {"watchlist": {}, "notes": {}}
    return st.session_state.guest_data

# ─────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def theme_css(dark: bool) -> str:
    if dark:
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Sora:wght@300;400;500;600;700&display=swap');
        :root{
          --bg:#09090f; --bg2:#111118; --card:#16161f; --card2:#1e1e2a;
          --acc:#e50914; --acc2:#ff6b35; --acc3:#f5c518;
          --t1:#f0f0f8; --t2:#9090b0; --t3:#505068;
          --bdr:rgba(255,255,255,0.07);
          --sh:0 8px 32px rgba(0,0,0,0.6);
          --tag:rgba(229,9,20,0.18); --tagc:#ff7070;
          --input:#1a1a26;
        }
        </style>"""
    else:
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Sora:wght@300;400;500;600;700&display=swap');
        :root{
          --bg:#f2f2f8; --bg2:#ffffff; --card:#ffffff; --card2:#ebebf5;
          --acc:#e50914; --acc2:#ff6b35; --acc3:#d4a017;
          --t1:#0d0d1a; --t2:#4a4a6a; --t3:#9090aa;
          --bdr:rgba(0,0,0,0.08);
          --sh:0 4px 20px rgba(0,0,0,0.10);
          --tag:rgba(229,9,20,0.08); --tagc:#cc0000;
          --input:#ffffff;
        }
        </style>"""

st.markdown(theme_css(st.session_state.dark_mode), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
html,body,.stApp{background:var(--bg)!important;color:var(--t1)!important;font-family:'Sora',sans-serif!important}
.block-container{padding-top:0.4rem!important;padding-bottom:3rem!important;max-width:1500px!important}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--bdr)!important}
[data-testid="stSidebar"] *{color:var(--t1)!important}

.stButton>button{
  background:transparent!important;border:1px solid var(--bdr)!important;
  color:var(--t2)!important;border-radius:9px!important;
  font-family:'Sora',sans-serif!important;font-size:0.8rem!important;
  transition:all 0.18s ease!important;padding:0.4rem 0.8rem!important}
.stButton>button:hover{background:var(--acc)!important;color:#fff!important;border-color:var(--acc)!important;transform:translateY(-1px)!important}

.stTextInput input,.stTextArea textarea{
  background:var(--input)!important;border:1px solid var(--bdr)!important;
  color:var(--t1)!important;border-radius:10px!important;
  font-family:'Sora',sans-serif!important}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:var(--acc)!important;box-shadow:0 0 0 3px rgba(229,9,20,0.14)!important}

[data-baseweb="select"] *{background:var(--input)!important;color:var(--t1)!important}

.stTabs [data-baseweb="tab-list"]{background:var(--bg2)!important;border-radius:12px!important;padding:4px!important}
.stTabs [data-baseweb="tab"]{color:var(--t2)!important;border-radius:9px!important;font-family:'Sora',sans-serif!important}
.stTabs [aria-selected="true"]{background:var(--acc)!important;color:#fff!important}

hr{border-color:var(--bdr)!important;opacity:1!important}

.movie-title{font-size:0.83rem;font-weight:600;line-height:1.18rem;max-height:2.36rem;overflow:hidden;color:var(--t1);margin:6px 0 3px}
.movie-meta{font-size:0.72rem;color:var(--t3)}
.star-row{display:flex;align-items:center;gap:3px;font-size:0.78rem;color:var(--acc3);font-weight:600}
.bar-wrap{background:var(--bdr);border-radius:99px;height:3px;overflow:hidden;margin-top:3px}
.bar-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--acc),var(--acc2))}
.genre-tag{display:inline-block;padding:2px 8px;border-radius:99px;background:var(--tag);color:var(--tagc);font-size:0.7rem;font-weight:600;margin:2px 2px 0 0}
.wl-badge{position:absolute;top:7px;right:7px;background:var(--acc);color:#fff;font-size:0.65rem;font-weight:700;padding:2px 7px;border-radius:99px;z-index:10}
.sec-head{font-family:'Bebas Neue',sans-serif;font-size:1.85rem;letter-spacing:0.07em;color:var(--t1);margin:0.1rem 0}
.sec-sub{font-size:0.82rem;color:var(--t3);margin-bottom:0.9rem}
.hero-wrap{position:relative;border-radius:18px;overflow:hidden;margin-bottom:1.8rem}
.hero-img{width:100%;max-height:370px;object-fit:cover;display:block}
.hero-over{position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,0.85) 0%,rgba(0,0,0,0.25) 60%,transparent 100%)}
.hero-cnt{position:absolute;bottom:0;left:0;padding:2rem 2.5rem}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:2.8rem;color:#fff;letter-spacing:0.05em;line-height:1;text-shadow:0 2px 14px rgba(0,0,0,0.5)}
.hero-sub{font-size:0.88rem;color:rgba(255,255,255,0.72);margin-top:0.35rem}
.stat-box{background:var(--card);border:1px solid var(--bdr);border-radius:12px;padding:0.9rem;text-align:center}
.stat-val{font-family:'Bebas Neue',sans-serif;font-size:2rem;color:var(--acc);letter-spacing:0.04em}
.stat-lbl{font-size:0.72rem;color:var(--t3);margin-top:1px}
.note-card{background:var(--card2);border:1px solid var(--bdr);border-radius:12px;padding:1rem;margin-bottom:0.7rem}
.login-wrap{max-width:420px;margin:3rem auto;background:var(--card);border:1px solid var(--bdr);border-radius:20px;padding:2.5rem}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
for k, v in [
    ("view", "home"), ("selected_tmdb_id", None),
    ("logged_in_user", None),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────
def goto(view, tmdb_id=None):
    st.session_state.view = view
    if tmdb_id:
        st.session_state.selected_tmdb_id = int(tmdb_id)
    st.rerun()

# ─────────────────────────────────────────────
# WATCHLIST / NOTES helpers
# ─────────────────────────────────────────────
def watchlist() -> dict:
    return user_data()["watchlist"]

def notes_store() -> dict:
    return user_data()["notes"]

def toggle_wl(movie: dict):
    wl = watchlist()
    tid = movie.get("tmdb_id")
    if not tid: return
    tid = int(tid)
    if tid in wl:
        del wl[tid]
    else:
        wl[tid] = movie

def in_wl(tmdb_id) -> bool:
    return int(tmdb_id) in watchlist()

def save_note(tmdb_id: int, title: str, text: str, rating: int):
    notes_store()[int(tmdb_id)] = {"title": title, "text": text, "rating": rating}

def get_note(tmdb_id: int) -> dict:
    return notes_store().get(int(tmdb_id), {})

# ─────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────
@st.cache_data(ttl=120)
def api_get(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}"
        return r.json(), None
    except Exception as e:
        return None, str(e)

def star_html(vote) -> str:
    if not vote: return ""
    f = round(float(vote) / 2)
    s = "★" * f + "☆" * (5 - f)
    return (
        f"<div class='star-row'>{s} "
        f"<span style='color:var(--t3);font-weight:400'>{float(vote):.1f}</span></div>"
        f"<div class='bar-wrap'><div class='bar-fill' style='width:{int(float(vote)*10)}%'></div></div>"
    )

# ─────────────────────────────────────────────
# FILTER HELPERS
# ─────────────────────────────────────────────
def apply_filters(cards: list, min_r: float, yr: tuple) -> list:
    out = []
    for m in (cards or []):
        try:
            vote = float(m.get("vote_average") or 0)
        except:
            vote = 0
        raw_date = str(m.get("release_date") or "")
        year_str = raw_date[:4]
        year = int(year_str) if year_str.isdigit() else 0
        if vote < min_r:
            continue
        if year and not (yr[0] <= year <= yr[1]):
            continue
        out.append(m)
    return out

# ─────────────────────────────────────────────
# TMDB PARSE
# ─────────────────────────────────────────────
def parse_search(data, keyword: str, limit=24):
    keyword_l = keyword.strip().lower()
    raw_items = []
    if isinstance(data, dict) and "results" in data:
        for m in (data.get("results") or []):
            t = (m.get("title") or "").strip()
            tid = m.get("id")
            if not t or not tid: continue
            pp = m.get("poster_path")
            raw_items.append({
                "tmdb_id": int(tid), "title": t,
                "poster_url": f"{TMDB_IMG}{pp}" if pp else None,
                "release_date": m.get("release_date", ""),
                "vote_average": m.get("vote_average"),
            })
    elif isinstance(data, list):
        for m in data:
            tid = m.get("tmdb_id") or m.get("id")
            t = (m.get("title") or "").strip()
            if not t or not tid: continue
            raw_items.append({
                "tmdb_id": int(tid), "title": t,
                "poster_url": m.get("poster_url"),
                "release_date": m.get("release_date", ""),
                "vote_average": m.get("vote_average"),
            })
    matched = [x for x in raw_items if keyword_l in x["title"].lower()]
    final = matched if matched else raw_items
    sugg = []
    for x in final[:10]:
        yr = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({yr})" if yr else x["title"]
        sugg.append((label, x["tmdb_id"]))
    return sugg, final[:limit]

def tfidf_to_cards(items):
    out = []
    for x in (items or []):
        t = x.get("tmdb") or {}
        if t.get("tmdb_id"):
            out.append({
                "tmdb_id": t["tmdb_id"],
                "title": t.get("title") or x.get("title") or "Untitled",
                "poster_url": t.get("poster_url"),
                "vote_average": t.get("vote_average"),
                "release_date": t.get("release_date"),
            })
    return out

# ─────────────────────────────────────────────
# POSTER GRID
# ─────────────────────────────────────────────
def poster_grid(cards, cols=5, prefix="g", show_wl=True):
    if not cards:
        st.markdown("<div style='color:var(--t3);padding:1.5rem 0;text-align:center'>No movies match your filters.</div>", unsafe_allow_html=True)
        return
    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        cs = st.columns(cols, gap="small")
        for c in range(cols):
            if idx >= len(cards): break
            m = cards[idx]; idx += 1
            tid   = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")
            vote  = m.get("vote_average")
            year  = (m.get("release_date") or "")[:4]
            wl    = in_wl(tid) if tid else False
            with cs[c]:
                if wl:
                    st.markdown("<div class='wl-badge'>★ SAVED</div>", unsafe_allow_html=True)
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.markdown("<div style='height:170px;background:var(--card2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:2.2rem'>🎬</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='movie-title'>{title}</div>", unsafe_allow_html=True)
                if vote:
                    st.markdown(star_html(vote), unsafe_allow_html=True)
                if year:
                    st.markdown(f"<div class='movie-meta'>{year}</div>", unsafe_allow_html=True)
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("Open", key=f"{prefix}_o_{r}_{c}_{idx}"):
                        if tid: goto("details", tid)
                with b2:
                    if show_wl and tid:
                        lbl = "★" if wl else "☆"
                        if st.button(lbl, key=f"{prefix}_w_{r}_{c}_{idx}"):
                            toggle_wl(m); st.rerun()

# ─────────────────────────────────────────────
# VOICE SEARCH COMPONENT
# ─────────────────────────────────────────────
VOICE_JS = """
<div style="margin-bottom:0.6rem">
  <button onclick="startVoice()" id="voiceBtn"
    style="background:#e50914;color:#fff;border:none;border-radius:10px;
           padding:0.5rem 1.2rem;font-size:0.9rem;cursor:pointer;display:flex;align-items:center;gap:8px">
    🎤 Voice Search
  </button>
  <div id="voiceStatus" style="font-size:0.78rem;color:#888;margin-top:5px"></div>
</div>
<script>
function startVoice(){
  if(!('webkitSpeechRecognition' in window||'SpeechRecognition' in window)){
    document.getElementById('voiceStatus').innerText='❌ Not supported in this browser (use Chrome)';return;
  }
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  var r=new SR();r.lang='en-US';r.interimResults=false;r.maxAlternatives=1;
  document.getElementById('voiceBtn').innerText='🔴 Listening…';
  document.getElementById('voiceStatus').innerText='Speak now…';
  r.onresult=function(e){
    var t=e.results[0][0].transcript;
    document.getElementById('voiceStatus').innerText='✅ Heard: '+t;
    document.getElementById('voiceBtn').innerText='🎤 Voice Search';
    var inputs=window.parent.document.querySelectorAll('input[type="text"]');
    if(inputs.length>0){
      var inp=inputs[0];
      var nativeInputValueSetter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
      nativeInputValueSetter.call(inp,t);
      inp.dispatchEvent(new Event('input',{bubbles:true}));
    }
  };
  r.onerror=function(e){
    document.getElementById('voiceStatus').innerText='❌ Error: '+e.error;
    document.getElementById('voiceBtn').innerText='🎤 Voice Search';
  };
  r.onend=function(){document.getElementById('voiceBtn').innerText='🎤 Voice Search';};
  r.start();
}
</script>
"""

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:1.9rem;color:#e50914;letter-spacing:0.1em;padding:0.4rem 0 0.1rem'>🎬 CineMatch</div>", unsafe_allow_html=True)

    u = current_user()
    if u:
        st.markdown(f"<div style='font-size:0.8rem;color:var(--t3)'>Logged in as <b style='color:var(--t1)'>{u}</b></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in_user = None
            st.rerun()
    else:
        st.markdown("<div style='font-size:0.78rem;color:var(--t3)'>Guest mode – login to save data</div>", unsafe_allow_html=True)
        if st.button("🔐 Login / Register", use_container_width=True):
            goto("login")

    st.markdown("---")

    pages = [
        ("🏠", "Home",        "home"),
        ("★",  "Watchlist",   "watchlist"),
        ("📝", "My Reviews",  "reviews"),
        ("🎲", "Random Pick", "random"),
    ]
    for icon, label, view in pages:
        wl_c = len(watchlist())
        display = f"{icon}  {label}" + (f"  ({wl_c})" if view == "watchlist" and wl_c else "")
        if st.button(display, use_container_width=True, key=f"nav_{view}"):
            goto(view)

    st.markdown("---")

    st.markdown("<div style='font-size:0.75rem;font-weight:700;color:var(--t3);letter-spacing:0.07em'>FILTERS</div>", unsafe_allow_html=True)
    min_rating = st.slider("Min Rating ⭐", 0.0, 10.0, 0.0, 0.5, key="min_r")
    year_range = st.slider("Release Year 📅", 1960, 2025, (1990, 2025), key="yr")
    st.markdown("<div style='font-size:0.7rem;color:var(--t3);margin-top:4px'>Filters apply to all grids</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='font-size:0.75rem;font-weight:700;color:var(--t3);letter-spacing:0.07em'>HOME FEED</div>", unsafe_allow_html=True)
    home_cat  = st.selectbox("", ["trending", "popular", "top_rated", "now_playing", "upcoming"], label_visibility="collapsed")
    grid_cols = st.slider("Columns", 3, 8, 5, key="gc")

    st.markdown("---")
    mode_lbl = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
    if st.button(mode_lbl, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Read filter values after sidebar renders
MIN_R = st.session_state.get("min_r", 0.0)
YR    = st.session_state.get("yr", (1990, 2025))

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(
    "<div style='border-bottom:1px solid var(--bdr);padding-bottom:0.8rem;margin-bottom:1.2rem'>"
    "<span style='font-family:Bebas Neue,sans-serif;font-size:2.2rem;color:#e50914;letter-spacing:0.08em'>🎬 CINEMATCH</span>"
    "<span style='font-size:0.82rem;color:var(--t3);margin-left:1rem'>Discover · Save · Explore</span>"
    "</div>",
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════
# VIEW: LOGIN / REGISTER
# ═══════════════════════════════════════════
if st.session_state.view == "login":
    _, mc, _ = st.columns([1, 2, 1])
    with mc:
        st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:2rem;color:#e50914;letter-spacing:0.08em;text-align:center;margin-bottom:1.2rem'>🎬 CINEMATCH</div>", unsafe_allow_html=True)
        tab_login, tab_reg = st.tabs(["🔐 Login", "📝 Register"])

        with tab_login:
            lu  = st.text_input("Username", key="l_user")
            lp  = st.text_input("Password", type="password", key="l_pass")
            if st.button("Login", use_container_width=True, key="do_login"):
                ok, msg = login_user(lu, lp)
                if ok:
                    st.session_state.logged_in_user = lu
                    st.success(msg)
                    goto("home")
                else:
                    st.error(msg)
            st.markdown("<div style='text-align:center;margin-top:1rem'>", unsafe_allow_html=True)
            if st.button("Continue as Guest →", key="guest_btn"):
                goto("home")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_reg:
            ru  = st.text_input("Choose Username", key="r_user")
            rp  = st.text_input("Choose Password (min 4 chars)", type="password", key="r_pass")
            rp2 = st.text_input("Confirm Password", type="password", key="r_pass2")
            if st.button("Create Account", use_container_width=True, key="do_reg"):
                if rp != rp2:
                    st.error("Passwords don't match.")
                else:
                    ok, msg = register_user(ru, rp)
                    if ok:
                        st.session_state.logged_in_user = ru
                        st.success(msg + " Logging you in…")
                        goto("home")
                    else:
                        st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# VIEW: HOME
# ═══════════════════════════════════════════
elif st.session_state.view == "home":

    st.components.v1.html(VOICE_JS, height=70)
    typed = st.text_input("🔍 Search movies", placeholder="Type title or use voice search above…", label_visibility="collapsed")

    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Keep typing…")
        else:
            with st.spinner("Searching…"):
                data, err = api_get("/tmdb/search", {"query": typed.strip()})
            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                sugg, cards = parse_search(data, typed.strip(), 24)
                cards = apply_filters(cards, MIN_R, YR)

                if sugg:
                    labels = ["-- Pick a movie for full details --"] + [s[0] for s in sugg]
                    sel = st.selectbox("Suggestions", labels, label_visibility="collapsed")
                    if sel != labels[0]:
                        goto("details", {s[0]: s[1] for s in sugg}[sel])

                st.markdown(f"<div class='sec-head'>Results for \"{typed}\"</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sec-sub'>{len(cards)} movies · ⭐≥{MIN_R} · {YR[0]}–{YR[1]}</div>", unsafe_allow_html=True)
                poster_grid(cards, cols=grid_cols, prefix="srch")
        st.stop()

    # Home feed
    with st.spinner("Loading…"):
        hcards, err = api_get("/home", {"category": home_cat, "limit": 24})
    if err or not hcards:
        st.error(f"Feed error: {err}")
        st.stop()

    hcards = apply_filters(hcards, MIN_R, YR)

    # Hero banner
    if hcards:
        hero = hcards[0]
        if hero.get("tmdb_id"):
            hd, _ = api_get(f"/movie/id/{hero['tmdb_id']}")
            if hd and hd.get("backdrop_url"):
                bd  = hd["backdrop_url"]; ht = hd.get("title", "")
                ov  = (hd.get("overview") or "")[:130] + "…"
                gn  = " · ".join([g["name"] for g in hd.get("genres", [])[:3]])
                vt  = hd.get("vote_average", 0)
                yr2 = (hd.get("release_date", ""))[:4]
                st.markdown(f"""
                <div class='hero-wrap'>
                  <img class='hero-img' src='{bd}'/>
                  <div class='hero-over'></div>
                  <div class='hero-cnt'>
                    <div class='hero-title'>{ht}</div>
                    <div class='hero-sub'>{'★' * round(float(vt) / 2)} {float(vt):.1f} &nbsp;·&nbsp; {yr2} &nbsp;·&nbsp; {gn}</div>
                    <div style='color:rgba(255,255,255,0.6);font-size:0.84rem;margin-top:0.4rem;max-width:480px'>{ov}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"▶  Open  {ht}", key="hero_btn"):
                    goto("details", hero["tmdb_id"])
                st.markdown("---")

    st.markdown(f"<div class='sec-head'>{home_cat.replace('_', ' ').upper()}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sec-sub'>{len(hcards)} movies · ⭐≥{MIN_R} · {YR[0]}–{YR[1]}</div>", unsafe_allow_html=True)
    poster_grid(hcards, cols=grid_cols, prefix="home")

# ═══════════════════════════════════════════
# VIEW: WATCHLIST
# ═══════════════════════════════════════════
elif st.session_state.view == "watchlist":
    if st.button("← Home"): goto("home")
    st.markdown("<div class='sec-head'>★ MY WATCHLIST</div>", unsafe_allow_html=True)
    wl = watchlist()
    if not wl:
        st.markdown(
            "<div style='text-align:center;padding:4rem 0;color:var(--t3)'>"
            "<div style='font-size:3.5rem'>🎬</div>"
            "<div style='font-size:1.1rem;margin-top:0.5rem'>Watchlist is empty</div>"
            "<div style='font-size:0.85rem;margin-top:0.3rem'>Click ☆ on any movie card to save it</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        wl_cards = apply_filters(list(wl.values()), MIN_R, YR)
        st.markdown(f"<div class='sec-sub'>{len(wl_cards)} movies shown · {len(wl)} saved total</div>", unsafe_allow_html=True)
        poster_grid(wl_cards, cols=grid_cols, prefix="wl")
        if st.button("🗑️ Clear all"):
            user_data()["watchlist"] = {}; st.rerun()

# ═══════════════════════════════════════════
# VIEW: REVIEWS / NOTES
# ═══════════════════════════════════════════
elif st.session_state.view == "reviews":
    if st.button("← Home"): goto("home")
    st.markdown("<div class='sec-head'>📝 MY REVIEWS</div>", unsafe_allow_html=True)
    ns = notes_store()
    if not ns:
        st.markdown(
            "<div style='text-align:center;padding:3rem 0;color:var(--t3)'>"
            "<div style='font-size:3rem'>📝</div>"
            "<div>No reviews yet — open a movie and write one!</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"<div class='sec-sub'>{len(ns)} reviews written</div>", unsafe_allow_html=True)
        for tid, note in ns.items():
            stars = "⭐" * note.get("rating", 0)
            st.markdown(f"""
            <div class='note-card'>
              <div style='font-weight:700;font-size:1rem;color:var(--t1)'>{note['title']}</div>
              <div style='color:var(--acc3);font-size:1rem;margin:2px 0'>{stars}</div>
              <div style='color:var(--t2);font-size:0.88rem;margin-top:6px'>{note['text']}</div>
            </div>""", unsafe_allow_html=True)
            if st.button("🗑️ Delete", key=f"del_note_{tid}"):
                del ns[tid]; st.rerun()

# ═══════════════════════════════════════════
# VIEW: RANDOM MOVIE PICKER
# ═══════════════════════════════════════════
elif st.session_state.view == "random":
    if st.button("← Home"): goto("home")
    st.markdown("<div class='sec-head'>🎲 RANDOM MOVIE PICKER</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-sub'>Can't decide? Let fate choose for you</div>", unsafe_allow_html=True)

    if st.button("🎲 Roll the dice!", key="roll"):
        cat = random.choice(["trending", "popular", "top_rated"])
        with st.spinner("Picking a random movie for you…"):
            data, err = api_get("/home", {"category": cat, "limit": 20})
        if data:
            pool = apply_filters(data, MIN_R, YR)
            if pool:
                st.session_state["random_pick"] = random.choice(pool)
            else:
                st.info("No movies match your current filters. Try lowering the minimum rating.")
        else:
            st.error(f"Error: {err}")

    pick = st.session_state.get("random_pick")
    if pick:
        tid    = pick.get("tmdb_id")
        title  = pick.get("title", "")
        poster = pick.get("poster_url")
        vote   = pick.get("vote_average")
        year   = (pick.get("release_date", ""))[:4]
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            if poster: st.image(poster, use_container_width=True)
        with c2:
            st.markdown(f"<div class='sec-head'>{title}</div>", unsafe_allow_html=True)
            if vote: st.markdown(star_html(vote), unsafe_allow_html=True)
            if year: st.markdown(f"<div class='movie-meta'>{year}</div>", unsafe_allow_html=True)
            bc1, bc2, bc3 = st.columns(3)
            with bc1:
                if st.button("▶ Open Movie", key="rand_open"): goto("details", tid)
            with bc2:
                if st.button("☆ Save", key="rand_save"):
                    toggle_wl(pick); st.rerun()
            with bc3:
                if st.button("🎲 Try Again", key="rand_again"):
                    del st.session_state["random_pick"]; st.rerun()

# ═══════════════════════════════════════════
# VIEW: DETAILS
# ═══════════════════════════════════════════
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected."); goto("home")

    if st.button("← Back"): goto("home")

    with st.spinner("Loading…"):
        data, err = api_get(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Load failed: {err}"); st.stop()

    title        = data.get("title", "")
    vote         = data.get("vote_average") or 0
    release      = data.get("release_date") or "-"
    year         = release[:4]
    genres       = data.get("genres", []) or []
    overview     = data.get("overview") or "No overview available."
    poster_url   = data.get("poster_url")
    backdrop_url = data.get("backdrop_url")

    # Hero banner
    if backdrop_url:
        tags = "".join([f"<span class='genre-tag'>{g['name']}</span>" for g in genres[:4]])
        st.markdown(f"""
        <div class='hero-wrap'>
          <img class='hero-img' src='{backdrop_url}'/>
          <div class='hero-over'></div>
          <div class='hero-cnt'>
            <div class='hero-title'>{title}</div>
            <div class='hero-sub'>{year} &nbsp; {tags}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    left, right = st.columns([1, 2.8], gap="large")

    with left:
        if poster_url:
            st.image(poster_url, use_container_width=True)
        else:
            st.markdown("<div style='height:280px;background:var(--card2);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:3.5rem'>🎬</div>", unsafe_allow_html=True)

        wl = in_wl(tmdb_id)
        if st.button("★ Remove from Watchlist" if wl else "☆ Add to Watchlist", use_container_width=True, key="det_wl"):
            toggle_wl({"tmdb_id": tmdb_id, "title": title, "poster_url": poster_url, "vote_average": vote, "release_date": release})
            st.rerun()

        tq = f"{title} {year} official trailer".replace(" ", "+")
        st.link_button("▶ Watch Trailer", f"{YOUTUBE_SEARCH}{tq}", use_container_width=True)

    with right:
        st.markdown(f"<div class='sec-head'>{title}</div>", unsafe_allow_html=True)
        tags = "".join([f"<span class='genre-tag'>{g['name']}</span>" for g in genres])
        st.markdown(f"<div style='margin-bottom:0.8rem'>{tags}</div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        for col, val, lbl in [
            (c1, f"{float(vote):.1f}", "TMDB Rating"),
            (c2, year,                  "Release Year"),
            (c3, f"{int(float(vote)*10)}%", "Score"),
        ]:
            with col:
                st.markdown(f"<div class='stat-box'><div class='stat-val'>{val}</div><div class='stat-lbl'>{lbl}</div></div>", unsafe_allow_html=True)

        st.markdown(star_html(vote), unsafe_allow_html=True)
        st.markdown("<div style='margin-top:1rem;font-size:0.72rem;font-weight:700;letter-spacing:0.08em;color:var(--t3)'>OVERVIEW</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.95rem;line-height:1.7;color:var(--t2)'>{overview}</div>", unsafe_allow_html=True)

    # Personal Review
    st.markdown("---")
    st.markdown("<div class='sec-head'>📝 MY REVIEW</div>", unsafe_allow_html=True)
    existing = get_note(tmdb_id)
    with st.expander("Write / Edit your review", expanded=bool(existing)):
        my_stars = st.slider("Your Rating", 0, 5, existing.get("rating", 0), key=f"nstar_{tmdb_id}")
        my_note  = st.text_area("Your thoughts…", value=existing.get("text", ""), height=100, key=f"ntxt_{tmdb_id}")
        if st.button("💾 Save Review", key=f"nsave_{tmdb_id}"):
            save_note(tmdb_id, title, my_note, my_stars)
            st.success("Review saved!")
            st.rerun()
        if existing and st.button("🗑️ Delete Review", key=f"ndel_{tmdb_id}"):
            if tmdb_id in notes_store(): del notes_store()[tmdb_id]
            st.rerun()

    # Recommendations
    st.markdown("---")
    with st.spinner("Loading recommendations…"):
        bundle, err2 = api_get("/movie/search", {"query": title, "tfidf_top_n": 12, "genre_limit": 12})

    if not err2 and bundle:
        tfidf_cards = apply_filters(tfidf_to_cards(bundle.get("tfidf_recommendations")), MIN_R, YR)
        genre_cards = apply_filters(bundle.get("genre_recommendations", []), MIN_R, YR)

        st.markdown("<div class='sec-head'>🔎 SIMILAR MOVIES</div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-sub'>Content-based similarity</div>", unsafe_allow_html=True)
        poster_grid(tfidf_cards, cols=grid_cols, prefix="det_tfidf")

        st.markdown("<div class='sec-head'>🎭 MORE LIKE THIS</div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-sub'>Genre-based picks</div>", unsafe_allow_html=True)
        poster_grid(genre_cards, cols=grid_cols, prefix="det_g")
    else:
        genre_only, _ = api_get("/recommend/genre", {"tmdb_id": tmdb_id, "limit": 18})
        if genre_only:
            poster_grid(apply_filters(genre_only, MIN_R, YR), cols=grid_cols, prefix="det_gf")
