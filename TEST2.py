import streamlit as st
import random
import pandas as pd

# 1. CONFIGURATION & DESIGN
st.set_page_config(page_title="Bingo Weekend VIP", layout="centered")

# Style CSS pour le look "Design"
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #FF4B4B; color: white; }
    .bingo-case { 
        padding: 20px; border: 2px solid #FF4B4B; border-radius: 10px; 
        text-align: center; background-color: white; font-weight: bold;
        min-height: 100px; display: flex; align-items: center; justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION DES VARIABLES
if 'etape' not in st.session_state: st.session_state.etape = 'prenom'
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'liste_global' not in st.session_state: st.session_state.liste_global = []
if 'participants' not in st.session_state: st.session_state.participants = []

NB_MAX_PERSONNES = 7 # Tu peux changer ce chiffre
CODE_SECRET = "1234" # Le code pour voir la grille

# 3. STRUCTURE DES PAGES
st.title("🎲 Bingo du Weekend")

# SI LE QUOTA EST ATTEINT
if len(st.session_state.participants) >= NB_MAX_PERSONNES:
    st.warning("⚠️ Les inscriptions sont closes ! Le quota de 7 personnes est atteint.")
    
    # Section Code Secret pour voir la grille
    with st.expander("🔓 Accéder aux grilles de jeu"):
        code = st.text_input("Entre le code secret :", type="password")
        if code == CODE_SECRET:
            st.success("Code correct !")
            nom_joueur = st.selectbox("Choisis ton nom :", st.session_state.participants)
            if st.button("Générer ma grille"):
                # Mélange unique basé sur le nom du joueur
                temp_list = st.session_state.liste_global.copy()
                random.seed(nom_joueur)
                random.shuffle(temp_list)
                
                # Affichage de la grille 5x5
                cols = st.columns(5)
                for i in range(25):
                    with cols[i % 5]:
                        st.markdown(f"<div class='bingo-case'>{temp_list[i]}</div>", unsafe_allow_html=True)
                st.info("Capture d'écran ta grille pour jouer !")
        elif code != "":
            st.error("Mauvais code !")

# SI ON PEUT ENCORE JOUER
else:
    # ÉTAPE 1 : LE PRÉNOM
    if st.session_state.etape == 'prenom':
        name = st.text_input("Quel est ton prénom ?")
        if st.button("Continuer"):
            if name:
                if name in st.session_state.participants:
                    st.error("Ce nom a déjà été utilisé !")
                else:
                    st.session_state.user_name = name
                    st.session_state.etape = 'idees'
                    st.rerun()

    # ÉTAPE 2 : LES IDÉES
    elif st.session_state.etape == 'idees':
        st.subheader(f"Salut {st.session_state.user_name} ! Note tes 4 prédictions :")
        with st.form("form_idees"):
            i1 = st.text_input("Prédiction 1")
            i2 = st.text_input("Prédiction 2")
            i3 = st.text_input("Prédiction 3")
            i4 = st.text_input("Prédiction 4")
            if st.form_submit_button("Valider mes idées"):
                if i1 and i2 and i3 and i4:
                    st.session_state.liste_global.extend([i1, i2, i3, i4])
                    st.session_state.participants.append(st.session_state.user_name)
                    st.session_state.etape = 'prenom' # Retour au début pour le suivant
                    st.success("Enregistré ! Donne le téléphone au suivant.")
                    st.rerun()
                else:
                    st.error("Il faut remplir les 4 !")

# Sidebar pour l'admin
with st.sidebar:
    st.write(f"📈 Progression : {len(st.session_state.participants)} / {NB_MAX_PERSONNES}")
    if st.button("RESET TOTAL"):
        st.session_state.clear()
        st.rerun()
