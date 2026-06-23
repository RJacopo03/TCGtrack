import streamlit as st
import requests
from streamlit_gsheets import GSheetsConnection

# Configurazione Pagina
st.set_page_config(page_title="TCGtrack", layout="centered")
st.title("🃏 TCGtrack")

# Connessione a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNZIONI API ---
def get_sets():
    response = requests.get("https://api.pokemontcg.io/v2/sets")
    return response.json().get("data", [])

def get_cards_by_set(set_id):
    # L'API filtra le carte per il set scelto
    url = f"https://api.pokemontcg.io/v2/cards?q=set.id:{set_id}"
    response = requests.get(url)
    return response.json().get("data", [])

# --- INTERFACCIA ---
menu = st.sidebar.radio("Navigazione", ["Cerca Carte", "I Miei Set"])

if menu == "Cerca Carte":
    st.header("Esplora i Set")
    sets = get_sets()
    
    # Creiamo un dizionario per avere nome set -> id set
    set_map = {s['name']: s['id'] for s in sets}
    selected_set_name = st.selectbox("Seleziona un set:", list(set_map.keys()))
    
    if selected_set_name:
        set_id = set_map[selected_set_name]
        cards = get_cards_by_set(set_id)
        
        st.write(f"### Carte in {selected_set_name}")
        for card in cards:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(card['images']['small'], width=100)
            with col2:
                st.write(f"**")
                if st.button(f"Aggiungi {card['name']}", key=card['id']):
                    # Logica per scrivere su Google Sheets
                    new_data = {"Nome": card['name'], "Set": selected_set_name}
                    # ... qui inserisci la logica per aggiungere al DF e salvare ...
                    st.success("Aggiunta!")

elif menu == "I Miei Set":
    st.header("La mia Collezione")
    try:
        df = conn.read(worksheet="Foglio1")
        st.dataframe(df)
    except:
        st.error("Collega il foglio Google Sheets nei Secrets!")
