import streamlit as st
import requests
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Pokécardex", page_icon="🃏", layout="centered")

# --- CSS per stile Pokecardex ---
st.markdown("""
    <style>
    .card-box { background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
    div.stButton > button { width: 100%; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNZIONI ---
@st.cache_data(ttl=3600)
def get_sets():
    r = requests.get("https://api.pokemontcg.io/v2/sets")
    return r.json()['data']

def load_collection():
    try:
        return conn.read(worksheet="Collezione")
    except:
        return pd.DataFrame(columns=["Nome", "Set", "ID_Carta", "Immagine"])

# --- INTERFACCIA ---
st.title("🃏 Pokécardex")
tab1, tab2 = st.tabs(["ESPLORA", "COLLEZIONE"])

with tab1:
    sets = get_sets()
    set_choice = st.selectbox("Seleziona Set", [s['name'] for s in sets])
    selected_set = next(s for s in sets if s['name'] == set_choice)
    
    cards = requests.get(f"https://api.pokemontcg.io/v2/cards?q=set.id:{selected_set['id']}").json()['data']
    
    coll = load_collection()
    
    for card in cards:
        with st.container():
            col1, col2 = st.columns([1, 3])
            col1.image(card['images']['small'], width=80)
            col2.write(f"**")
            
            is_owned = card['id'] in coll['ID_Carta'].values
            if is_owned:
                col2.success("✅ Posseduta")
            else:
                if col2.button("➕ Aggiungi", key=card['id']):
                    new_df = pd.concat([coll, pd.DataFrame([{
                        "Nome": card['name'], "Set": set_choice, 
                        "ID_Carta": card['id'], "Immagine": card['images']['small']
                    }])], ignore_index=True)
                    conn.update(worksheet="Collezione", data=new_df)
                    st.rerun()

with tab2:
    st.subheader("La tua raccolta")
    df = load_collection()
    st.dataframe(df[['Nome', 'Set']], use_container_width=True)
