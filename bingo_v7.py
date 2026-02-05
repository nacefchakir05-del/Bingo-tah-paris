import streamlit as st
import random
import json

# 1. CONFIGURATION
st.set_page_config(page_title="Bingo Reveal VIP", layout="centered")

# Liste de couleurs fixes pour les 7 joueurs
COULEURS = ["#FF4B4B", "#4BFF4B", "#4B4BFF", "#FF4BFF", "#FFFF4B", "#4BFFFF", "#FF964B"]

st.markdown("""
    <style>
    .stApp { background-color: #121212 !important; color: #ffffff !important; }
    
    .bingo-container { 
        display: grid; 
        grid-template-columns: repeat(5, 1fr); 
        gap: 6px; 
        max-width: 450px; 
        margin: auto; 
    }
    
    .bingo-box { 
        aspect-ratio: 1/1; 
        background: white !important; 
        color: black !important; 
        border-radius: 8px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        text-align: center; 
        font-size: clamp(7px, 2.2vw, 10px); 
        font-weight: bold; 
        padding: 4px;
        transition: all 0.3s ease;
        border: 3px solid var(--border-color);
    }

    /* Style pour les cases "Révélées" ou "Trouvées" */
    .highlight { 
        transform: scale(1.05);
        box-shadow: 0 0 15px var(--border-color);
        filter: brightness(1.2);
    }
    
    .dimmed { opacity: 0.2; filter: grayscale(1); }

    input { background-color: white !important; color: black !important; }
    .stButton>button { background: linear-gradient(90deg, #00d4ff, #0055ff) !important; color: white !important; border-radius: 20px !important; }
    .legend-item { padding: 5px; border-radius: 5px; margin-bottom: 5px; color: black; font-weight: bold; text-align: center; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION
if 'all_ideas' not in st.session_state: st.session_state.all_ideas = []
if 'players' not in st.session_state: st.session_state.players = []
if 'step' not in st.session_state: st.session_state.step = 'INSCRIPTION'

SECRET_CODE = "1234"

st.title("🎲 BINGO REVEAL")

# --- BARRE LATÉRALE (SAUVEGARDE & LÉGENDE) ---
with st.sidebar:
    st.header("💾 Gestion & Sauvegarde")
    import_data = st.text_area("Restaurer via code :")
    if st.button("Charger la partie"):
        try:
            data = json.loads(import_data)
            st.session_state.all_ideas = data['ideas']
            st.session_state.players = data['players']
            st.success("Chargé !")
        except: st.error("Code invalide")

    if st.session_state.all_ideas:
        st.subheader("📋 Code actuel")
        backup = json.dumps({"ideas": st.session_state.all_ideas, "players": st.session_state.players})
        st.code(backup, language="json")

    st.divider()
    if st.session_state.players:
        st.subheader("🎨 Qui a écrit quoi ?")
        for p in st.session_state.players:
            st.markdown(f'<div class="legend-item" style="background-color: {p["color"]};">{p["name"]}</div>', unsafe_allow_html=True)

# --- LOGIQUE PRINCIPALE ---

# ÉTAPE 1 : TOUT LE MONDE N'A PAS ENCORE REMPLI
if len(st.session_state.players) < 7:
    st.subheader(f"Joueurs enregistrés : {len(st.session_state.players)} / 7")
    
    # On utilise un formulaire avec une clé unique pour reset le nom
    with st.form(key=f"form_joueur_{len(st.session_state.players)}"):
        nom = st.text_input("Ton prénom :")
        i1 = st.text_input
