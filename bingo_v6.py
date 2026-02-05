import streamlit as st
import random
import json

# 1. CONFIGURATION
st.set_page_config(page_title="Bingo Weekend VIP", layout="centered")

# Liste de couleurs distinctes pour les 7 joueurs
COULEURS = ["#FF4B4B", "#4BFF4B", "#4B4BFF", "#FF4BFF", "#FFFF4B", "#4BFFFF", "#FF964B"]

st.markdown("""
    <style>
    .stApp { background-color: #121212 !important; color: #ffffff !important; }
    .bingo-container { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; max-width: 450px; margin: auto; }
    
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
        box-shadow: inset 0 0 0 3px var(--border-color); /* La bordure de couleur */
    }
    
    input { background-color: white !important; color: black !important; }
    .stButton>button { background: linear-gradient(90deg, #00d4ff, #0055ff) !important; color: white !important; border-radius: 20px !important; }
    .legend-item { padding: 5px; border-radius: 5px; margin-bottom: 5px; color: black; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION
if 'all_ideas' not in st.session_state: st.session_state.all_ideas = [] # Stocke {"text": "...", "color": "..."}
if 'players' not in st.session_state: st.session_state.players = [] # Stocke {"name": "...", "color": "..."}

SECRET = "1234"

st.title("🎲 BINGO COULEURS")

# --- SECTION SIDEBAR (SAUVEGARDE & LÉGENDE) ---
with st.sidebar:
    st.header("💾 Gestion")
    
    # Import / Export
    import_data = st.text_area("Restaurer une partie (coller le code) :")
    if st.button("Restaurer"):
        try:
            data = json.loads(import_data)
            st.session_state.all_ideas = data['ideas']
            st.session_state.players = data['players']
            st.rerun()
        except: st.error("Code invalide")

    if st.session_state.all_ideas:
        st.subheader("📋 Code de sauvegarde")
        backup = json.dumps({"ideas": st.session_state.all_ideas, "players": st.session_state.players})
        st.code(backup, language="json")

    st.divider()
    st.write(f"Inscrits : {len(st.session_state.players)} / 7")
    
    # Affichage de la légende des couleurs (uniquement si on a commencé)
    if st.session_state.players:
        st.subheader("🎨 Légende")
        for p in st.session_state.players:
            st.markdown(f'<div class="legend-item" style="background-color: {p["color"]};">{p["name"]}</div>', unsafe_allow_html=True)

# --- LOGIQUE DE JEU ---
if len(st.session_state.players) >= 7:
    st.success("🎯 Tout le monde est là !")
    pwd = st.text_input("Code Secret :", type="password")
    
    if pwd == SECRET:
        target = st.selectbox("Qui es-tu ?", ["Choisis ton nom"] + [p["name"] for p in st.session_state.players])
        
        if target != "Choisis ton nom":
            # On récupère les idées et on mélange
            pool = list(st.session_state.all_ideas)
            random.seed(target)
            random.shuffle(pool)
            final_grid = (pool * 2)[:25]
            
            st.write(f"### Grille de {target}")
            grid_html = '<div class="bingo-container">'
            for item in final_grid:
                # On applique la couleur du créateur en bordure
                grid_html += f'<div class="bingo-box" style="--border-color: {item["color"]};">{item["text"]}</div>'
            grid_html += '</div>'
            
            st.markdown(grid_html, unsafe_allow_html=True)
            st.info("📸 Chaque couleur de bordure correspond à un ami (voir légende à gauche) !")

else:
    # Formulaire d'inscription
    name = st.text_input("Ton prénom :")
    if name in [p["name"] for p in st.session_state.players]:
        st.warning("Prénom déjà utilisé !")
    else:
        with st.form("form"):
            v1 = st.text_input("Idée 1")
            v2 = st.text_input("Idée 2")
            v3 = st.text_input("Idée 3")
            v4 = st.text_input("Idée 4")
            if st.form_submit_button("Envoyer mes prédictions"):
                if name and v1 and v2 and v3 and v4:
                    # Attribuer la couleur suivante
                    couleur_attribuee = COULEURS[len(st.session_state.players)]
                    
                    # Enregistrer le joueur
                    st.session_state.players.append({"name": name, "color": couleur_attribuee})
                    
                    # Enregistrer les idées avec la couleur
                    for v in [v1, v2, v3, v4]:
                        st.session_state.all_ideas.append({"text": v, "color": couleur_attribuee})
                    
                    st.rerun()
                else:
                    st.error("Remplis tout !")
