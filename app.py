import streamlit as st
import requests
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="TCGtrack", layout="centered")

# Connessione a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🃏 TCGtrack Pro")

tab1, tab2 = st.tabs(["🔍 Cerca", "📁 Collezione"])

with tab1:
    query = st.text_input("Cerca Pokémon")
    if query:
        res = requests.get(f"https://api.pokemontcg.io/v2/cards?q=name:{query}*&pageSize=5")
        cards = res.json().get('data', [])
        for c in cards:
            st.image(c['images']['small'], width=100)
            st.write(f"**{c['name']}**")
            if st.button(f"Salva {c['name']}", key=c['id']):
                # Salva su Google Sheets
                df = pd.DataFrame([{"Nome": c['name'], "Set": c['set']['name'], "Tipo": "Singola", "Prezzo": 0}])
                conn.update(worksheet="Foglio1", data=df)
                st.success("Salvato su Google Sheets!")

with tab2:
    st.write("La tua collezione dal database:")
    df_collezione = conn.read(worksheet="Foglio1")
    st.dataframe(df_collezione)
