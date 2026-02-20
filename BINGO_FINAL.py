import streamlit as st
import random
import json
import re
import unicodedata
from uuid import uuid4

# =========================
# 1) CONFIG & DESIGN NEON
# =========================
st.set_page_config(page_title="NEON BINGO CHAMPION", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    .stApp { background-color: #000 !important; font-family: 'VT323', monospace !important; }

    h1, h2, h3, p, label, .stMarkdown {
        color: #00FF41 !important;
        text-shadow: 0 0 8px #00FF41;
    }

    /* Grille Bingo */
    .bingo-container {
        display: grid; grid-template-columns: repeat(5, 1fr);
        gap: 6px; width: 100%; max-width: 450px; margin: auto;
    }

    .bingo-box {
        aspect-ratio: 1/1; background: #0a0a0a !important;
        border: 1px solid #333; color: transparent !important;
        display: flex; align-items: center; justify-content: center;
        text-align: center; font-size: 8px !important; /* TEXTE PETIT */
        padding: 4px; border-radius: 4px; line-height: 1.1;
        transition: all 0.4s ease;
    }

    .revealed {
        background: #000 !important; color: #FFFFFF !important;
        border: 2px solid var(--p-color) !important;
        box-shadow: 0 0 15px var(--p-color);
        font-weight: bold;
    }

    /* Sidebar & Inputs */
    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #FF00FF;
    }

    .legend-box {
        padding: 5px; border-left: 5px solid var(--p-color);
        margin-bottom: 5px; background: #111;
    }

    input {
        background-color: #111 !important; color: #00FFFF !important;
        border: 1px solid #FF00FF !important; font-family: 'VT323' !important;
    }

    .stButton>button {
        background: #FF00FF !important; color: white !important;
        border: 2px solid #00FFFF !important; font-size: 18px !important;
    }
    
    .reveal-all-btn>button {
        background: #FF4B4B !important; /* Rouge pour le bouton spécial */
        border: 2px solid #FFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SECRET = "1234"
# Ajout d'une 8ème couleur : Bleu Néon (#00BFFF)
FLASHY_COLORS = ["#FF00FF", "#00FFFF", "#FFFF00", "#00FF41", "#FF4B4B", "#FF8000", "#BF00FF", "#00BFFF"]

# =========================
# 2) FONCTIONS UTILS
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

# =========================
# 3) INITIALISATION
# =========================
if "players" not in st.session_state: st.session_state.players = []
if "all_ideas" not in st.session_state: st.session_state.all_ideas = []
if "revealed_ids" not in st.session_state: st.session_state.revealed_ids = set()
if "locked" not in st.session_state: st.session_state.locked = False

# =========================
# 4) SIDEBAR (LÉGENDE & BACKUP)
# =========================
with st.sidebar:
    st.title("🕹️ DASHBOARD")

    # --- LA LÉGENDE (Toujours visible) ---
    if st.session_state.players:
        st.subheader("🎨 LÉGENDE JOUEURS")
        for p in st.session_state.players:
            st.markdown(f"""
                <div class="legend-box" style="--p-color: {p['color']};">
                    <span style="color:{p['color']}; font-weight:bold;">{p['name']}</span>
                </div>
            """, unsafe_allow_html=True)
        
        # --- CLASSEMENT ---
        st.divider()
        st.subheader("🏆 SCORE")
        scores = {p["name"]: 0 for p in st.session_state.players}
        for idea in st.session_state.all_ideas:
            if idea["id"] in st.session_state.revealed_ids and idea["author"] != "System":
                if idea["author"] in scores: scores[idea["author"]] += 1
        
        for name, pts in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            st.write(f"{name} : {pts} pts")

    st.divider()
    with st.expander("💾 SAUVEGARDE"):
        code_in = st.text_area("Restaurer code :")
        if st.button("OK"):
            try:
                d = json.loads(code_in)
                st.session_state.players, st.session_state.all_ideas = d["players"], d["ideas"]
                st.session_state.revealed_ids, st.session_state.locked = set(d["revealed_ids"]), d["locked"]
                st.rerun()
            except: st.error("Erreur")
        
        if st.session_state.all_ideas:
            save_obj = {"players": st.session_state.players, "ideas": st.session_state.all_ideas, 
                        "revealed_ids": list(st.session_state.revealed_ids), "locked": st.session_state.locked}
            st.code(json.dumps(save_obj, ensure_ascii=False))

    if st.button("RESET TOUT"):
        st.session_state.clear()
        st.rerun()

# =========================
# 5) INSCRIPTION
# =========================
st.title("👾 BINGO REVEAL")

# On passe la limite à 8 joueurs
if not st.session_state.locked and len(st.session_state.players) < 8:
    st.header(f"JOUEUR {len(st.session_state.players) + 1}/8")
    with st.form(key=f"reg_{len(st.session_state.players)}", clear_on_submit=True):
        name = st.text_input("TON NOM :")
        p1 = st.text_input("PRÉDICTION 1")
        p2 = st.text_input("PRÉDICTION 2")
        p3 = st.text_input("PRÉDICTION 3") # Seulement 3 prédictions
        if st.form_submit_button("VALIDER"):
            if name and p1 and p2 and p3:
                color = FLASHY_COLORS[len(st.session_state.players)]
                st.session_state.players.append({"name": name, "color": color})
                
                for txt in [p1, p2, p3]:
                    st.session_state.all_ideas.append({
                        "id": str(uuid4()), "text": txt.strip(), "author": name, "color": color, "tokens": tokenize(txt)
                    })
                
                # Quand le 8ème joueur a validé, on ajoute la case Joker pour faire 25 cases et on lock
                if len(st.session_state.players) >= 8: 
                    joker_id = "joker_case_1234"
                    st.session_state.all_ideas.append({
                        "id": joker_id, "text": "🌟 CASE JOKER 🌟", "author": "System", "color": "#FFFFFF", "tokens": ["joker"]
                    })
                    st.session_state.revealed_ids.add(joker_id) # Le joker est auto-révélé
                    st.session_state.locked = True
                
                st.rerun()

# =========================
# 6) JEU
# =========================
else:
    pwd = st.text_input("CODE ACCÈS :", type="password")

    if pwd == SECRET:
        # --- BOUTON REVEAL ALL (Conditionnel au code 1234) ---
        st.markdown('<div class="reveal-all-btn">', unsafe_allow_html=True)
        if st.button("🔓 TOUT RÉVÉLER (GOD MODE)"):
            st.session_state.revealed_ids = {i["id"] for i in st.session_state.all_ideas}
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        user_view = st.selectbox("VOIR LA GRILLE DE :", [p["name"] for p in st.session_state.players])
        
        st.divider()
        search = st.text_input("🔍 SCANNER (2 mots clés ex: 'Thomas bière')").strip()
        search_tokens = tokenize(search)

        if len(search_tokens) >= 2:
            for item in st.session_state.all_ideas:
                if all(t in item["tokens"] for t in search_tokens):
                    if item["id"] not in st.session_state.revealed_ids:
                        st.session_state.revealed_ids.add(item["id"])
                        st.toast(f"MATCH ! {item['text']}")

        # GRILLE
        grid = stable_grid_for_player(user_view, st.session_state.all_ideas)
        html = '<div class="bingo-container">'
        for it in grid:
            is_rev = it["id"] in st.session_state.revealed_ids
            cls = "bingo-box revealed" if is_rev else "bingo-box"
            display = it["text"] if is_rev else "???"
            c = it["color"] if is_rev else "#333"
            html += f'<div class="{cls}" style="--p-color: {c};">{display}</div>'
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
