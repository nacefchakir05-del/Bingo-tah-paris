import streamlit as st
import random
import json

# 1. CONFIGURATION & STYLE RETRO
st.set_page_config(page_title="BINGO SEMI_Safe place", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    /* Fond style Arcade */
    .stApp {
        background-color: #050505 !important;
        background-image: radial-gradient(#1a1a2e 0.5px, transparent 0.5px);
        background-size: 20px 20px;
        color: #00ff41 !important; /* Vert Matrix */
        font-family: 'VT323', monospace !important;
    }

    /* Grille Bingo */
    .bingo-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 10px;
        max-width: 500px;
        margin: 20px auto;
    }

    /* Cases du Bingo */
    .bingo-box {
        aspect-ratio: 1/1;
        background: #111 !important;
        border: 3px solid #333;
        color: #555 !important; /* Texte caché (sombre) par défaut */
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 14px;
        padding: 5px;
        border-radius: 5px;
        transition: all 0.5s ease;
        text-transform: uppercase;
    }

    /* Style Case Révélée (Glow Néon) */
    .revealed {
        background: #fff !important;
        color: #000 !important;
        border: 4px solid var(--p-color) !important;
        box-shadow: 0 0 15px var(--p-color), inset 0 0 10px var(--p-color);
        transform: scale(1.02);
    }

    /* Sidebar Style */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 2px solid #00ff41;
    }

    .legend-item {
        padding: 8px;
        margin: 5px 0;
        border: 1px solid #333;
        border-radius: 5px;
        font-size: 18px;
    }

    /* Inputs et Boutons Retro */
    input { background-color: #222 !important; color: #00ff41 !important; border: 1px solid #00ff41 !important; }
    .stButton>button {
        background-color: #ff00ff !important; /* Rose Néon */
        color: white !important;
        border: none !important;
        box-shadow: 4px 4px 0px #800080;
        font-family: 'VT323', monospace !important;
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION DE LA MÉMOIRE (SESSION STATE)
if 'players' not in st.session_state: st.session_state.players = []
if 'all_ideas' not in st.session_state: st.session_state.all_ideas = []
if 'revealed_indices' not in st.session_state: st.session_state.revealed_indices = {} # Par joueur

COLORS = ["#00ffff", "#ff00ff", "#ffff00", "#ff0000", "#00ff00", "#ff8000", "#ffffff"]
SECRET = "1234"

# 3. BARRE LATÉRALE : LÉGENDE & SAUVEGARDE
with st.sidebar:
    st.title("🕹️ STATUS")
    
    if st.session_state.players:
        st.subheader("LÉGENDE JOUEURS")
        for p in st.session_state.players:
            st.markdown(f'<div class="legend-item" style="color: {p["color"]}; border-color: {p["color"]};">■ {p["name"]}</div>', unsafe_allow_html=True)
    
    st.divider()
    with st.expander("💾 BACKUP SYSTEM"):
        save_code = st.text_area("Coller code ici :")
        if st.button("RESTAURER"):
            data = json.loads(save_code)
            st.session_state.all_ideas = data['ideas']
            st.session_state.players = data['players']
            st.rerun()
        
        if st.session_state.all_ideas:
            current_json = json.dumps({"ideas": st.session_state.all_ideas, "players": st.session_state.players})
            st.code(current_json)

    if st.button("RESET GAME"):
        st.session_state.clear()
        st.rerun()

# 4. LOGIQUE PRINCIPALE
st.title("👾 BINGO RADICAL 80S")

# PHASE 1 : INSCRIPTION (7 JOUEURS)
if len(st.session_state.players) < 7:
    st.header(f"READY PLAYER {len(st.session_state.players)+1}")
    with st.form(key=f"reg_{len(st.session_state.players)}", clear_on_submit=True):
        nom = st.text_input("NOM DU JOUEUR :")
        i1 = st.text_input("PRÉDICTION 1")
        i2 = st.text_input("PRÉDICTION 2")
        i3 = st.text_input("PRÉDICTION 3")
        i4 = st.text_input("PRÉDICTION 4")
        if st.form_submit_button("S'INSCRIRE"):
            if nom and i1 and i2 and i3 and i4:
                p_color = COLORS[len(st.session_state.players)]
                st.session_state.players.append({"name": nom, "color": p_color})
                for text in [i1, i2, i3, i4]:
                    st.session_state.all_ideas.append({"text": text, "color": p_color})
                st.rerun()

# PHASE 2 : LE JEU
else:
    st.subheader("INSERT COIN TO REVEAL")
    pwd = st.text_input("CODE D'ACCÈS :", type="password")
    
    if pwd == SECRET:
        user_view = st.selectbox("CHOISIS TA GRILLE :", [p['name'] for p in st.session_state.players])
        
        # Initialisation de la mémoire de révélation pour ce joueur si vide
        if user_view not in st.session_state.revealed_indices:
            st.session_state.revealed_indices[user_view] = set()

        st.divider()
        st.write("🔍 **REVEAL SYSTEM** : Tape au moins 2 mots clés pour valider une case !")
        search = st.text_input("EX: 'BIERE RENVERSEE'", key="search_bar").lower().strip()

        # LOGIQUE DE RÉVÉLATION (2 MOTS CLÉS MINIMUM)
        search_words = [w for w in search.split() if len(w) >= 2]
        
        # Génération Grille Stable
        grid_data = list(st.session_state.all_ideas)
        random.seed(user_view)
        random.shuffle(grid_data)
        grid_data = (grid_data * 2)[:25]

        # Vérification des nouveaux "Reveals"
        if len(search_words) >= 2:
            for idx, item in enumerate(grid_data):
                # Si tous les mots de la recherche sont dans la case
                if all(word in item['text'].lower() for word in search_words):
                    st.session_state.revealed_indices[user_view].add(idx)

        # AFFICHAGE GRILLE
        html_grid = '<div class="bingo-container">'
        for idx, item in enumerate(grid_data):
            is_revealed = idx in st.session_state.revealed_indices[user_view]
            
            style_class = "bingo-box revealed" if is_revealed else "bingo-box"
            content = item['text'] if is_revealed else "???"
            border_color = item['color'] if is_revealed else "#333"
            
            html_grid += f'''
            <div class="{style_class}" style="--p-color: {border_color};">
                {content}
            </div>
            '''
        html_grid += '</div>'
        
        st.markdown(html_grid, unsafe_allow_html=True)
        
        if st.session_state.revealed_indices[user_view]:
            st.success(f"SCORE : {len(st.session_state.revealed_indices[user_view])} cases trouvées !")
