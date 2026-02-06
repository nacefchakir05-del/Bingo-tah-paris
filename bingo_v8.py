import streamlit as st
import random
import json

# 1. CONFIGURATION & DESIGN RETRO-ARCADE
st.set_page_config(page_title="BINGO NEON REDUX", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    .stApp { background-color: #000 !important; font-family: 'VT323', monospace !important; }
    
    /* Textes Matrix/Neon */
    h1, h2, h3, p, label, .stMarkdown { 
        color: #00FF41 !important; 
        text-shadow: 0 0 8px #00FF41; 
        font-size: 18px; 
    }

    /* Grille Bingo */
    .bingo-container { 
        display: grid; grid-template-columns: repeat(5, 1fr); 
        gap: 6px; width: 100%; max-width: 450px; margin: auto; 
    }
    
    .bingo-box { 
        aspect-ratio: 1/1; background: #0a0a0a !important; 
        border: 1px solid #222; color: transparent !important;
        display: flex; align-items: center; justify-content: center; 
        text-align: center; font-size: 8px; /* Taille compacte */
        padding: 4px; border-radius: 4px; line-height: 1;
        transition: all 0.4s ease;
    }

    /* Case révélée */
    .revealed { 
        background: #000 !important; color: #FFFFFF !important; 
        border: 2px solid var(--p-color) !important; 
        box-shadow: 0 0 15px var(--p-color);
        font-weight: bold;
    }

    /* Sidebar Neon */
    section[data-testid="stSidebar"] { 
        background-color: #050505 !important; 
        border-right: 2px solid #FF00FF; 
    }
    
    input { 
        background-color: #111 !important; color: #00FFFF !important; 
        border: 1px solid #FF00FF !important; font-family: 'VT323' !important; 
    }
    
    .stButton>button { 
        background: #FF00FF !important; color: white !important; 
        border: 2px solid #00FFFF !important; font-size: 18px !important;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION DE LA MÉMOIRE SÉCURISÉE
if 'players' not in st.session_state: st.session_state.players = []
if 'all_ideas' not in st.session_state: st.session_state.all_ideas = []
if 'reveals' not in st.session_state: st.session_state.reveals = {}

SECRET = "1234"
FLASHY_COLORS = ["#FF00FF", "#00FFFF", "#FFFF00", "#00FF41", "#FF4B4B", "#FF8000", "#BF00FF"]

# 3. SIDEBAR (BACKUP ET LÉGENDE)
with st.sidebar:
    st.title("💾 SYSTEM CONTROL")
    
    # SAUVEGARDE / RESTAURATION
    with st.expander("RESTAURER UNE SESSION"):
        restore_input = st.text_area("Coller le code ici :")
        if st.button("LANCER LA RESTAURATION"):
            try:
                data = json.loads(restore_input)
                st.session_state.players = data['players']
                st.session_state.all_ideas = data['ideas']
                st.session_state.reveals = data.get('reveals', {})
                st.success("DATA SYNC OK")
                st.rerun()
            except:
                st.error("CODE CORROMPU")

    if st.session_state.all_ideas:
        st.subheader("CODE DE SAUVEGARDE :")
        current_state = {
            "players": st.session_state.players,
            "ideas": st.session_state.all_ideas,
            "reveals": st.session_state.reveals
        }
        st.code(json.dumps(current_state))

    st.divider()
    if st.session_state.players:
        st.subheader("TEAM STATUS")
        for p in st.session_state.players:
            st.markdown(f'<p style="color:{p["color"]};">>> {p["name"]}</p>', unsafe_allow_html=True)

    if st.button("RESET TOTAL"):
        st.session_state.clear()
        st.rerun()

# 4. LOGIQUE PRINCIPALE : NAVIGATION PAR ÉTAPES
st.title("👾 NEON BINGO ARCADE")

# ÉTAPE 1 : INSCRIPTION (Tant qu'on n'a pas 7 joueurs)
if len(st.session_state.players) < 7:
    st.header(f"INSCRIPTION : PLAYER {len(st.session_state.players) + 1}/7")
    
    # Formulaire avec clé unique pour éviter les conflits
    with st.form(key=f"player_reg_{len(st.session_state.players)}", clear_on_submit=True):
        new_name = st.text_input("NOM :")
        pred1 = st.text_input("PRÉDICTION 1")
        pred2 = st.text_input("PRÉDICTION 2")
        pred3 = st.text_input("PRÉDICTION 3")
        pred4 = st.text_input("PRÉDICTION 4")
        
        submit = st.form_submit_button("VALIDER")
        
        if submit:
            if new_name and pred1 and pred2 and pred3 and pred4:
                # Attribution de la couleur
                p_color = FLASHY_COLORS[len(st.session_state.players)]
                # Sauvegarde immédiate dans le state
                st.session_state.players.append({"name": new_name, "color": p_color})
                for idea in [pred1, pred2, pred3, pred4]:
                    st.session_state.all_ideas.append({"text": idea, "color": p_color})
                # Forcer le rafraîchissement pour passer au suivant ou au jeu
                st.rerun()
            else:
                st.error("REMPLIS TOUTES LES CASES !")

# ÉTAPE 2 : LE JEU (Une fois les 7 inscrits)
else:
    st.subheader("🎯 TOUS LES JOUEURS SONT PRÊTS")
    access_code = st.text_input("ENTRER CODE D'ACCÈS :", type="password")
    
    if access_code == SECRET:
        user_select = st.selectbox("QUI ES-TU ?", [p['name'] for p in st.session_state.players])
        
        if user_select:
            # S'assurer que le dictionnaire de révélations existe pour ce joueur
            if user_select not in st.session_state.reveals:
                st.session_state.reveals[user_select] = []

            st.divider()
            st.write("🔍 **REVEAL SCANNER** (Tape 2 mots minimum)")
            search_query = st.text_input("EX: ' Thomas tombe '").lower().strip()
            
            # Génération de la grille stable (Seedée sur le nom)
            full_pool = list(st.session_state.all_ideas)
            random.seed(user_select)
            random.shuffle(full_pool)
            final_grid = (full_pool * 2)[:25]

            # LOGIQUE DE RÉVÉLATION (Min 2 mots de min 2 lettres)
            words = [w for w in search_query.split() if len(w) >= 2]
            if len(words) >= 2:
                for idx, item in enumerate(final_grid):
                    if all(word in item['text'].lower() for word in words):
                        if idx not in st.session_state.reveals[user_select]:
                            st.session_state.reveals[user_select].append(idx)
                            st.toast(f"CASE DÉBLOQUÉE : {item['text']}")

            # AFFICHAGE DE LA GRILLE
            grid_html = '<div class="bingo-container">'
            for idx, item in enumerate(final_grid):
                is_revealed = idx in st.session_state.reveals[user_select]
                
                box_class = "bingo-box revealed" if is_revealed else "bingo-box"
                txt = item['text'] if is_revealed else "???"
                clr = item['color'] if is_revealed else "#333"
                
                grid_html += f'<div class="{box_class}" style="--p-color: {clr};">{txt}</div>'
            grid_html += '</div>'
            
            st.markdown(grid_html, unsafe_allow_html=True)
            st.write(f"SCORE : {len(st.session_state.reveals[user_select])} / 25")
    elif access_code != "":
        st.error("CODE ERRONÉ")
