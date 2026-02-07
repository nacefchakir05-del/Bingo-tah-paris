import streamlit as st
import random
import json
import re
import unicodedata
from uuid import uuid4

# =========================
# CONFIG & DESIGN
# =========================
st.set_page_config(page_title="BINGO NEON REDUX", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    .stApp { background-color: #000 !important; font-family: 'VT323', monospace !important; }

    h1, h2, h3, p, label, .stMarkdown {
        color: #00FF41 !important;
        text-shadow: 0 0 8px #00FF41;
        font-size: 18px;
    }

    .bingo-container {
        display: grid; grid-template-columns: repeat(5, 1fr);
        gap: 6px; width: 100%; max-width: 450px; margin: auto;
    }

    .bingo-box {
        aspect-ratio: 1/1; background: #0a0a0a !important;
        border: 1px solid #222; color: transparent !important;
        display: flex; align-items: center; justify-content: center;
        text-align: center; font-size: 8px;
        padding: 4px; border-radius: 4px; line-height: 1;
        transition: all 0.4s ease;
        user-select: none;
    }

    .revealed {
        background: #000 !important; color: #FFFFFF !important;
        border: 2px solid var(--p-color) !important;
        box-shadow: 0 0 15px var(--p-color);
        font-weight: bold;
    }

    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #FF00FF;
    }

    input {
        background-color: #111 !important; color: #00FFFF !important;
        border: 1px solid #FF00FF !important; font-family: 'VT323' !important;
    }

    .stButton>button {
        background: #FF00FF !important; color: white !important;
        border: 2px solid #00FFFF !important; font-size: 18px !important;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SECRET = "1234"
FLASHY_COLORS = ["#FF00FF", "#00FFFF", "#FFFF00", "#00FF41", "#FF4B4B", "#FF8000", "#BF00FF"]

# =========================
# OUTILS
# =========================
def normalize_text(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def tokenize(s: str) -> list[str]:
    s = normalize_text(s)
    if not s:
        return []
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
# STATE INIT
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
    st.title("💾 SYSTEM CONTROL")

    if st.session_state.all_ideas:
        st.subheader("CODE DE SAUVEGARDE :")
        current_state = {
            "players": st.session_state.players,
            "ideas": st.session_state.all_ideas,
            "revealed_ids": list(st.session_state.revealed_ids),
            "locked": st.session_state.locked,
        }
        st.code(json.dumps(current_state, ensure_ascii=False))

    st.divider()

    if st.session_state.players:
        st.subheader("TEAM STATUS")
        for p in st.session_state.players:
            st.markdown(f'<p style="color:{p["color"]};">■ {p["name"]}</p>', unsafe_allow_html=True)

    st.divider()

    if st.button("RESET TOTAL"):
        st.session_state.clear()
        st.rerun()

# =========================
# APP
# =========================
st.title("👾 NEON BINGO ARCADE")

# =========================
# INSCRIPTION
# =========================
if (not st.session_state.locked) and (len(st.session_state.players) < 7):
    st.header(f"INSCRIPTION : PLAYER {len(st.session_state.players) + 1}/7")

    with st.form(key=f"player_reg_{len(st.session_state.players)}", clear_on_submit=True):
        new_name = st.text_input("NOM :")
        preds = [st.text_input(f"PRÉDICTION {i}") for i in range(1, 5)]
        submit = st.form_submit_button("VALIDER")

        if submit:
            if not new_name or any(not p for p in preds):
                st.error("REMPLIS TOUTES LES CASES !")
            elif not ensure_unique_player_name(new_name, st.session_state.players):
                st.error("NOM DÉJÀ UTILISÉ.")
            else:
                p_color = FLASHY_COLORS[len(st.session_state.players) % len(FLASHY_COLORS)]
                player_name = new_name.strip()
                st.session_state.players.append({"name": player_name, "color": p_color})

                for idea_text in preds:
                    idea_text = idea_text.strip()
                    st.session_state.all_ideas.append(
                        {
                            "id": str(uuid4()),
                            "text": idea_text,
                            "norm": normalize_text(idea_text),
                            "tokens": tokenize(idea_text),
                            "author": player_name,
                            "color": p_color,
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
        st.warning("SESSION INCOMPLÈTE.")
        st.stop()

    access_code = st.text_input("ENTRER CODE D'ACCÈS :", type="password")

    if access_code == SECRET:
        user_select = st.selectbox("QUI REGARDE ?", [p["name"] for p in st.session_state.players])

        st.divider()
        st.write("🔍 **REVEAL SCANNER** (2 mots minimum)")
        search_query = st.text_input("Recherche")
        words = tokenize(search_query)

        if len(st.session_state.all_ideas) < 25:
            st.error("Pas assez d'idées.")
            st.stop()

        final_grid = stable_grid_for_player(user_select, st.session_state.all_ideas)

        # SCAN
        if len(words) >= 2:
            hit = False
            for item in st.session_state.all_ideas:
                item_tokens = set(item.get("tokens", []))
                if all(w in item_tokens for w in words):
                    if item["id"] not in st.session_state.revealed_ids:
                        st.session_state.revealed_ids.add(item["id"])
                        st.toast(f"CASE DÉBLOQUÉE : {item['text']}")
                    hit = True
            if not hit and search_query != "":
                st.info("Aucun match.")

        # REVEAL ALL
        if st.button("🎆 RÉVÉLATION FINALE"):
            for it in st.session_state.all_ideas:
                st.session_state.revealed_ids.add(it["id"])
            st.rerun()

        # =========================
        # GRILLE
        # =========================
        grid_html = '<div class="bingo-container">'
        score = 0

        for item in final_grid:
            revealed = item["id"] in st.session_state.revealed_ids
            box_class = "bingo-box revealed" if revealed else "bingo-box"
            text = item["text"] if revealed else "???"

            if revealed:
                score += 1
                color = item.get("color", "#00FFFF")
            else:
                color = "#333"

            grid_html += f'<div class="{box_class}" style="--p-color: {color};">{text}</div>'

        grid_html += "</div>"

        st.markdown(grid_html, unsafe_allow_html=True)
        st.write(f"CASES RÉVÉLÉES : {score} / 25")

        # =========================
        # LÉGENDE
        # =========================
        with st.expander("🎨 LÉGENDE"):
            for p in st.session_state.players:
                st.markdown(f'<p style="color:{p["color"]};">■ {p["name"]}</p>', unsafe_allow_html=True)

    elif access_code != "":
        st.error("CODE ERRONÉ")
