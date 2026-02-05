import streamlit as st
import random

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Bingo Weekend", layout="centered")

# 2. DESIGN PERSONNALISÉ (CSS)
st.markdown("""
    <style>
    /* Fond général */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        color: #ffffff;
    }
    
    /* Titres */
    h1, h2, h3 { color: #00d4ff !important; text-align: center; }

    /* Conteneur de la Grille */
    .bingo-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 5px;
        width: 100%;
        max-width: 450px;
        margin: 0 auto;
        padding: 10px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
    }

    /* Cases du Bingo */
    .bingo-box {
        aspect-ratio: 1 / 1;
        background-color: #ffffff;
        border: 2px solid #00d4ff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 4px;
        text-align: center;
        color: #1e1e2f !important;
        font-weight: bold;
        line-height: 1.1;
        /* Taille de texte adaptative */
        font-size: clamp(8px, 2.5vw, 12px);
        word-wrap: break-word;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* Boutons personnalisés */
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        background: linear-gradient(90deg, #00d4ff, #0055ff);
        color: white;
        border: none;
        padding: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    
    /* Input fixes */
    input { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. INITIALISATION DU SYSTÈME
if 'step' not in st.session_state: st.session_state.step = 'NAME'
if 'all_ideas' not in st.session_state: st.session_state.all_ideas = []
if 'players' not in st.session_state: st.session_state.players = []

LIMIT = 7
SECRET = "1234"

# 4. LOGIQUE DE NAVIGATION
st.title("✨ BINGO PARTY ✨")

# CAS : QUOTA ATTEINT
if len(st.session_state.players) >= LIMIT:
    st.info("🎯 Tout le monde a participé ! Les grilles sont prêtes.")
    
    pwd = st.text_input("Code Secret pour voir les grilles", type="password")
    
    if pwd == SECRET:
        target = st.selectbox("Qui es-tu ?", ["Selectionne ton nom"] + st.session_state.players)
        
        if target != "Selectionne ton nom":
            st.write(f"### 📱 Grille de {target}")
            
            # Génération de la grille stable
            pool = list(st.session_state.all_ideas)
            random.seed(target)
            random.shuffle(pool)
            final_grid = (pool * 2)[:25]

            # Rendu HTML de la grille
            grid_html = '<div class="bingo-container">'
            for item in final_grid:
                grid_html += f'<div class="bingo-box">{item}</div>'
            grid_html += '</div>'
            
            st.markdown(grid_html, unsafe_allow_html=True)
            st.write("")
            st.caption("💡 Astuce : Fais ton screenshot maintenant !")
    elif pwd != "":
        st.error("Code incorrect.")

# CAS : COLLECTE DES INFOS
else:
    if st.session_state.step == 'NAME':
        name = st.text_input("Entre ton prénom pour commencer :")
        if st.button("Continuer 🚀"):
            if name and name not in st.session_state.players:
                st.session_state.current_user = name
                st.session_state.step = 'IDEAS'
                st.rerun()
            else:
                st.error("Prénom vide ou déjà pris.")

    elif st.session_state.step == 'IDEAS':
        st.subheader(f"À toi {st.session_state.current_user} !")
        st.write("Quelles sont tes 4 prédictions ?")
        
        with st.form("bingo_form"):
            val1 = st.text_input("Situation 1", placeholder="Ex: Jean renverse sa bière")
            val2 = st.text_input("Situation 2", placeholder="Ex: On finit par chanter du Jul")
            val3 = st.text_input("Situation 3", placeholder="Ex: Quelqu'un s'endort sur la table")
            val4 = st.text_input("Situation 4", placeholder="Ex: On perd les clés du gîte")
            
            if st.form_submit_button("Envoyer mes idées"):
                if all([val1, val2, val3, val4]):
                    st.session_state.all_ideas.extend([val1, val2, val3, val4])
                    st.session_state.players.append(st.session_state.current_user)
                    st.session_state.step = 'NAME'
                    st.success("C'est envoyé ! Passe au suivant.")
                    st.rerun()
                else:
                    st.error("Remplis bien les 4 cases !")

# SIDEBAR ADMIN
with st.sidebar:
    st.header("📊 État du jeu")
    st.write(f"Inscrits : {len(st.session_state.players)} / {LIMIT}")
    for p in st.session_state.players:
        st.write(f"✅ {p}")
    
    st.divider()
    if st.button("🔄 Reset Complet"):
        st.session_state.clear()
        st.rerun()
