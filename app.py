import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta
import pytz

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="FANTAPODIO 2026", page_icon="🏎️", layout="wide")

# --- GESTIONE ORARIO (Deadline Roma) ---
tz = pytz.timezone('Europe/Rome')
ora_attuale = datetime.now(tz)

# Calendario GP 2026 
scadenze_gp = {
    "Australia (Melbourne)": "2026-03-15 05:00",
    "Cina (Shanghai)": "2026-03-22 08:00",
    "Giappone (Suzuka)": "2026-04-05 07:00",
    "Bahrain (Sakhir)": "2026-04-19 17:00",
    "Arabia Saudita (Jeddah)": "2026-04-26 19:00",
    "Miami": "2026-05-03 21:30",
    "Emilia-Romagna (Imola)": "2026-05-17 15:00",
    "Monaco": "2026-05-24 15:00",
    "Spagna (Barcelona)": "2026-06-07 15:00",
    "Canada (Montreal)": "2026-06-21 20:00",
    "Austria (Spielberg)": "2026-07-05 15:00",
    "Regno Unito (Silverstone)": "2026-07-12 16:00",
    "Belgio (Spa)": "2026-07-26 15:00",
    "Ungheria (Budapest)": "2026-08-02 15:00",
    "Olanda (Zandvoort)": "2026-08-23 15:00",
    "Italia (Monza)": "2026-08-30 15:00",
    "Azerbaijan (Baku)": "2026-09-13 13:00",
    "Singapore": "2026-09-20 14:00",
    "USA (Austin)": "2026-10-18 21:00",
    "Messico": "2026-10-25 21:00",
    "Brasile (Interlagos)": "2026-11-08 18:00",
    "Las Vegas": "2026-11-22 07:00",
    "Qatar (Lusail)": "2026-11-29 18:00",
    "Abu Dhabi (Yas Marina)": "2026-12-06 14:00"
}

# --- ELENCO PILOTI 2026 (Cadillac: Bottas/Perez | Audi: Hulkenberg/Bortoleto) ---
piloti_2026 = sorted([
    "Max Verstappen", "Liam Lawson", "Lewis Hamilton", "Charles Leclerc",
    "Lando Norris", "Oscar Piastri", "George Russell", "Kimi Antonelli",
    "Fernando Alonso", "Lance Stroll", "Carlos Sainz", "Alex Albon",
    "Nico Hulkenberg", "Gabriel Bortoleto", "Valtteri Bottas", "Sergio Perez",
    "Pierre Gasly", "Jack Doohan", "Yuki Tsunoda", "Isack Hadjar",
    "Esteban Ocon", "Oliver Bearman"
])

# --- FUNZIONE CALCOLO PUNTI ---
def calcola_punteggio(pronostico, reale, p1_ritirato):
    if pronostico == reale: return 50
    punti = 0
    for i in range(3):
        if pronostico[i] == reale[i]: punti += 10
        elif pronostico[i] in reale: punti += 5
    if p1_ritirato and pronostico[0] not in reale: punti -= 5
    return punti

# --- CONNESSIONE ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_storico = conn.read()

st.title("🏁 FANTAPODIO 2026")

# --- LEADERBOARD ---
if not df_storico.empty:
    st.subheader("🏆 Classifica Generale")
    punti_totali = df_storico[['Punti_CL', 'Punti_ML', 'Punti_FL']].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Team CL", f"{int(punti_totali['Punti_CL'])} pt")
    c2.metric("Team ML", f"{int(punti_totali['Punti_ML'])} pt")
    c3.metric("Team FL", f"{int(punti_totali['Punti_FL'])} pt")
    st.dataframe(df_storico, hide_index=True)

st.divider()

# --- SEZIONE COUNTDOWN E INSERIMENTO ---
st.subheader("📝 Pronostici e Risultati")
gp_scelto = st.selectbox("Seleziona Gran Premio", list(scadenze_gp.keys()))

# Calcolo Deadline e Countdown
data_limite = tz.localize(datetime.strptime(scadenze_gp[gp_scelto], "%Y-%m-%d %H:%M"))
differenza = data_limite - ora_attuale
aperto = ora_attuale < data_limite

# Visualizzazione Countdown
if aperto:
    giorni = differenza.days
    ore, resto = divmod(differenza.seconds, 3600)
    minuti, _ = divmod(resto, 60)
    st.info(f"⏳ **COUNTDOWN DEADLINE:** {giorni}g {ore}h {minuti}m al via!")
else:
    st.error(f"🔒 **PRONOSTICI CHIUSI.** Gara iniziata il {scadenze_gp[gp_scelto]}")

with st.form("main_form"):
    st.write("### 📤 Inserimento Dati")
    col_cl, col_ml, col_fl = st.columns(3)
    with col_cl:
        st.markdown("🥇 **Team CL**")
        cl_p = [st.selectbox(f"CL - P{i+1}", piloti_2026, key=f"cl_{i}") for i in range(3)]
    with col_ml:
        st.markdown("🥇 **Team ML**")
        ml_p = [st.selectbox(f"ML - P{i+1}", piloti_2026, key=f"ml_{i}") for i in range(3)]
    with col_fl:
        st.markdown("🥇 **Team FL**")
        fl_p = [st.selectbox(f"FL - P{i+1}", piloti_2026, key=f"fl_{i}") for i in range(3)]

    st.write("---")
    st.write("### 🏁 Risultato Ufficiale")
    cr1, cr2, cr3, cr4 = st.columns(4)
    r1 = cr1.selectbox("1° Reale", piloti_2026)
    r2 = cr2.selectbox("2° Reale", piloti_2026)
    r3 = cr3.selectbox("3° Reale", piloti_2026)
    p1_dnf = cr4.checkbox("Malus DNF (P1 ritirato?)")

    submit = st.form_submit_button("REGISTRA E AGGIORNA CLASSIFICA", disabled=not aperto)

if submit:
    reale = [r1, r2, r3]
    pt_cl = calcola_punteggio(cl_p, reale, p1_dnf)
    pt_ml = calcola_punteggio(ml_p, reale, p1_dnf)
    pt_fl = calcola_punteggio(fl_p, reale, p1_dnf)
    
    nuova_riga = pd.DataFrame([{
        "GP": gp_scelto, "Punti_CL": pt_cl, "Punti_ML": pt_ml, "Punti_FL": pt_fl, "Risultato": f"{r1}-{r2}-{r3}"
    }])
    
    df_finale = pd.concat([df_storico, nuova_riga], ignore_index=True)
    conn.update(data=df_finale)
    st.balloons()
    st.rerun()
