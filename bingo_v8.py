import streamlit as st
import random
import json
import re
import unicodedata
from uuid import uuid4
from collections import defaultdict

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="BINGO NEON GROUP", layout="centered")

SECRET = "1234"
FLASHY_COLORS = ["#FF00FF", "#00FFFF", "#FFFF00", "#00FF41", "#FF4B4B", "#FF8000", "#BF00FF"]

# =========================
# DESIGN
# =========================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    .stApp { background-color: #000 !important; font-family: 'VT323', monospace !important; }

    h1, h2, h3, p, label, .stMarkdown {
        color: #00FF41 !important;
        text-shadow: 0 0 6px #00FF41;
    }

    .bingo-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 6px;
        max-width: 500px;
        margin: auto;
    }

    .bingo-box {
        aspect-ratio: 1/1;
        background: #0a0a0a;
        border: 1px solid #222;
        color: transparent;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 10px;
        padding: 4px;
        border-radius: 6px;
        transition: all 0.3s ease;
    }

    .revealed {
        color: white !important;
        border: 2px solid var(--p-color) !important;
        box-shadow: 0 0 12px var(--p-color);
        font-weight: bold;
    }

    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #FF00FF;
    }

    .stButton>button {
        background: #FF00FF !important;
        color: white !important;
        border: 2px solid #00FFFF !important;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# OUTILS TEXTE
# =========================
def normalize_text(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def tokenize(s: str) -> list[str]:
    s = normalize_text(s)
    return [w for w in s.split() if len(w) >= 2]

def stable_grid_for_player(player_name: str, ideas: list[dict]) -> list[dict]:
    pool = ideas[:]
    rnd = random.Random(player_name)
    rnd.shuffle(pool)
    return pool[:25]

def ensure_unique_player_name(name: str, players: list[dict]) -> bool:
    n = normalize_text(name)
    return n != "" and all(normalize_text(p["name"]) != n for p in players)

# =========================
# STATE
# =========================
if "players" not in st.session_state:
    st.session_state.players = []
if "all_ideas" not in st.session_state:
    st.session_state.all_ideas = []
if "revealed_ids" not in st.session_state:
    st.session_state.revealed_ids = set()
if "locked" not in st.session_state:
    st.session_state.locked = False

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("💾 SYSTEM")

    if st.session_state.all_ideas:
        st.subheader("SAVE CODE")
        current_state = {
            "players": st.session_state.players,
            "ideas": st.session_state.all_ideas,
            "revealed_ids": list(st.session_state.revealed_ids),
            "locked": st.session_state.locked,
        }
        st.code(json.dumps(current_state, ensure_ascii=False))

    st.divider()

    if st.session_state.players:
        st.subheader("PLAYERS")
        for p in st.session_state.players:
            st.markdown(f'<p style="color:{p["color"]};">■ {p["name"]}</p>', unsafe_allow_html=True)

    st.divider()

    if st.button("RESET"):
        st.session_state.clear()
        st.rerun()

# =========================
# APP
# =========================
st.title("👾 NEON BINGO – WEEKEND MODE")

# =========================
# INSCRIPTIONS
# =========================
if (not st.session_state.locked) and (len(st.session_state.players) < 7):

    st.header(f"PLAYER {len(st.session_state.players) + 1}/7")

    with st.form("register", clear_on_submit=True):
        name = st.text_input("Nom")
        preds = [st.text_input(f"Prédiction {i}") for i in range(1, 5)]
        ok = st.form_submit_button("Valider")

        if ok:
            if not name or any(not p for p in preds):
                st.error("Remplis tout.")
            elif not ensure_unique_player_name(name, st.session_state.players):
                st.error("Nom déjà pris.")
            else:
                color = FLASHY_COLORS[len(st.session_state.players) % len(FLASHY_COLORS)]
                name = name.strip()

                st.session_state.players.append({"name": name, "color": color})

                for idea in preds:
                    st.session_state.all_ideas.append(
                        {
                            "id": str(uuid4()),
                            "text": idea.strip(),
                            "norm": normalize_text(idea),
                            "tokens": tokenize(idea),
                            "author": name,
                            "color": color,
                        }
                    )

                if len(st.session_state.players) >= 7:
                    st.session_state.locked = True

                st.rerun()

# =========================
# JEU
# =========================
else:
    if len(st.session_state.players) < 7:
        st.warning("Session incomplète.")
        st.stop()

    access = st.text_input("Code d'accès", type="password")

    if access == SECRET:

        st.divider()
        st.subheader("🔍 SCAN")

        query = st.text_input("2 mots minimum")
        words = tokenize(query)

        if len(words) >= 2:
            found = False
            for item in st.session_state.all_ideas:
                if all(w in item["tokens"] for w in words):
                    if item["id"] not in st.session_state.revealed_ids:
                        st.session_state.revealed_ids.add(item["id"])
                        st.toast(f"Trouvé : {item['text']}")
                    found = True
            if not found:
                st.info("Rien trouvé.")

        # =========================
        # REVEAL ALL (soirée finale)
        # =========================
        if st.button("🎆 RÉVÉLATION FINALE"):
            for it in st.session_state.all_ideas:
                st.session_state.revealed_ids.add(it["id"])
            st.rerun()

        # =========================
        # GRILLE (celle du premier joueur pour affichage commun)
        # =========================
        viewer = st.session_state.players[0]["name"]
        final_grid = stable_grid_for_player(viewer, st.session_state.all_ideas)

        grid_html = '<div class="bingo-container">'
        for item in final_grid:
            revealed = item["id"] in st.session_state.revealed_ids
            box_class = "bingo-box revealed" if revealed else "bingo-box"
            text = item["text"] if revealed else "???"
            color = item["color"] if revealed else "#333"

            grid_html += f'''
                <div class="{box_class}" style="--p-color:{color};">
                    {text}
                </div>
            '''
        grid_html += "</div>"

        st.markdown(grid_html, unsafe_allow_html=True)

        # =========================
        # STATS JOUEURS
        # =========================
        st.divider()
        st.subheader("🏆 Classement")

        counter = defaultdict(int)
        for item in st.session_state.all_ideas:
            if item["id"] in st.session_state.revealed_ids:
                counter[item["author"]] += 1

        ranking = sorted(counter.items(), key=lambda x: x[1], reverse=True)

        for name, pts in ranking:
            color = next(p["color"] for p in st.session_state.players if p["name"] == name)
            st.markdown(
                f'<p style="color:{color}; font-size:20px;">{name} — {pts}</p>',
                unsafe_allow_html=True,
            )

    elif access != "":
        st.error("Code faux")
