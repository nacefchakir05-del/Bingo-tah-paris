import streamlit as st
import random

# 1. CONFIGURATION & DESIGN
st.set_page_config(page_title="Bingo Weekend VIP", layout="wide")

# Design amélioré avec texte noir et cases auto-adaptables
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { border-radius: 10px; background-color: #FF4B4B; color: white; font-weight: bold; }
    
    /* Grille de Bingo */
    .bingo-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 10px;
        margin-top: 20px;
    }
    
    /* Style des cases */
    .bingo-case { 
        aspect-ratio: 1 / 1;
        border: 2px solid #333; 
        border-radius: 8px; 
        text-align: center; 
        background-color: white; 
        color: #000000 !important; /* Texte bien noir */
        font-weight: 600;
        display: flex; 
        align-items: center; 
        justify-content: center;
        padding: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        
        /* Taille de texte adaptative : 
           minimum 0.8rem, s'adapte à la largeur, maximum 1.2rem */
        font-size: clamp(0.7rem, 2.5vw, 1.1rem);
        line-height: 1.2;
        overflow: hidden;
        word-wrap: break-word;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION
if 'etape' not in st.session_state: st.session_state.etape = 'prenom'
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'liste_global' not in st.session_state: st.session_state.liste_global = []
if 'participants' not in st.session_state: st.session_state.participants = []

NB_MAX_PERSONNES = 7 
CODE_SECRET = "1234" # Change le code ici si besoin

st.title("🎲 Bingo du Weekend")

# 3. LOGIQUE DES PAGES
if len(st.session_state.participants) >= NB_MAX_PERSONNES:
    st.warning(f"✅ Quota de {NB_MAX_PERSONNES} personnes atteint !")
    
    st.subheader("🔓 Espace Grilles")
    code = st.text_input("Entre le code secret pour voir ta grille :", type="password")
    
    if code == CODE_SECRET:
        nom_joueur = st.selectbox("Qui es-tu ?", ["Choisis ton nom"] + st.session_state.participants)
        
        if nom_joueur != "Choisis ton nom":
            # Mélange fixe par joueur pour que la grille ne change pas à chaque clic
            temp_list = list(st.session_state.liste_global)
            random.seed(nom_joueur) 
            random.shuffle(temp_list)
            
            # On s'assure d'avoir 25 cases (en répétant ou coupant)
            final_list = (temp_list * 2)[:25] 

            st.write(f"### Grille de {nom_joueur}")
            
            # Affichage en grille HTML pure pour un meilleur contrôle du design
            grid_html = '<div class="bingo-grid">'
            for item in final_list:
                grid_html += f'<div class="bingo-case">{item}</div>'
            grid_html += '</div>'
            
            st.markdown(grid_html, unsafe_allow_html=True)
            st.write("")
            st.info("📸 Prends une capture d'écran pour jouer !")
            
    elif code != "":
        st.error("Code erroné")

else:
    # FORMULAIRE D'INSCRIPTION
    if st.session_state.etape == 'prenom':
        st.subheader("Bienvenue ! On commence par ton prénom ?")
        name = st.text_input("Prénom :", placeholder="Ex: Thomas")
        if st.button("Suivant ➡️"):
            if name:
                if name in st.session_state.participants:
                    st.error("Ce nom est déjà pris !")
                else:
                    st.session_state.user_name = name
                    st.session_state.etape = 'idees'
                    st.rerun()

    elif st.session_state.etape == 'idees':
        st.subheader(f"À toi {st.session_state.user_name} ! ✍️")
        st.write("Propose 4 situations qui risquent d'arriver ce weekend :")
        
        with st.form("form_idees"):
            i1 = st.text_input("Situation 1", placeholder="Ex: Quelqu'un oublie ses clés")
            i2 = st.text_input("Situation 2", placeholder="Ex: On finit la bouteille de rhum")
            i3 = st.text_input("Situation 3", placeholder="Ex: On commande des pizzas")
            i4 = st.text_input("Situation 4", placeholder="Ex: Quelqu'un chante du Céline Dion")
            
            if st.form_submit_button("Valider mes prédictions"):
                if i1 and i2 and i3 and i4:
                    st.session_state.liste_global.extend([i1, i2, i3, i4])
                    st.session_state.participants.append(st.session_state.user_name)
                    st.session_state.etape = 'prenom'
                    st.success("C'est envoyé ! Passe le téléphone au suivant.")
                    st.rerun()
                else:
                    st.error("Toutes les cases doivent être remplies.")

# Sidebar Admin
with st.sidebar:
    st.write(f"**Participants ({len(st.session_state.participants)}/{NB_MAX_PERSONNES})**")
    for p in st.session_state.participants:
        st.text(f"✅ {p}")
    
    if st.button("🗑️ Reset de la partie"):
        st.session_state.clear()
        st.rerun()
