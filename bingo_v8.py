import streamlit as st
import random
import json

# 1. CONFIG & STYLE NEON COMPACT
st.set_page_config(page_title="NEON BINGO ULTIMATE", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    .stApp { background-color: #000000 !important; font-family: 'Press Start 2P', cursive !important; }
    
    /* Textes */
    h1, h2, h3, p, label { color: #00FF41 !important; text-shadow: 0 0 5px #00FF41; font-size: 10px; }

    /* Grille et Cases */
    .bingo-container { 
        display: grid; grid-template-columns: repeat(5, 1fr); 
        gap: 5px; width: 100%; max-width: 420px; margin: auto; 
    }
    
    .bingo-box { 
        aspect-ratio: 1/1; background: #0a0a0a !important; 
        border: 1px solid #333; color: transparent !important; /* Caché par défaut */
        display: flex; align-items: center; justify-content: center; 
        text-align: center; font-size: 7px; /* TAILLE RÉDUITE ICI */
        padding: 3px; border-radius: 4px; line-height: 1.1;
    }

    .revealed { 
        background: #000 !important; color: #FFFFFF !important; 
        border: 2px solid var(--p-color) !important; 
        box-shadow: 0 0 10px var(--p-color);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 2px solid #FF00FF; }
    
    input { background-color: #111 !important; color: #00FFFF !important; border: 1px solid #FF00FF !important; font-family: 'Press Start 2P', cursive !important; font-size: 10px !important; }
    
    .stButton>button { 
        background: #FF00FF !important; color: white !important; 
        border: 2px solid #00FFFF !important; font-family: 'Press Start 2P', cursive !important; font-size: 9px !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION (SÉCURISÉE)
if 'players' not in st.session_state: st.session_state.players = []
if 'all_ideas' not in st.session_state: st.session_state.all_ideas = []
if 'reveals' not in st.session_state: st.session_state.reveals = {}

SECRET = "1234"
FLASHY_COLORS = ["#FF00FF", "#00FFFF", "#FFFF00", "#00FF41", "#FF4B4B", "#FF8000", "#BF00FF"]

# 3. SIDEBAR : LE CERVEAU DU JEU
with st.sidebar:
    st.title("📟 DATA CENTER")
    
    # BACKUP / RESTORE
    with st.expander("💾 SAUVEGARDE / RESTAURER"):
        restore_code = st.text_area("Colle ton code de secours ici :")
        if st.button("RESTAURATION GÉNÉRALE"):
            try:
                data = json.loads(restore_code)
                st.session_state.players = data['players']
                st.session_state.all_ideas = data['ideas']
                # On s'assure que les révélations sont bien importées
                st.session_state.reveals = data.get('reveals', {})
                st.success("SYNC TERMINÉE !")
                st.rerun()
            except:
                st.error("CODE INCORRECT")

    # GÉNÉRATION DU CODE (À copier régulièrement)
    if st.session_state.all_ideas:
        st.subheader("CODE À COPIER :")
        full_data = {
            "players": st.session_state.players,
            "ideas": st.session_state.all_ideas,
            "reveals": st.session_state.reveals
        }
        st.code(json.dumps(full_data), language="json")

    st.divider()
    if st.session_state.players:
        st.subheader("TEAM :")
        for p in st.session_state.players:
            st.markdown(f'<p style="color:{p["color"]};">>> {p["name"]}</p>', unsafe_allow_html=True)

    if st.button("FORMATER TOUT (RESET)"):
        st.session_state.clear()
        st.rerun()

# 4. ÉTAPE 1 : INSCRIPTION
if len(st.session_state.players) < 7:
    st.title("👾 INSCRIPTION")
    with st.form(key=f"form_{len(st.session_state.players)}", clear_on_submit=True):
        name = st.text_input("NOM :")
        ideas = [st.text_input(f"PRÉDICTION {i+1}") for i in range(4)]
        if st.form_submit_button("VALIDER"):
            if name and all(ideas):
                color = FLASHY_COLORS[len(st.session_state.players)]
                st.session_state.players.append({"name": name, "color": color})
                for text in ideas:
                    st.session_state.all_ideas.append
