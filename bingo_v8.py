import streamlit as st
import random
import json
import re
import unicodedata
from uuid import uuid4

# =========================
# 1) CONFIG & DESIGN
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
# 2) OUTILS
# =========================
def normalize_text(s: str) -> str:
    """Minuscule, sans accents, sans ponctuation (stable pour matching)."""
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
    """Grille de 25 idées stable par joueur (seed sur le nom)."""
    pool = ideas[:]
    rnd = random.Random(player_name)  # générateur local (évite effets de bord)
    rnd.shuffle(pool)
    return pool[:25]  # 28 idées -> 25 sans doublons

def ensure_unique_player_name(name: str, players: list[dict]) -> bool:
    n = normalize_text(name)
    return n != "" and all(normalize_text(p["name"]) != n for p in players)

# =========================
# 3) STATE INIT
# =========================
if "players" not in st.session_state:
    st.session_state.players = []  # [{name, color}]
if "all_ideas" not in st.session_state:
    st.session_state.all_ideas = []  # [{id, text, norm, tokens, author, color}]
if "revealed_ids" not in st.session_state:
    st.session_state.revealed_ids = set()  # set(str idea_id)
if "locked" not in st.session_state:
    st.session_state.locked = False  # une fois 7 joueurs, on verrouille l'inscription

# =========================
# 4) SIDEBAR (BACKUP/RESTORE/RESET)
# =========================
with st.sidebar:
    st.title("💾 SYSTEM CONTROL")

    with st.expander("RESTAURER UNE SESSION"):
        restore_input = st.text_area("Coller le code ici :")
        if st.button("LANCER LA RESTAURATION"):
            try:
                data = json.loads(restore_input)

                # players
                st.session_state.players = data.get("players", [])

                # ideas
                ideas = data.get("ideas", [])
                rebuilt = []
                for it in ideas:
                    text = it.get("text", "")
                    author = it.get("author", "")
                    color = it.get("color", "#00FFFF")
                    idea_id = it.get("id", str(uuid4()))
                    tokens = it.get("tokens") or tokenize(text)
                    rebuilt.append(
                        {
                            "id": idea_id,
                            "text": text,
                            "norm": normalize_text(text),
                            "tokens": tokens,
                            "author": author,
                            "color": color,
                        }
                    )
                st.session_state.all_ideas = rebuilt

                # revealed
                rev = data.get("revealed_ids", [])
                st.session_state.revealed_ids = set(rev)

                # locked
                st.session_state.locked = bool(data.get("locked", False))

                st.success("DATA SYNC OK")
                st.rerun()
            except Exception:
                st.error("CODE CORROMPU")

    if st.session_state.all_ideas:
        st.subheader("CODE DE SAUVEGARDE :")
        current_state = {
            "players": st.session_state.players,
            "ideas": [
                {
                    "id": it["id"],
                    "text": it["text"],
                    "author": it.get("author", ""),
                    "color": it.get("color", "#00FFFF"),
                    "tokens": it.get("tokens", []),
                }
                for it in st.session_state.all_ideas
            ],
            "revealed_ids": list(st.session_state.revealed_ids),
            "locked": st.session_state.locked,
        }
        st.code(json.dumps(current_state, ensure_ascii=False))

    st.divider()
    if st.session_state.players:
        st.subheader("TEAM STATUS")
        for p in st.session_state.players:
            st.markdown(f'<p style="color:{p["color"]};">>> {p["name"]}</p>', unsafe_allow_html=True)

    if st.button("RESET TOTAL"):
        st.session_state.clear()
        st.rerun()

# =========================
# 5) APP
# =========================
st.title("👾 NEON BINGO ARCADE")

