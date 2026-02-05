import streamlit as st
import random

# 1. CONFIGURATION & FORÇAGE DU THÈME
st.set_page_config(page_title="Bingo Weekend", layout="centered")

# CSS BLINDÉ : On force TOUT pour éviter les conflits clair/sombre
st.markdown("""
    <style>
    /* Force le fond de la page en sombre */
    .stApp {
        background-color: #121212 !important;
        color: #ffffff !important;
    }

    /* Force les textes des labels et titres en blanc */
    label, p, h1, h2, h3, .stMarkdown {
        color: #ffffff !important;
    }

    /* Conteneur de la grille */
    .bingo-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 4px;
        width: 100%;
        max-width: 400px;
        margin: 10px auto;
        padding: 8px;
        background-color: #333333;
        border-radius: 10px;
    }

    /* Case de Bingo : On force le BLANC et texte NOIR */
    .bingo-box {
        aspect-ratio: 1 / 1;
        background-color: #ffffff !important; /* Fond case blanc */
        color: #000000 !important;           /* Texte case noir */
        border: 1px solid #000000;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 4px;
        text-align: center;
        font-weight: bold;
        font-size: clamp(7px, 2.2vw, 10px); /* Taille adaptée mobile */
        line-height: 1;
        word-wrap: break-word;
        overflow: hidden;
    }

    /* Force les champs de saisie (Inputs) pour être lisibles */
    input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 5px !important;
    }

    /* Boutons stylés */
    .stButton>button {
        background: linear-gradient(90deg, #00d4ff, #0055ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION
if 'step' not in st.session_state: st.session_state.step = 'NAME'
if 'all_ideas' not in st.session_state: st.session_state.all_ideas = []
if 'players' not in st.session_state: st.session_state.players = []

LIMIT = 7
SECRET = "1234"

st.title("🎲 BINGO DU WEEKEND")

# 3. LOGIQUE DE NAVIGATION
if len(st.session_state.players) >= LIMIT:
    st.info("🎯 Tout le monde a participé !")
    
    pwd = st.text_input("Code Secret :", type="password")
    
    if pwd == SECRET:
        target = st.selectbox("Qui es-tu ?", ["Choisis ton nom"] + st.session_state.players)
        
        if target != "Choisis ton nom":
            st.write(f"### Grille de {target}")
            
            # Génération stable
            pool = list(st.session_state.all_ideas)
            random.seed(target)
            random.shuffle(pool)
            final_grid = (pool * 2)[:25]

            # Grille HTML
            grid_html = '<div class="bingo-container">'
            for item in final_grid:
                grid_html += f'<div class="bingo-box">{item}</div>'
            grid_html += '</div>'
            
            st.markdown(grid_html, unsafe_allow_html=True)
            st.caption("📸 Fais ton screenshot !")
    elif pwd != "":
        st.error("Code faux")

else:
    if st.session_state.step == 'NAME':
        name = st.text_input("Ton prénom :")
        if st.button("Suivant ➡️"):
            if name and name not in st.session_state.players:
                st.session_state.current_user = name
                st.session_state.step = 'IDEAS'
                st.rerun()
            else:
                st.error("Prénom invalide ou déjà pris")

    elif st.session_state.step == 'IDEAS':
        st.subheader(f"À toi {st.session_state.current_user} !")
        with st.form("my_form"):
            v1 = st.text_input("Idée 1")
            v2 = st.text_input("Idée 2")
            v3 = st.text_input("Idée 3")
            v4 = st.text_input("Idée 4")
            if st.form_submit_button("Valider"):
                if all([v1, v2, v3, v4]):
                    st.session_state.all_ideas.extend([v1, v2, v3, v4])
                    st.session_state.players.append(st.session_state.current_user)
                    st.session_state.step = 'NAME'
                    st.rerun()
                else:
                    st.error("Remplis tout !")

# SIDEBAR
with st.sidebar:
    st.write(f"Joueurs : {len(st.session_state.players)} / {LIMIT}")
    if st.button("RESET"):
        st.session_state.clear()
        st.rerun()
