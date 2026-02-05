import streamlit as st
import random
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Bingo du Week-end", page_icon="🎲")

st.title("🎲 Bingo Secret")
st.write("Chacun soumet 4 idées anonymement. Une fois que tout le monde a fini, générez votre grille !")

# On utilise le 'session_state' pour stocker les idées pendant que l'app tourne
if 'liste_idees' not in st.session_state:
    st.session_state.liste_idees = []

# --- FORMULAIRE D'AJOUT ---
with st.form("form_ajout", clear_on_submit=True):
    st.subheader("Ajouter mes 4 prédictions")
    i1 = st.text_input("Idée 1")
    i2 = st.text_input("Idée 2")
    i3 = st.text_input("Idée 3")
    i4 = st.text_input("Idée 4")
    bouton = st.form_submit_button("Envoyer")
    
    if bouton:
        if i1 and i2 and i3 and i4:
            st.session_state.liste_idees.extend([i1, i2, i3, i4])
            st.success("C'est envoyé ! Prochaine personne ?")
        else:
            st.warning("Remplis les 4 cases !")

st.divider()

# --- AFFICHAGE DU COMPTEUR ---
nb_idees = len(st.session_state.liste_idees)
st.sidebar.metric("Total d'idées reçues", nb_idees)
st.sidebar.write(f"Objectif : 28 idées (7 personnes x 4)")

# --- GÉNÉRATION DE LA GRILLE ---
if nb_idees >= 10: # On débloque à partir de 10 pour tester
    st.subheader("Générer ma grille personnelle")
    nom = st.text_input("Ton prénom (pour le titre)")
    
    if st.button("Afficher ma grille"):
        # On mélange toutes les idées
        toutes_les_idees = st.session_state.liste_idees.copy()
        random.shuffle(toutes_les_idees)
        
        # On crée une grille 4x4 (16 cases) ou 5x5 (25 cases)
        taille = 4 if nb_idees < 25 else 5
        selection = toutes_les_idees[:taille*taille]
        
        # Transformation en tableau
        grille = [selection[i:i+taille] for i in range(0, len(selection), taille)]
        df = pd.DataFrame(grille)
        
        st.write(f"### Grille de {nom}")
        st.table(df)
        st.info("Prends un screenshot de ta grille !")
else:
    st.info("En attente d'assez d'idées pour générer les grilles...")

if st.sidebar.button("Réinitialiser tout (Attention !)"):
    st.session_state.liste_idees = []
    st.rerun()
