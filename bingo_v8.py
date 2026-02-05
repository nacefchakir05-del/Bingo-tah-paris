import streamlit as st
import random
import json

# 1. CONFIGURATION
st.set_page_config(page_title="Bingo Reveal VIP", layout="centered")

COULEURS = ["#FF4B4B", "#4BFF4B", "#36D1FF", "#FF4BFF", "#FFD700", "#00FFC8", "#FF964B"]

st.markdown("""
    <style>
    .stApp { background-color: #121212 !important; color: #ffffff !important; }
    
    .bingo-container { 
        display: grid; 
        grid-template-columns: repeat(5, 1fr); 
        gap: 8px; 
        width: 100%;
        max-width: 450px; 
        margin: 20px auto; 
    }
    
    .bingo-box { 
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
        border: 4px solid var(--p-color);
        transition: all 0.3s ease;
    }

    /* Animation quand on trouve un mot */
    .found { 
        transform: scale(1.1);
        box-shadow: 0 0 20px var(--p-color);
        border-width: 6px;
        z-index: 2;
    }
    
    /* Quand on cherche, on estompe ce qui ne correspond pas */
    .not-found { opacity: 0.15; filter: grayscale(1) blur(1px); }

    input { background-color: #ffffff !important; color: #000000 !important; }
    .stButton>button { background: linear-gradient(90deg, #00d4ff, #0055ff) !important; color: white !important; border-radius: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION
if 'all_ideas' not in st.session_state: st.session_state.all_ideas = []
if 'players' not in st.session_state: st.session_state.players = []

SECRET_CODE = "1234"

# 3. SIDEBAR
with st.sidebar:
    st.header("⚙️ Admin")
    with st.expander("💾 Sauvegarde"):
        import_data = st.text_area("Code :")
        if st.button("Charger"):
            data = json.loads(import_data)
            st.session_state.all_ideas = data['ideas']
            st.session_state.players = data['players']
            st.rerun()
        if st.session_state.all_ideas:
            st.code(json.dumps({"ideas": st.session_state.all_ideas, "players": st.session_state.players}))
    
    if st.button("🗑️ Reset"):
        st.session_state.clear()
        st.rerun()

st.title("🎲 BINGO REVEAL")

# 4. LOGIQUE
if len(st.session_state.players) < 7:
    with st.form(key=f"f_{len(st.session_state.players)}", clear_on_submit=True):
        nom = st.text_input("Prénom :")
        i = [st.text_input(f"Idée {j+1}") for j in range(4)]
        if st.form_submit_button("Valider"):
            if nom and all(i):
                col = COULEURS[len(st.session_state.players)]
                st.session_state.players.append({"name": nom, "color": col})
                for txt in i:
                    st.session_state.all_ideas.append({"text": txt, "color": col})
                st.rerun()

else:
    code = st.text_input("Code secret :", type="password")
    if code == SECRET_CODE:
        joueur = st.selectbox("Qui regarde ?", ["--"] + [p['name'] for p in st.session_state.players])
        
        if joueur != "--":
            # Champ Reveal hors du formulaire pour réactivité immédiate
            search = st.text_input("🔍 Chercher un mot (ex: 'bière')").lower().strip()
            
            # Grille stable
            pool = list(st.session_state.all_ideas)
            random.seed(joueur)
            random.shuffle(pool)
            grid = (pool * 2)[:25]
            
            html = '<div class="bingo-container">'
            for item in grid:
                cls = "bingo-box"
                # On vérifie si la recherche est dans le texte
                if search:
                    if search in item['text'].lower():
                        cls += " found"
                    else:
                        cls += " not-found"
                
                html += f'<div class="{cls}" style="--p-color: {item["color"]}">{item["text"]}</div>'
            html += '</div>'
            
            st.markdown(html, unsafe_allow_html=True)
