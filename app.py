import streamlit as st
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="FANTAPODIO 2026", page_icon="🏎️", layout="wide")

# --- FUNZIONE CARICAMENTO DATI ---
def load_data():
    try:
        # Legge il link dai Secrets
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        
        # Forza il formato CSV per evitare errori di permessi
        if "pub?output=csv" not in url:
            # Se hai incollato il link normale, questo lo trasforma in link diretto
            if "/edit" in url:
                url = url.split("/edit")[0] + "/export?format=csv"
            elif "pubhtml" in url:
                url = url.replace("pubhtml", "pub?output=csv")
        
        return pd.read_csv(url)
    except Exception as e:
        # Se il foglio è vuoto o il link non va, crea una tabella base
        return pd.DataFrame(columns=["GP", "Team_CL", "Team_ML", "Team_FL", "Reale_1", "Reale_2", "Reale_3"])

# Carichiamo i dati all'avvio
df_storico = load_data()

# --- INTERFACCIA ---
st.title("🏁 FANTAPODIO 2026")
st.markdown("---")

# Visualizzazione dati esistenti
st.subheader("📊 Classifica e Storico")
if df_storico.empty:
    st.info("Nessun dato presente nel foglio Google. Inizia a inserire il primo GP!")
else:
    st.dataframe(df_storico, use_container_width=True)

st.markdown("---")

# --- SEZIONE INSERIMENTO ---
st.subheader("📝 Inserisci Risultati GP")

# Liste Piloti (Modificabili)
piloti = ["Verstappen", "Leclerc", "Hamilton", "Norris", "Sainz", "Piastri", "Russell", "Alonso", "Gasly", "Perez"]

with st.form("form_inserimento"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        gp_nome = st.text_input("Nome Gran Premio", placeholder="es. Bahrain")
        st.markdown("**Scelte Team**")
        scelta_cl = st.selectbox("Team CL", piloti)
        
    with col2:
        st.write("") # Spazio
        st.write("") # Spazio
        scelta_ml = st.selectbox("Team ML", piloti)
        scelta_fl = st.selectbox("Team FL", piloti)
        
    with col3:
        st.markdown("**Podio Reale**")
        r1 = st.selectbox("1° Classificato", piloti)
        r2 = st.selectbox("2° Classificato", piloti)
        r3 = st.selectbox("3° Classificato", piloti)

    submit = st.form_submit_button("CALCOLA E SALVA")

if submit:
    if not gp_nome:
        st.error("Inserisci il nome del Gran Premio!")
    else:
        st.success(f"Dati per il GP di {gp_nome} pronti per essere salvati!")
        st.balloons()
        # Nota: La scrittura richiede una configurazione extra (GSheets Connection)
        # Per ora verifichiamo che l'interfaccia funzioni!
        st.info("Nota: La funzione di scrittura sarà attivata appena confermi che vedi questa schermata senza errori.")
