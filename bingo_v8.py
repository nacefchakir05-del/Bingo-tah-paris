import streamlit as st
import random
import json
import re
import unicodedata
from uuid import uuid4

# =========================
# 1) CONFIG & DESIGN
# =========================
st.set_page_config(page_title="BINGO NEON CHAMPIONSHIP", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    .stApp { background-color: #000 !important; font-family: 'VT323', monospace !important; }

    h1, h2, h3, p, label, .stMarkdown {
        color: #00FF41 !important;
        text-shadow: 0 0 8px #00FF41;
    }

    /* Grille */
    .bingo-container {
        display: grid; grid-template-columns: repeat(5, 1fr);
        gap: 6px; width: 100%; max-width: 450px; margin: auto;
    }

    .bingo-box {
        aspect-ratio: 1/1; background: #0a0a0a !important;
        border: 1px solid #222; color: transparent !important;
        display: flex; align-items: center; justify-content: center;
        text-align: center; font-size: 8px; /* Texte réduit */
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

    /* Classement */
    .leaderboard-card {
        border: 1px solid #FF00FF;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
        background: rgba(255, 0, 255, 0.05);
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
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SECRET_USER = "1234"
SECRET_GOD_MODE = "REVELATION" # Code pour tout découvrir
FLASHY_COLORS = ["#FF00FF", "#00FFFF", "#FFFF00", "#00FF41", "#FF4B4B", "#FF8000", "#BF00FF"]

# =========================
# 2) OUTILS LOGIQUES
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
    return [w for w in s.split() if len(w) >= 2]

def stable_grid_for_player(player_name: str, ideas: list[dict]) -> list[dict]:
    pool = ideas[:]
    rnd = random.Random(player_name)
    rnd.shuffle(pool)
    return pool[:25]

def rebuild_ideas(raw_ideas: list[dict]) -> list[dict]:
    rebuilt = []
    for it in raw_ideas:
        text = it.get("text", "").strip()
        rebuilt.append({
            "id": it.get("id") or str(uuid4()),
            "text": text,
            "tokens": it.get("tokens") or tokenize(text),
            "author": it.get("author", "Inconnu"),
            "color": it.get("color", "#00FFFF"),
        })
    return rebuilt

# =========================
# 3) INITIALISATION
# =========================
if "players" not in st.session_state: st.session_state.players = []
if "all_ideas" not in st.session_state: st.session_state.all_ideas = []
if "revealed_ids" not in st.session_state: st.session_state.revealed_ids = set()
if "locked" not in st.session_state: st.session_state.locked = False

# =========================
# 4) SIDEBAR (BACKUP & CLASSEMENT)
# =========================
with st.sidebar:
    st.title("📟 DATA & SCORE")

    # CLASSEMENT COLLECTIF
    if st.session_state.revealed_ids:
        st.subheader("🏆 LEADERBOARD")
        # Compter les points par auteur
        scores = {p["name"]: 0 for p in st.session_state.players}
        for idea in st.session_state.all_ideas:
            if idea["id"] in st.session_state.revealed_ids:
                author = idea["author"]
                if author in scores:
                    scores[author] += 1
        
        # Affichage trié
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for name, score in sorted_scores:
            p_color = next((p["color"] for p in st.session_state.players if p["name"] == name), "#FFF")
            st.markdown(f'<p style="color:{p_color}; margin:0;">{name}: {score} pts</p>', unsafe_allow_html=True)
    
    st.divider()

    with st.expander("💾 BACKUP"):
        restore_input = st.text_area("Coller code :")
        if st.button("RESTAURER"):
            try:
                data = json.loads(restore_input)
                st.session_state.players = data.get("players", [])
                st.session_state.all_ideas = rebuild_ideas(data.get("ideas", []))
                st.session_state.revealed_ids = set(data.get("revealed_ids", []))
                st.session_state.locked = data.get("locked", False)
                st.rerun()
            except: st.error("Erreur")

    if st.session_state.all_ideas:
        st.subheader("CODE SAUVEGARDE")
        save_data = {
            "players": st.session_state.players,
            "ideas": st.session_state.all_ideas,
            "revealed_ids": list(st.session_state.revealed_ids),
            "locked": st.session_state.locked
        }
        st.code(json.dumps(save_data, ensure_ascii=False))

    if st.button("RESET TOTAL"):
        st.session_state.clear()
        st.rerun()

# =========================
# 5) PHASE INSCRIPTION
# =========================
st.title("👾 BINGO TAH LES ZINZINS ")

if not st.session_state.locked and len(st.session_state.players) < 7:
    st.header(f"INSCRIPTION : {len(st.session_state.players) + 1}/7")
    with st.form(key=f"reg_{len(st.session_state.players)}", clear_on_submit=True):
        new_name = st.text_input("NOM :")
        preds = [st.text_input(f"PRÉDICTION {i+1}") for i in range(4)]
        
        if st.form_submit_button("VALIDER"):
            if new_name and all(preds):
                p_color = FLASHY_COLORS[len(st.session_state.players)]
                st.session_state.players.append({"name": new_name, "color": p_color})
                for p in preds:
                    st.session_state.all_ideas.append({
                        "id": str(uuid4()), "text": p.strip(), 
                        "tokens": tokenize(p), "author": new_name, "color": p_color
                    })
                if len(st.session_state.players) >= 7: st.session_state.locked = True
                st.rerun()
            else: st.error("Champs vides !")

# =========================
# 6) PHASE JEU
# =========================
else:
    access_code = st.text_input("CODE ACCÈS (ou Code Secret)", type="password")

    # OPTION : RÉVÉLER TOUT
    if access_code == SECRET_GOD_MODE:
        if st.button("💥 RÉVÉLER TOUTES LES CASES"):
            all_ids = {it["id"] for it in st.session_state.all_ideas}
            st.session_state.revealed_ids = all_ids
            st.success("Toutes les cases sont maintenant visibles !")
            st.rerun()

    if access_code == SECRET_USER or access_code == SECRET_GOD_MODE:
        user_select = st.selectbox("JOUEUR :", [p["name"] for p in st.session_state.players])
        
        # REVEAL SCANNER
        st.divider()
        search_query = st.text_input("🔍 REVEAL SCANNER (2 mots clés)").strip()
        words = tokenize(search_query)

        if len(words) >= 2:
            for item in st.session_state.all_ideas:
                if all(w in item["tokens"] for w in words):
                    if item["id"] not in st.session_state.revealed_ids:
                        st.session_state.revealed_ids.add(item["id"])
                        st.toast(f"DÉBLOQUÉ : {item['text']} (par {item['author']})")

        # AFFICHAGE GRILLE
        final_grid = stable_grid_for_player(user_select, st.session_state.all_ideas)
        grid_html = '<div class="bingo-container">'
        
        for item in final_grid:
            is_revealed = item["id"] in st.session_state.revealed_ids
            box_class = "bingo-box revealed" if is_revealed else "bingo-box"
            txt = item["text"] if is_revealed else "???"
            clr = item["color"] if is_revealed else "#333"
            grid_html += f'<div class="{box_class}" style="--p-color: {clr};">{txt}</div>'
        
        grid_html += "</div>"
        st.markdown(grid_html, unsafe_allow_html=True)
        
        # LÉGENDE RAPIDE
        st.write("---")
        cols = st.columns(4)
        for i, p in enumerate(st.session_state.players):
            cols[i % 4].markdown(f'<p style="color:{p["color"]}; font-size:12px;">■ {p["name"]}</p>', unsafe_allow_html=True)
