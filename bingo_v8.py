import streamlit as st
import random
import json

# 1. CONFIGURATION & DESIGN ULTRA-FLASHY
st.set_page_config(page_title="NEON BINGO REVEAL", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    /* Fond Noir Total */
    .stApp {
        background-color: #000000 !important;
        font-family: 'Press Start 2P', cursive !important;
    }

    /* Textes en Vert Flashy */
    h1, h2, h3, p, label, .stMarkdown {
        color: #00FF41 !important;
        text-shadow: 0 0 5px #00FF41;
        font-size: 12px;
    }

    /* Grille Bingo */
    .bingo-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 10px;
        width: 100%;
        max-width: 480px;
        margin: auto;
    }

    /* Cases du Bingo */
    .bingo-box {
        aspect-ratio: 1/1;
        background: #111 !important;
        border: 2px solid #333;
        color: #333 !important; /* Texte caché */
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 8px;
        padding: 5px;
        border-radius: 5px;
        transition: all 0.3s;
    }

    /* Case RÉVÉLÉE : Couleurs Flashy */
    .revealed {
        background: #000 !important;
        color: #FFFFFF !important; /* Texte Blanc Flashy sur fond noir */
        border: 3px solid var(--p-color) !important;
        box-shadow: 0 0 15px var(--p-color);
        text-shadow: 0 0 5px #FFF;
    }

    /* Sidebar Flashy */
    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 3px solid #FF00FF;
    }

    /* Inputs */
    input { 
        background-color: #111 !important; 
        color: #00FFFF !important; 
        border: 2px solid #FF00FF !important;
        font-family: 'Press Start 2P', cursive !important;
    }
    
    .stButton>button {
        background: #FF00FF !important;
        color: white !important;
        border: 3px solid #00FFFF !important;
        width: 100%;
        font-family: 'Press Start 2P', cursive !important;
        font-size: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ÉTAT DU JEU
if 'players' not in st.session_state: st.session_state.players = []
if 'all_ideas' not in st.session_state: st.session_state.all_ideas = []
# On stocke les révélations sous forme de liste pour que le JSON l'accepte
if 'reveals' not in st.session_state: st.session_state.reveals = {} 

FLASHY_COLORS = ["#FF00FF", "#00FFFF", "#FFFF00", "#00FF41", "#FF4B4B", "#FF8000", "#BF00FF"]
SECRET = "1234"

# 3. SIDEBAR : SYSTÈME DE SAUVEGARDE TOTALE
with st.sidebar:
    st.title("📟 SYSTEM")
    
    # Zone de restauration
    with st.expander("💾 BACKUP / RESTORE"):
        restore_code = st.text_area("Coller code de sauvegarde :")
        if st.button("RESTAURER LA SESSION"):
            try:
                data = json.loads(restore_code)
                st.session_state.players = data['players']
                st.session_state.all_ideas = data['ideas']
                st.session_state.reveals = data['reveals']
                st.success("Session synchronisée !")
                st.rerun()
            except:
                st.error("Code corrompu !")

    # Génération du code de sauvegarde
    if st.session_state.all_ideas:
        st.subheader("CODE ACTUEL (A COPIER)")
        full_backup = {
            "players": st.session_state.players,
            "ideas": st.session_state.all_ideas,
            "reveals": st.session_state.reveals
        }
        st.code(json.dumps(full_backup), language="json")

    # Légende
    if st.session_state.players:
        st.subheader("PLAYER LIST")
        for p in st.session_state.players:
            st.markdown(f'<p style="color:{p["color"]};">>> {p["name"]}</p>', unsafe_allow_html=True)

    if st.button("HARD RESET"):
        st.session_state.clear()
        st.rerun()

# 4. ÉTAPE 1 : INSCRIPTION
if len(st.session_state.players) < 7:
    st.title("👾 NEW GAME")
    with st.form(key=f"join_{len(st.session_state.players)}", clear_on_submit=True):
        name = st.text_input("PLAYER NAME :")
        p1 = st.text_input("PREDICTION 1")
        p2 = st.text_input("PREDICTION 2")
        p3 = st.text_input("PREDICTION 3")
        p4 = st.text_input("PREDICTION 4")
        if st.form_submit_button("INSERT COIN"):
            if name and p1 and p2 and p3 and p4:
                color = FLASHY_COLORS[len(st.session_state.players)]
                st.session_state.players.append({"name": name, "color": color})
                for text in [p1, p2, p3, p4]:
                    st.session_state.all_ideas.append({"text": text, "color": color})
                st.rerun()

# 5. ÉTAPE 2 : RÉVÉLATION (LE JEU)
else:
    st.title("🕹️ BINGO TIME")
    pwd = st.text_input("ENTER ACCESS CODE :", type="password")
    
    if pwd == SECRET:
        current_user = st.selectbox("WHO ARE YOU?", [p['name'] for p in st.session_state.players])
        
        # Initialiser les révélations pour ce joueur si nécessaire
        if current_user not in st.session_state.reveals:
            st.session_state.reveals[current_user] = []

        st.divider()
        st.subheader("🔍 REVEAL SCANNER")
        search = st.text_input("Taper 2 mots-clés (ex: 'bière renversée')").lower().strip()
        
        # Génération Grille Stable
        grid = list(st.session_state.all_ideas)
        random.seed(current_user)
        random.shuffle(grid)
        grid = (grid * 2)[:25]

        # LOGIQUE DE RÉVÉLATION
        search_words = [w for w in search.split() if len(w) >= 2]
        
        if len(search_words) >= 2:
            for idx, item in enumerate(grid):
                # On vérifie si CHAQUE mot de la recherche est dans la phrase
                if all(word in item['text'].lower() for word in search_words):
                    if idx not in st.session_state.reveals[current_user]:
                        st.session_state.reveals[current_user].append(idx)
                        st.toast(f"CASE RÉVÉLÉE : {item['text']}")

        # AFFICHAGE
        html = '<div class="bingo-container">'
        for idx, item in enumerate(grid):
            is_rev = idx in st.session_state.reveals[current_user]
            
            box_class = "bingo-box revealed" if is_rev else "bingo-box"
            text_content = item['text'] if is_rev else "???"
            b_color = item['color'] if is_rev else "#333"
            
            html += f'<div class="{box_class}" style="--p-color: {b_color};">{text_content}</div>'
        html += '</div>'
        
        st.markdown(html, unsafe_allow_html=True)
