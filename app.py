import streamlit as st
import requests
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configurazione Pagina
st.set_page_config(page_title="TCGtrack", page_icon="🃏", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; }
    .card-container { border: 1px solid #ddd; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 2. Connessione Database
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Funzioni con Caching (per velocità)
@st.cache_data(ttl=3600)
def get_all_sets():
    r = requests.get("https://api.pokemontcg.io/v2/sets")
    return sorted(r.json()['data'], key=lambda x: x['releaseDate'], reverse=True)

@st.cache_data(ttl=3600)
def get_cards_by_set(set_id):
    r = requests.get(f"https://api.pokemontcg.io/v2/cards?q=set.id:{set_id}")
    return r.json()['data']

# 4. Navigazione
tab_esplora, tab_collezione = st.tabs(["📚 Esplora Set", "🎒 La mia Collezione"])

# --- TAB ESPLORA (Stile Pokécardex) ---
with tab_esplora:
    sets = get_all_sets()
    set_names = [s['name'] for s in sets]
    selected_set_name = st.selectbox("Seleziona un Set Pokémon:", set_names)
    
    selected_set = next(s for s in sets if s['name'] == selected_set_name)
    st.image(selected_set['images']['logo'], width=200)
    
    cards = get_cards_by_set(selected_set['id'])
    
    # Carichiamo la collezione per vedere cosa abbiamo già
    try:
        current_coll = conn.read(worksheet="Collezione")
        owned_ids = current_coll['ID_Carta'].tolist()
    except:
        owned_ids = []

    st.write(f"### Carte del set: {selected_set_name} ({len(cards)} carte)")
    
    # Griglia a 3 colonne per mobile/desktop
    cols = st.columns(3)
    for idx, card in enumerate(cards):
        with cols[idx % 3]:
            st.image(card['images']['small'])
            is_owned = card['id'] in owned_ids
            
            label = "✅ Posseduta" if is_owned else "➕ Aggiungi"
            if st.button(label, key=card['id'], disabled=is_owned):
                new_row = pd.DataFrame([{
                    "Nome": card['name'],
                    "Set": selected_set_name,
                    "ID_Carta": card['id'],
                    "Immagine": card['images']['small']
                }])
                try:
                    # Leggi, aggiungi e aggiorna
                    df_old = conn.read(worksheet="Collezione")
                    df_new = pd.concat([df_old, new_row], ignore_index=True)
                    conn.update(worksheet="Collezione", data=df_new)
                    st.toast(f"{card['name']} aggiunta!")
                    st.rerun()
                except Exception as e:
                    st.error("Errore nel salvataggio. Verifica i Secrets.")

# --- TAB COLLEZIONE ---
with tab_collezione:
    st.header("La tua raccolta")
    try:
        df = conn.read(worksheet="Collezione")
        if df.empty:
            st.info("La tua collezione è ancora vuota. Inizia ad aggiungere carte!")
        else:
            # Mostra la collezione in griglia
            c_cols = st.columns(4)
            for i, row in df.iterrows():
                with c_cols[i % 4]:
                    st.image(row['Immagine'], caption=row['Nome'])
    except:
        st.warning("Configura il database nei Secrets di Streamlit.")
