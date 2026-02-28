import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 🏎️ 1. CONFIGURAZIONE PAGINA E STILE
st.set_page_config(page_title="FANTAPODIO 2.0", page_icon="🏎️", layout="centered")

st.markdown("""
<style>
    .team-cl { background-color: #ffcccc; color: #cc0000; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; }
    .team-ml { background-color: #ccffcc; color: #006600; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; }
    .team-fl { background-color: #ccebff; color: #004d99; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; }
    .main-title { color: #333; font-size: 32px; font-weight: bold; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 🔗 2. CONNESSIONE DATABASE (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(worksheet="Foglio1")

df_storico = load_data()

# 🏎️ 3. DATABASE PILOTI 2026
piloti_2026 = [
    "Scegli un pilota...", "L. Hamilton (Ferrari)", "C. Leclerc (Ferrari)", 
    "M. Verstappen (Red Bull)", "I. Hadjar (Red Bull)", "L. Norris (McLaren)", 
    "O. Piastri (McLaren)", "G. Russell (Mercedes)", "A. K. Antonelli (Mercedes)", 
    "F. Alonso (Aston Martin)", "L. Stroll (Aston Martin)", "C. Sainz (Williams)", 
    "A. Albon (Williams)", "N. Hulkenberg (Audi)", "G. Bortoleto (Audi)", 
    "P. Gasly (Alpine)", "F. Colapinto (Alpine)", "E. Ocon (Haas)", 
    "O. Bearman (Haas)", "S. Perez (Cadillac)", "V. Bottas (Cadillac)", 
    "L. Lawson (RB)", "A. Lindblad (RB)"
]

# 🏁 4. LOGICA PUNTI
def calcola_punti(pronostico, reale, dnf_p1, penalizzati):
    if "Scegli un pilota..." in pronostico: return 0
    p = 0
    for i in range(3):
        if pronostico[i] == reale[i]: p += 10
        elif pronostico[i] in reale: p += 5
    if pronostico == reale: p += 20 # Bonus En Plein
    if dnf_p1: p -= 5 # Malus DNF
    for pilota in pronostico:
        if pilota in penalizzati: p -= 3 # Malus Penalità FIA
    return p

# --- INTERFACCIA UTENTE ---
st.markdown('<div class="main-title">🏁 FANTAPODIO 2.0</div>', unsafe_allow_html=True)

# 📝 INSERIMENTO PRONOSTICI
with st.expander("📝 Inserisci Pronostici Team", expanded=True):
    col_cl, col_ml, col_fl = st.columns(3)
    with col_cl:
        st.markdown('<div class="team-cl">TEAM CL</div>', unsafe_allow_html=True)
        cl = [st.selectbox(f"CL P{i+1}", piloti_2026, key=f"cl{i}") for i in range(3)]
    with col_ml:
        st.markdown('<div class="team-ml">TEAM ML</div>', unsafe_allow_html=True)
        ml = [st.selectbox(f"ML P{i+1}", piloti_2026, key=f"ml{i}") for i in range(3)]
    with col_fl:
        st.markdown('<div class="team-fl">TEAM FL</div>', unsafe_allow_html=True)
        fl = [st.selectbox(f"FL P{i+1}", piloti_2026, key=f"fl{i}") for i in range(3)]

# 🏆 RISULTATO REALE
st.divider()
st.header("🏆 Risultato Ufficiale FIA")
gp_nome = st.text_input("Nome Gran Premio (es. Australia)")
r1 = st.selectbox("1° POSTO", piloti_2026, key="r1")
r2 = st.selectbox("2° POSTO", piloti_2026, key="r2")
r3 = st.selectbox("3° POSTO", piloti_2026, key="r3")
reale = [r1, r2, r3]

col_m1, col_m2 = st.columns(2)
with col_m1: dnf = st.checkbox("Il P1 pronosticato è DNF? (-5 pt)")
with col_m2: pen = st.multiselect("Piloti penalizzati post-gara (-3 pt)", piloti_2026)

# 💾 SALVATAGGIO
if st.button("CALCOLA E SALVA NEL CAMPIONATO"):
    if "Scegli un pilota..." in reale or not gp_nome:
        st.error("Inserisci il nome del GP e il podio reale!")
    else:
        p_cl = calcola_punti(cl, reale, dnf, pen)
        p_ml = calcola_punti(ml, reale, dnf, pen)
        p_fl = calcola_punti(fl, reale, dnf, pen)
        
        nuova_riga = pd.DataFrame([{"GP": gp_nome, "Team_CL": p_cl, "Team_ML": p_ml, "Team_FL": p_fl}])
        df_aggiornato = pd.concat([df_storico, nuova_riga], ignore_index=True)
        conn.update(worksheet="Foglio1", data=df_aggiornato)
        st.balloons()
        st.success(f"Risultati {gp_nome} salvati!")

# 📊 CLASSIFICA GENERALE
st.divider()
st.header("📊 Classifica Generale")
if not df_storico.empty:
    totali = {
        "TEAM": ["Team CL", "Team ML", "Team FL"],
        "Punti": [df_storico["Team_CL"].sum(), df_storico["Team_ML"].sum(), df_storico["Team_FL"].sum()]
    }
    st.table(pd.DataFrame(totali).sort_values(by="Punti", ascending=False).set_index("TEAM"))
else:
    st.info("Nessun dato ancora salvato nel campionato.")
