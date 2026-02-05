import streamlit as st
import random
import json

# 1. CONFIGURATION & DESIGN FORCÉ
st.set_page_config(page_title="Bingo Reveal VIP", layout="centered")

COULEURS = ["#FF4B4B", "#4BFF4B", "#36D1FF", "#FF4BFF", "#FFD700", "#00FFC8", "#FF964B"]

st.markdown(f"""
    <style>
    .stApp {{ background-color: #121212 !important; color: #ffffff !important; }}
    
    .bingo-container {{ 
        display: grid; 
        grid-template-columns: repeat(5, 1fr); 
        gap: 8px; 
        width: 100%;
        max-width: 450px; 
        margin: 20px auto; 
    }}
    
    .bingo-box {{ 
        aspect-ratio: 1/1; 
        background: #ffffff !important; 
        color: #000000 !important; 
        border-radius: 10px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        text-align: center; 
        font-size: clamp(8px, 2.5vw, 11px); 
        font-weight: bold; 
        padding: 5px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 4px solid var(--player-color);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}

    .highlight {{ 
        transform: scale(1.1);
        z-index: 10;
        box-shadow: 0 0 20px var(--player-color);
        filter: brightness(1.1);
    }}
    
    .dimmed {{ opacity: 0.15; filter: grayscale(0.8) blur(1px); }}

    input {{ background-color: #ffffff !important; color: #000000 !important; border-radius: 8px !important; }}
    .stButton>button {{ 
        background: linear-gradient(90deg, #00d4ff, #0055ff) !important; 
        color: white !important; 
        border-radius: 25px !important; 
        font-weight: bold !important;
        border: none !important;
    }}
    .legend-card {{ 
        padding: 8px; border-radius: 8px; margin: 4px 0; 
        color: #000; font-weight: bold; font-size: 13px; text-align: center; 
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION DE LA MÉMOIRE
if 'all_ideas' not in st.session_state: st.session_state.all_ideas = []
if 'players' not in st.session_state: st.session_state.players = []

SECRET_CODE = "1234"
LIMIT = 7

# 3. BARRE LATÉRALE (SIDEBAR)
with st.sidebar:
    st.header("⚙️ Administration")
    
    # Import/Export pour ne jamais perdre les données
    with st.expander("💾 Sauvegarde / Restauration"):
        import_data = st.text_area("Code de sauvegarde :")
        if st.button("Charger les données"):
            try:
                data = json.loads(import_data)
                st.session_state.all_ideas = data['ideas']
                st.session_state.players = data['players']
                st.rerun()
            except: st.error("Format invalide")
        
        if st.session_state.all_ideas:
            current_save = json.dumps({"ideas": st.session_state.all_ideas, "players": st.session_state.players})
            st.code(current_save, language="json")

    st.divider()
    
    # Légende dynamique
    if st.session_state.players:
        st.subheader("🎨 Les Joueurs")
        for p in st.session_state.players:
            st.markdown(f'<div class="legend-card" style="background-color: {p["color"]};">{p["name"]}</div>', unsafe_allow_html=True)

    if st.button("🗑️ Réinitialiser tout"):
        st.session_state.clear()
        st.rerun()

# 4. CORPS DE L'APPLICATION
st.title("🎲 BINGO REVEAL PARTY")

# Phase A : Inscription
if len(st.session_state.players) < LIMIT:
    st.subheader(f"Inscription ({len(st.session_state.players)}/{LIMIT})")
    
    # Key dynamique pour reset le form à chaque nouvel utilisateur
    with st.form(key=f"user_form_{len(st.session_state.players)}", clear_on_submit=True):
        nom = st.text_input("Ton prénom :")
        c1 = st.text_input("Prédiction 1")
        c2 = st.text_input("Prédiction 2")
        c3 = st.text_input("Prédiction 3")
        c4 = st.text_input("Prédiction 4")
        
        if st.form_submit_button("Valider mes idées"):
            if nom and all([c1, c2, c3, c4]):
                if nom not in [p['name'] for p in st.session_state.players]:
                    player_color = COULEURS[len(st.session_state.players)]
                    st.session_state.players.append({"name": nom, "color": player_color})
                    for text in [c1, c2, c3, c4]:
                        st.session_state.all_ideas.append({"text": text, "color": player_color})
                    st.rerun()
                else: st.error("Prénom déjà pris !")
            else: st.error("Veuillez remplir tous les champs.")

# Phase B : Le Jeu
else:
    st.success("🎯 Tout le monde est prêt !")
    code_input = st.text_input("Entrez le code secret pour voir les grilles", type="password")
    
    if code_input == SECRET_CODE:
        current_player = st.selectbox("Qui regarde sa grille ?", ["-- Choisis ton nom --"] + [p['name'] for p in st.session_state.players])
        
        if current_player != "-- Choisis ton nom --":
            st.divider()
            reveal_query = st.text_input("🔍 Tape un mot pour révéler (ex: 'bière')").lower().strip()
            
            # Génération d'une grille stable basée sur le nom
            grid_pool = list(st.session_state.all_ideas)
            random.seed(current_player) # Grille identique pour un même nom
            random.shuffle(grid_pool)
            display_items = (grid_pool * 2)[:25]
            
            # Rendu de la grille
            grid_html = '<div class="bingo-container">'
            for item in display_items:
                # Logique de reveal
                status_class = ""
                if reveal_query:
                    if reveal_query in item['text'].lower():
                        status_class = "highlight"
                    else:
                        status_class = "dimmed"
                
                grid_html += f'''
                <div class="bingo-box {status_class}" style="--player-color: {item['color']};">
                    {item['text']}
                </div>
                '''
            grid_html += '</div>'
            st.markdown(grid_html, unsafe_allow_html=True)
            st.caption("📱 Conseil : Si tu trouves une case, fais un screenshot ou laisse ton mot dans la barre de recherche !")