# ÉTAPE 1 : INSCRIPTION
if (not st.session_state.locked) and (len(st.session_state.players) < 7):
    st.header(f"INSCRIPTION : PLAYER {len(st.session_state.players) + 1}/7")

    with st.form(key=f"player_reg_{len(st.session_state.players)}", clear_on_submit=True):
        new_name = st.text_input("NOM :")
        pred1 = st.text_input("PRÉDICTION 1")
        pred2 = st.text_input("PRÉDICTION 2")
        pred3 = st.text_input("PRÉDICTION 3")
        pred4 = st.text_input("PRÉDICTION 4")
        submit = st.form_submit_button("VALIDER")

        if submit:
            if not (new_name and pred1 and pred2 and pred3 and pred4):
                st.error("REMPLIS TOUTES LES CASES !")
            elif not ensure_unique_player_name(new_name, st.session_state.players):
                st.error("NOM DÉJÀ UTILISÉ (ou vide). Mets un nom unique.")
            else:
                p_color = FLASHY_COLORS[len(st.session_state.players) % len(FLASHY_COLORS)]
                st.session_state.players.append({"name": new_name.strip(), "color": p_color})

                for idea_text in [pred1, pred2, pred3, pred4]:
                    idea_text = idea_text.strip()
                    st.session_state.all_ideas.append(
                        {
                            "id": str(uuid4()),
                            "text": idea_text,
                            "norm": normalize_text(idea_text),
                            "tokens": tokenize(idea_text),
                            "author": new_name.strip(),
                            "color": p_color,
                        }
                    )

                # si 7 joueurs, on verrouille
                if len(st.session_state.players) >= 7:
                    st.session_state.locked = True

                st.rerun()

# ÉTAPE 2 : ACCÈS AU JEU (verrouillage ou 7 joueurs)
else:
    if len(st.session_state.players) < 7:
        st.warning("SESSION RESTAURÉE MAIS INCOMPLÈTE : il faut 7 joueurs pour jouer.")
    else:
        st.subheader("🎯 TOUS LES JOUEURS SONT PRÊTS")

    access_code = st.text_input("ENTRER CODE D'ACCÈS :", type="password")

    if access_code == SECRET:
        user_select = st.selectbox("QUI ES-TU ?", [p["name"] for p in st.session_state.players], index=0)

        if user_select:
            st.divider()
            st.write("🔍 **REVEAL SCANNER** (2 mots minimum)")
            search_query = st.text_input("EX: 'Thomas clés'").strip()

            words = tokenize(search_query)

            # Construire la grille du joueur (stable)
            if len(st.session_state.all_ideas) < 25:
                st.error("Il manque des idées pour générer une grille de 25 cases.")
                st.stop()

            final_grid = stable_grid_for_player(user_select, st.session_state.all_ideas)

            # RÉVÉLATION GLOBALE : si match -> on ajoute l'idea_id au set global
            # (un événement du week-end débloque l'idée, pas une position)
            if len(words) >= 2:
                hit = False
                for item in st.session_state.all_ideas:
                    item_tokens = set(item.get("tokens", []))
                    if all(w in item_tokens for w in words):
                        if item["id"] not in st.session_state.revealed_ids:
                            st.session_state.revealed_ids.add(item["id"])
                            st.toast(f"CASE DÉBLOQUÉE : {item['text']}")
                        hit = True

                # petit feedback si rien ne match (optionnel, mais utile)
                if not hit and search_query != "":
                    st.info("Aucun match. Essaie des mots plus spécifiques.")

            # AFFICHAGE DE LA GRILLE
            grid_html = '<div class="bingo-container">'
            score = 0
            for item in final_grid:
                is_revealed = item["id"] in st.session_state.revealed_ids
                box_class = "bingo-box revealed" if is_revealed else "bingo-box"
                txt = item["text"] if is_revealed else "???"
                clr = item["color"] if is_revealed else "#333"
                if is_revealed:
                    score += 1
                grid_html += f'<div class="{box_class}" style="--p-color: {clr};">{txt}</div>'
            grid_html += "</div>"

            st.markdown(grid_html, unsafe_allow_html=True)
            st.write(f"SCORE : {score} / 25")

            # BONUS : afficher la légende des auteurs (pratique en soirée)
            with st.expander("🎨 LÉGENDE (auteur → couleur)"):
                for p in st.session_state.players:
                    st.markdown(f'<p style="color:{p["color"]};">■ {p["name"]}</p>', unsafe_allow_html=True)

    elif access_code != "":
        st.error("CODE ERRONÉ")
