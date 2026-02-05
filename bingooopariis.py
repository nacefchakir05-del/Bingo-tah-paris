import streamlit as st
import random

# 1. CONFIGURATION & DESIGN
st.set_page_config(page_title="Bingo Weekend VIP", layout="centered")

st.markdown("""
    <style>
    /* Global */
    .main { background-color: #f8f9fa; padding: 10px; }
    
    /* Grille de Bingo optimisée pour écran mobile */
    .bingo-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr); /* 5 colonnes égales */
        gap: 4px; /* Espace réduit entre les cases */
        width: 100%; /* Prend toute la largeur de l'écran */
        max-width: 500px; /* Empêche d'être trop géant sur ordi */
        margin: 0 auto;
    }
    
    /* Case de Bingo */
    .bingo-case { 
        aspect-ratio: 1 / 1;
        border: 1.5px solid #000; 
        background-color: white; 
        color: #000 !important;
        font-weight: bold;
        display: flex; 
        align-items: center; 
        justify-content: center;
        padding: 4px;
        text-align: center;
        
        /* Ajustement automatique du texte pour que ça tienne */
        font-size: clamp(0.5rem, 2.2vw, 0.8rem);
        line-height: 1.1;
        word-wrap: break-word;
        overflow: hidden;
    }

    /* Style du bouton de validation */
    .stButton>button { width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION
if 'etape' not in st.session_state: st.session_state.etape = 'prenom'
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'liste_global' not in st.session_state: st.session_state.liste_global = []
if 'participants' not in st.session_state: st.session_state.participants = []

NB_MAX_PERSONNES = 7 
CODE_SECRET = "1234"

st.title("🎲 Bingo Weekend")

# 3. LOGIQUE
if len(st.session_state.participants) >= NB_MAX_PERSONNES:
    st.success(f"Grilles prêtes ({NB_MAX_PERSONNES}/7) !")
    
    code = st.text_input("Code secret :", type="password")
    
    if code == CODE_SECRET:
        nom_joueur = st.selectbox("Qui es-tu ?", ["Choisis ton nom"] + st.session_state.participants)
        
        if nom_joueur != "Choisis ton nom":
            temp_list = list(st.session_state.liste_global)
            random.seed(nom_joueur) 
            random.shuffle(temp_list)
            final_list = (temp_list * 2)[:25] 

            st.write(f"### Grille de {nom_joueur}")
            
            # Affichage de la grille
            grid_html = '<div class="bingo-grid">'
            for item in final_list:
                grid_html += f'<div class="bingo-case">{item}</div>'
            grid_html += '</div>'
            
            st.markdown(grid_html, unsafe_allow_html=True)
            
            st.write("")
            st.warning("📸 La grille est maintenant adaptée à ton écran. Tu peux screenshot !")
            
    elif code != "":
        st.error("Code erroné")

else:
    # FORMULAIRE
    if st.session_state.etape == 'prenom':
        name = st.text_input("Ton prénom :")
        if st.button("Suivant ➡️"):
            if name:
                if name not in st.session_state.participants:
                    st.session_state.user_name = name
                    st.session_state.etape = 'idees'
                    st.rerun()
                else: st.error("Nom déjà pris")

    elif st.session_state.etape == 'idees':
        st.subheader(f"À toi {st.session_state.user_name} !")
        with st.form("form_idees"):
            i1 = st.text_input("Idée 1")
            i2 = st.text_input("Idée 2")
            i3 = st.text_input("Idée 3")
            i4
