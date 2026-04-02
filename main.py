import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import gspread  
from num2words import num2words
import requests
import base64
import re

# ==========================================
# 1. CONFIGURAZIONE PAGINA E COLLEGAMENTO
# ==========================================
st.set_page_config(page_title="Junior Club Terni", layout="wide", initial_sidebar_state="expanded")
URL_WEB_APP = "https://script.google.com/macros/s/AKfycbwP8if8l0wZ6OuhQxnPVsLu33F23RzLYp7LsKrnbB8WXhEYkh3Wjx63JeFmyVKDOr4/exec"

st.components.v1.html("""
    <script>
        window.parent.document.documentElement.lang = 'it';
        window.parent.document.documentElement.setAttribute('translate', 'no');
        window.parent.document.documentElement.className += ' notranslate';
    </script>
""", height=0, width=0)

# ==========================================
# 1.5 SISTEMA DI LOGIN (PASSWORD)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<br><br><br><h2 style='text-align: center; color: #0F172A; font-family: sans-serif;'>🔒 Accesso Riservato Junior Club</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        pwd = st.text_input("Inserisci la password", type="password")
        if st.button("Accedi", type="primary", use_container_width=True):
            if pwd == "admin":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Password errata!")
    st.stop() 

# ==========================================
# 2. DESIGN DEFINITIVO 
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
#MainMenu {visibility: hidden;} footer {visibility: hidden;} 
[data-testid="stHeader"] { background-color: transparent !important; }
.stAppDeployButton { display: none !important; }
.stApp { background-color: #F1F5F9 !important; font-family: 'Inter', sans-serif !important; }
[data-testid="block-container"] { max-width: 1200px !important; padding-top: 0px !important; margin-top: -110px !important; padding-bottom: 2rem !important; }
.stMain > div:first-child { padding-top: 0px !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #FF6501 0%, #D95300 100%) !important; border-right: none !important; box-shadow: 4px 0 20px rgba(0,0,0,0.15); }
.sidebar-title { color: #FFFFFF; font-weight: 900; font-size: 26px; text-align: center; margin-top: 10px; margin-bottom: 35px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); letter-spacing: -0.5px;}
[data-testid="stSidebar"] div[role="radiogroup"] { gap: 12px; padding: 0 15px; }
[data-testid="stSidebar"] .stRadio label { background-color: rgba(255,255,255,0.08) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 12px !important; padding: 16px 20px !important; cursor: pointer; transition: all 0.3s ease; }
[data-testid="stSidebar"] .stRadio label:hover { background-color: rgba(255,255,255,0.15) !important; transform: translateX(4px); }
[data-testid="stSidebar"] .stRadio div[role="radio"] { display: none !important; }
[data-testid="stSidebar"] .stRadio label p { color: #FFFFFF !important; font-size: 16px !important; font-weight: 600 !important; margin: 0 !important; }
[data-testid="stSidebar"] .stRadio label:has(input:checked) { background-color: #FFFFFF !important; box-shadow: 0 8px 20px rgba(0,0,0,0.2) !important; border: none !important; transform: scale(1.02); }
[data-testid="stSidebar"] .stRadio label:has(input:checked) p { color: #FF6501 !important; font-weight: 900 !important; font-size: 17px !important; }
[data-testid="stSidebar"] button { background-color: rgba(0,0,0,0.15) !important; border: 1px solid rgba(255,255,255,0.2) !important; color: #FFFFFF !important; border-radius: 10px !important; padding: 12px !important; font-weight: 700 !important; font-size: 15px !important; transition: all 0.2s; margin-top: 25px; width: 90%; margin-left: 5%; }
[data-testid="stSidebar"] button:hover { background-color: rgba(0,0,0,0.3) !important; }
.titolo-app { color: #0F172A; font-size: 32px; font-weight: 900; letter-spacing: -1px; margin-bottom: 0px; padding-top: 0px; line-height: 1.2; }
.sottotitolo { color: #64748B; font-size: 15px; font-weight: 600; margin-bottom: 12px; margin-top: 4px;}
[data-testid="stVerticalBlockBorderWrapper"] { background-color: #FFFFFF !important; border-radius: 16px !important; border: 1px solid #E2E8F0 !important; box-shadow: 0 10px 30px -10px rgba(0,0,0,0.08) !important; padding: 30px 45px !important; margin-bottom: 1rem !important; }
.section-header { font-size: 14px; font-weight: 800; color: #1E293B; text-transform: uppercase; letter-spacing: 1px; margin-top: 20px; margin-bottom: 15px; padding: 10px 15px; background-color: #F8FAFC; border-radius: 8px; border-left: 5px solid #FF6501; display: flex; align-items: center; }
.section-header i { margin-right: 12px; font-style: normal; font-size: 18px; color: #FF6501; }
.stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox div[data-baseweb="select"] { background-color: #FFFFFF !important; border: 2px solid #E2E8F0 !important; border-radius: 10px !important; padding: 14px 16px !important; font-size: 16px !important; font-weight: 700 !important; color: #0F172A !important; box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important; transition: all 0.2s ease !important; }
.stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus, .stSelectbox div[data-baseweb="select"]:focus-within { border-color: #FF6501 !important; box-shadow: 0 0 0 4px rgba(255, 101, 1, 0.15) !important; }
.stTextInput label, .stNumberInput label, .stSelectbox label { color: #475569 !important; font-size: 13px !important; font-weight: 800 !important; text-transform: uppercase; margin-bottom: 8px !important; }
.main div[role="radiogroup"] { background-color: #FFFFFF !important; padding: 6px !important; border-radius: 12px !important; display: inline-flex !important; gap: 8px; margin-bottom: 10px; border: 1px solid #E2E8F0; box-shadow: 0 4px 15px rgba(0,0,0,0.03);}
.main div[role="radiogroup"] label { background-color: transparent !important; border: none !important; border-radius: 8px !important; padding: 12px 24px !important; cursor: pointer; transition: all 0.2s ease; }
.main div[role="radiogroup"] label:has(input:checked) { background-color: #F1F5F9 !important; border: 1px solid #CBD5E1 !important; box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;}
.main div[role="radiogroup"] div[role="radio"] { display: none !important; }
.main div[role="radiogroup"] label p { color: #64748B !important; font-size: 14px !important; font-weight: 700 !important; margin: 0 !important; }
.main div[role="radiogroup"] label:has(input:checked) p { color: #0F172A !important; font-weight: 900 !important; }
button[kind="primary"] { background: linear-gradient(135deg, #FF6501 0%, #E65A00 100%) !important; color: white !important; border: none !important; border-radius: 12px !important; padding: 1.4rem !important; font-size: 18px !important; font-weight: 900 !important; letter-spacing: 0.5px !important; box-shadow: 0 8px 20px -5px rgba(255, 101, 1, 0.4) !important; text-transform: uppercase; width: 100%; margin-top: 20px; transition: transform 0.2s; }
button[kind="primary"]:hover { transform: translateY(-3px); box-shadow: 0 15px 30px -5px rgba(255, 101, 1, 0.5) !important; }
div[data-testid="metric-container"] { background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 6px solid #FF6501; border-radius: 14px; padding: 25px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); margin-top: 15px; }
div[data-testid="metric-container"] label { color: #64748B !important; font-size: 14px !important; font-weight: 800 !important; text-transform: uppercase; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #0F172A !important; font-size: 36px !important; font-weight: 900 !important; }
.stTabs [data-baseweb="tab-list"] { gap: 20px; border-bottom: 2px solid #E2E8F0; margin-bottom: 25px; }
.stTabs [data-baseweb="tab"] { background-color: transparent; padding: 12px 20px; font-weight: 800; color: #64748B; border: none; font-size: 16px; }
.stTabs [aria-selected="true"] { color: #FF6501 !important; border-bottom: 4px solid #FF6501 !important; }
[data-testid="stDataFrame"] { border-radius: 12px !important; border: 1px solid #E2E8F0 !important; overflow: hidden !important; background: #FFFFFF; }
[data-testid="stWidgetLabel"] p { font-weight: 800 !important; color: #0F172A !important; font-size: 15px !important;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. NAVIGAZIONE INTERFACCIA
# ==========================================
st.sidebar.markdown("<div translate='no' class='notranslate sidebar-title'>JUNIOR CLUB TERNI</div>", unsafe_allow_html=True)
menu = st.sidebar.radio("Navigazione", ["📝 Emissione Ricevuta", "👥 Anagrafica Clienti", "📊 Storico Pagamenti"], label_visibility="collapsed")

if st.sidebar.button("🔄 Sincronizza Dati Cloud"):
    st.cache_data.clear()
    st.rerun()

if menu == "📝 Emissione Ricevuta":
    st.markdown("<div translate='no' class='titolo-app notranslate'>Emissione Ricevuta</div><div translate='no' class='sottotitolo notranslate'>Compilazione rapida e caricamento automatico.</div>", unsafe_allow_html=True)
elif menu == "👥 Anagrafica Clienti":
    st.markdown("<div translate='no' class='titolo-app notranslate'>Anagrafica Soci</div><div translate='no' class='sottotitolo notranslate'>Gestione centralizzata atleti e clienti</div>", unsafe_allow_html=True)
else:
    st.markdown("<div translate='no' class='titolo-app notranslate'>Storico Pagamenti</div><div translate='no' class='sottotitolo notranslate'>Reportistica e riepilogo incassi</div>", unsafe_allow_html=True)

# ==========================================
# FUNZIONI DI GESTIONE E DATABASE
# ==========================================
@st.cache_data(ttl=3600, show_spinner="Sincronizzazione dal Cloud in corso... ⚡")
def carica_fogli_google():
    df_s = pd.DataFrame()
    df_h = pd.DataFrame()
    try:
        gc = gspread.service_account(filename='credentials.json')
        sh = gc.open("Database_Junior_Club")
        
        ws_soci = sh.worksheet("soci")
        d_s = ws_soci.get_all_values()
        if len(d_s) > 1:
            df_s = pd.DataFrame(d_s[1:], columns=[str(c).strip().upper() for c in d_s[0]])
            df_s = df_s.loc[:, ~df_s.columns.duplicated()]
            df_s = df_s.loc[:, df_s.columns != '']
            
        ws_storico = sh.worksheet("storico")
        d_h = ws_storico.get_all_values()
        if len(d_h) > 1:
            df_h = pd.DataFrame(d_h[1:], columns=[str(c).strip().upper() for c in d_h[0]])
            df_h = df_h.loc[:, ~df_h.columns.duplicated()]
            df_h = df_h.loc[:, df_h.columns != '']
            
        return df_s, df_h
    except Exception as e:
        st.error(f"⚠️ Errore di connessione a Google Fogli: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_soci_cloud, df_storico_cloud = carica_fogli_google()

def get_prossimo_numero_cloud(tipo, df_h):
    if df_h.empty or 'NUMERO' not in df_h.columns: return 1
    df_f = df_h[df_h['TIPO'] == tipo]
    if df_f.empty: return 1
    massimo = pd.to_numeric(df_f['NUMERO'], errors='coerce').max()
    return int(massimo) + 1 if pd.notna(massimo) else 1

def carica_su_drive_e_invia_email(pdf_bytes, nome_file, email_destinazione=""):
    try:
        b64_data = base64.b64encode(pdf_bytes).decode('utf-8')
        payload = {"fileName": nome_file, "fileData": b64_data, "email": email_destinazione}
        response = requests.post(URL_WEB_APP, data=payload)
        return response.text
    except: return "Errore Bridge"

def estrai_id_drive(url):
    url_str = str(url)
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url_str)
    if match: return match.group(1)
    match = re.search(r'id=([a-zA-Z0-9_-]+)', url_str)
    if match: return match.group(1)
    return None

# ==========================================
# FUNZIONI CREAZIONE PDF
# ==========================================
def crea_pdf_pos(num_ric_str, data_ric, importo, chi_paga, cf_pagante, importo_lettere, causale, nome_allievo, nascita_allievo, indirizzo_allievo, testo_firma):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page(); pdf.rect(10, 10, 190, 140)
    pdf.set_xy(15, 15); pdf.set_font("Arial", 'B', 12); pdf.cell(90, 6, "JUNIOR CLUB TERNI S.S.D. A R.L.", ln=1)
    pdf.set_x(15); pdf.set_font("Arial", '', 10); pdf.cell(90, 5, "Via Arturo Toscanini n.49 - 05100 Terni (TR) ITA", ln=1)
    pdf.set_x(15); pdf.cell(90, 5, "C.F.: 01550520553", ln=1)
    pdf.set_xy(120, 15); pdf.set_font("Arial", 'B', 16); pdf.cell(40, 8, "RICEVUTA n.")
    pdf.set_font("Courier", 'B', 16); pdf.cell(30, 8, num_ric_str, border='B', align='C')
    pdf.set_xy(125, 30); pdf.set_font("Arial", 'B', 16); pdf.cell(15, 10, "Euro", align='R')
    pdf.set_font("Courier", 'B', 16); pdf.cell(50, 10, f"{importo:.2f}", border=1, align='C')
    pdf.set_xy(15, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 8, "RICEVIAMO")
    pdf.set_xy(15, 60); pdf.set_font("Arial", '', 10); pdf.cell(8, 6, "da")
    pdf.set_font("Courier", 'B', 11); pdf.cell(92, 6, chi_paga, border='B')
    pdf.set_font("Arial", '', 10); pdf.cell(35, 6, "(CODICE FISCALE)")
    pdf.set_font("Courier", 'B', 11); pdf.cell(40, 6, cf_pagante, border='B')
    pdf.set_xy(15, 70); pdf.set_font("Arial", '', 10); pdf.cell(32, 6, "la somma di Euro")
    pdf.set_font("Courier", 'B', 11); pdf.cell(93, 6, importo_lettere, border=1)
    pdf.set_font("Arial", '', 10); pdf.cell(25, 6, "(IN LETTERE)")
    pdf.set_xy(15, 80); pdf.set_font("Arial", '', 10); pdf.cell(38, 6, "per l'attivita' sportiva")
    pdf.set_font("Courier", 'B', 11); pdf.cell(137, 6, causale, border='B')
    pdf.rect(15, 95, 175, 35)
    pdf.set_xy(15, 95); pdf.set_font("Arial", '', 9); pdf.cell(40, 11, " COGNOME E NOME", border='B')
    pdf.set_font("Courier", 'B', 11); pdf.cell(135, 11, nome_allievo, border='B', align='R')
    pdf.set_xy(15, 106); pdf.set_font("Arial", '', 9); pdf.cell(40, 11, " LUOGO/DATA NASCITA", border='B')
    pdf.set_font("Courier", 'B', 11); pdf.cell(135, 11, nascita_allievo, border='B', align='R')
    pdf.set_xy(15, 117); pdf.set_font("Arial", '', 9); pdf.cell(40, 11, " INDIRIZZO")
    pdf.set_font("Courier", 'B', 11); pdf.cell(135, 11, indirizzo_allievo, align='R')
    pdf.set_xy(15, 135); pdf.set_font("Arial", 'B', 10); pdf.cell(12, 6, "Data")
    pdf.set_font("Courier", 'B', 10); pdf.cell(40, 6, data_ric, border='B')
    pdf.set_xy(120, 131); pdf.set_font("Arial", '', 10); pdf.cell(70, 6, "Firma dell'incaricato", align='C')
    pdf.set_xy(120, 137); pdf.set_font("Courier", 'B', 10); pdf.cell(70, 6, testo_firma, border='T', align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

def crea_pdf_contanti(num_ric_str, data_ric, importo, chi_paga, importo_lettere, causale, testo_firma):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page(); pdf.rect(10, 10, 190, 100)
    pdf.set_xy(15, 15); pdf.set_font("Arial", 'B', 12); pdf.cell(90, 6, "JUNIOR CLUB TERNI S.S.D. A R.L.", ln=1)
    pdf.set_x(15); pdf.set_font("Arial", '', 10); pdf.cell(90, 5, "Via Arturo Toscanini n.49 - 05100 Terni (TR) ITA", ln=1)
    pdf.set_x(15); pdf.cell(90, 5, "C.F.: 01550520553", ln=1)
    pdf.set_xy(120, 15); pdf.set_font("Arial", 'B', 16); pdf.cell(40, 8, "RICEVUTA n.", align='R')
    pdf.set_font("Courier", 'B', 16); pdf.cell(30, 8, num_ric_str, border='B', align='C')
    pdf.set_xy(120, 25); pdf.set_font("Arial", '', 12); pdf.cell(40, 8, "data", align='R')
    pdf.set_font("Courier", 'B', 12); pdf.cell(30, 8, data_ric, border='B', align='C')
    pdf.set_xy(15, 45); pdf.set_font("Arial", '', 12); pdf.cell(25, 8, "Ricevuti da")
    pdf.set_font("Courier", 'B', 14); pdf.cell(150, 8, chi_paga, border='B')
    pdf.set_xy(15, 60); pdf.set_font("Arial", 'B', 16); pdf.cell(15, 12, "Euro") 
    pdf.rect(30, 60, 160, 12, style='D'); pdf.set_xy(30, 60); pdf.set_fill_color(240, 244, 248); pdf.rect(30, 60, 160, 12, style='FD')
    pdf.set_font("Courier", 'B', 14); pdf.cell(160, 12, f"  {importo_lettere}", align='L')
    pdf.set_xy(15, 80); pdf.set_font("Arial", '', 12); pdf.cell(10, 8, "Per")
    pdf.set_font("Courier", 'B', 12); pdf.cell(175, 8, causale, border='B')
    pdf.set_xy(15, 95); pdf.set_font("Arial", 'B', 14); pdf.cell(35, 10, "TOTALE Euro")
    pdf.set_fill_color(240, 244, 248); pdf.rect(50, 95, 40, 10, style='FD'); pdf.set_xy(50, 95)
    pdf.set_font("Courier", 'B', 14); pdf.cell(40, 10, f"{importo:.2f}", align='C')
    pdf.set_xy(125, 95); pdf.set_font("Arial", '', 10); pdf.cell(65, 5, "Firma", align='C')
    pdf.set_xy(125, 105); pdf.set_font("Courier", 'B', 10); pdf.cell(65, 5, testo_firma, border='T', align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

def mostra_anteprima_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    # Usiamo object invece di iframe, è molto più tollerato dai browser
    pdf_display = f'''
        <object data="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="600px" style="border: 2px solid #E2E8F0; border-radius: 12px; margin-top: 15px;">
            <div style="padding: 30px; text-align: center; background: #F8FAFC; border-radius: 8px;">
                <p style="color: #64748B; font-weight: 600;">Il tuo browser blocca l'anteprima diretta dei PDF per motivi di sicurezza.</p>
                <p style="color: #0F172A; font-weight: 800;">Nessun problema: usa il pulsante arancione qui sotto per scaricarlo e stamparlo!</p>
            </div>
        </object>
    '''
    st.markdown("### 📄 Ricevuta Generata")
    st.markdown(pdf_display, unsafe_allow_html=True)

# ------------------------------------------
# SEZIONE 1: EMISSIONE RICEVUTA
# ------------------------------------------
if menu == "📝 Emissione Ricevuta":
    tipo_r = st.radio("Seleziona Modello", ["💳 RICEVUTA SPORTIVA (POS)", "💵 RICEVUTA GENERICA (CONTANTI)"], horizontal=True, label_visibility="collapsed")
    tipo_key = "POS" if "POS" in tipo_r else "CONTANTI"
    
    nomi_allievi = ["-- NUOVO (COMPILAZIONE MANUALE) --"]
    if not df_soci_cloud.empty:
        for _, row in df_soci_cloud.iterrows():
            n_atl = str(row.get('NOME', '')).strip()
            n_gen = str(row.get('GENITORE', '')).strip()
            if n_atl and n_atl.lower() != 'nan': nomi_allievi.append(n_atl)
            elif n_gen and n_gen.lower() != 'nan': nomi_allievi.append(n_gen)
    
    st.markdown("<div translate='no' class='notranslate' style='margin-bottom: 5px; margin-top: 5px;'><span style='font-size: 13px; font-weight: 800; color: #475569; text-transform: uppercase;'>🔍 Ricerca Rapida in Archivio</span></div>", unsafe_allow_html=True)
    scelta = st.selectbox("", nomi_allievi, label_visibility="collapsed")
    
    d_atl, d_nas, d_ind, d_gen, d_cf, d_ema = "", "", "", "", "", ""
    if scelta != "-- NUOVO (COMPILAZIONE MANUALE) --":
        try:
            match = df_soci_cloud[(df_soci_cloud['NOME'] == scelta) | (df_soci_cloud['GENITORE'] == scelta)]
            if not match.empty:
                row = match.iloc[0]
                d_atl = str(row.get('NOME', '')).replace('nan', '')
                d_nas = str(row.get('NASCITA', '')).replace('nan', '')
                d_ind = str(row.get('INDIRIZZO', '')).replace('nan', '')
                d_gen = str(row.get('GENITORE', '')).replace('nan', '')
                d_cf = str(row.get('CF', '')).replace('nan', '')
                d_ema = str(row.get('EMAIL', '')).replace('nan', '')
        except: pass

    with st.container(border=True):
        st.markdown("<div class='section-header'><i>💶</i> Dettagli Economici</div>", unsafe_allow_html=True)
        num_previsto = get_prossimo_numero_cloud(tipo_key, df_storico_cloud)
        c1, c2, c3 = st.columns([1, 1.5, 1.5]) 
        n_ric = c1.number_input("N. Ricevuta", value=num_previsto, min_value=1)
        dt = c2.text_input("Data Emissione", datetime.now().strftime('%d/%m/%Y'))
        val = c3.number_input("Importo Cifre (€)", value=50.0, step=5.0)
        
        parte_intera = int(val) if val else 0
        parte_dec = int(round((val - parte_intera) * 100)) if val else 0
        testo_lettere_auto = f"{num2words(parte_intera, lang='it').upper()}/{parte_dec:02d}"
        
        c4, c5 = st.columns([1.5, 1])
        importo_lettere = c4.text_input("Importo in Lettere", value=testo_lettere_auto)
        cau = c5.text_input("Causale", value="Scuola tennis" if tipo_key=="POS" else "")

        st.markdown("<div class='section-header'><i>👤</i> Dati Intestatario (Pagante)</div>", unsafe_allow_html=True)
        c_p1, c_p2 = st.columns(2)
        pag = c_p1.text_input("Nome e Cognome Pagante", value=d_gen if d_gen else d_atl)
        cf_p = c_p2.text_input("Codice Fiscale", value=d_cf)
        
        if tipo_key == "POS":
            st.markdown("<div class='section-header'><i>🏃</i> Dati Atleta</div>", unsafe_allow_html=True)
            ca1, ca2, ca3 = st.columns(3)
            atl_n = ca1.text_input("Nome Atleta", value=d_atl)
            atl_na = ca2.text_input("Luogo e Data Nascita", value=d_nas)
            atl_in = ca3.text_input("Indirizzo Residenza", value=d_ind)
        else:
            atl_n, atl_na, atl_in = "N/A", "N/A", "N/A"
            
        st.markdown("<div class='section-header'><i>📧</i> Finalizzazione e Invio</div>", unsafe_allow_html=True)
        c_em, c_fi = st.columns([2,1])
        email_invio = c_em.text_input("Email Cliente (Se inserita il PDF verrà spedito)", value=d_ema)
        firm = c_fi.selectbox("Firma Autorizzata", ["Sara Cesaroni", "Elisa Tradardi", "Valerio Cesaroni", "Federico Sciaboletta", "Eleonora Bartoli"])
        
        conferma_forzatura = True
        if n_ric != num_previsto:
            st.markdown(f"<div style='background-color: #F8FAFC; border: 1px solid #CBD5E1; border-left: 4px solid #FF6501; padding: 12px 16px; border-radius: 8px; margin-bottom: 12px; margin-top: 15px;'>Modifica Progressivo Rilevata (da {num_previsto} a {n_ric}). Attiva l'interruttore per procedere.</div>", unsafe_allow_html=True)
            conferma_forzatura = st.toggle(f"Sì, autorizzo il salvataggio con il n. {n_ric}")

        submit = st.button("✨ Genera Ricevuta e Salva in Cloud", type="primary", use_container_width=True)
        
    if submit:
        if not conferma_forzatura: st.error("👆 Attiva l'interruttore per procedere.")
        else:
            with st.spinner("Elaborazione, Invio Email e Backup su Drive in corso..."):
                if tipo_key == "POS": pdf_b = crea_pdf_pos(f"{n_ric:02d}", dt, val, pag, cf_p, importo_lettere, cau, atl_n, atl_na, atl_in, firm)
                else: pdf_b = crea_pdf_contanti(f"{n_ric:02d}", dt, val, pag, importo_lettere, cau, firm)
                
                f_name = f"{tipo_key}_{dt.replace('/','-')}_n{n_ric:02d}_{pag.replace(' ','_')}.pdf"
                link_d = carica_su_drive_e_invia_email(pdf_b, f_name, email_invio)
                
                try:
                    gc = gspread.service_account(filename='credentials.json')
                    sh = gc.open("Database_Junior_Club")
                    sh.worksheet("storico").append_row([dt, str(n_ric), tipo_key, str(val), pag.upper(), cf_p.upper(), cau.upper(), atl_n.upper(), atl_na.upper(), atl_in.upper(), firm, email_invio, link_d])
                    st.success("Operazione completata con successo! Ricevuta salvata.")
                    st.cache_data.clear() 
                    
                    mostra_anteprima_pdf(pdf_b)
                    st.download_button(
                        label="⬇️ Scarica Copia PDF",
                        data=pdf_b,
                        file_name=f_name,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e: st.error(f"Errore Google Sheets: {e}")

# ------------------------------------------
# SEZIONE 2: ANAGRAFICA 
# ------------------------------------------
elif menu == "👥 Anagrafica Clienti":
    tab1, tab2 = st.tabs(["Aggiungi Nuovo", "Elenco Completo"])
    with tab1:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            n = c1.text_input("Nome Atleta")
            nas = c2.text_input("Luogo/Data di Nascita")
            ind = st.text_input("Indirizzo di Residenza")
            gen = c1.text_input("Genitore (Pagante)")
            cf = c2.text_input("Codice Fiscale")
            ema = st.text_input("Email")
            if st.button("Registra in Anagrafica", type="primary"):
                try:
                    gc = gspread.service_account(filename='credentials.json')
                    sh = gc.open("Database_Junior_Club")
                    sh.worksheet("soci").append_row([n.upper(), nas.upper(), ind.upper(), gen.upper(), cf.upper(), ema.lower()])
                    st.success("Socio aggiunto correttamente!")
                    st.cache_data.clear()
                except Exception as e: st.error(f"Errore: {e}")
    with tab2:
        st.dataframe(df_soci_cloud, use_container_width=True, height=550) if not df_soci_cloud.empty else st.info("Archivio vuoto.")

# ------------------------------------------
# SEZIONE 3: STORICO E CANCELLAZIONE
# ------------------------------------------
else:
    if not df_storico_cloud.empty:
        df_storico_cloud['IMPORTO_NUM'] = pd.to_numeric(df_storico_cloud.get('IMPORTO', '0').astype(str).str.replace(',', '.'), errors='coerce')
        c1, c2, c3 = st.columns(3)
        c1.metric("FATTURATO", f"€ {df_storico_cloud['IMPORTO_NUM'].sum():,.2f}")
        c2.metric("POS", f"€ {df_storico_cloud[df_storico_cloud['TIPO'] == 'POS']['IMPORTO_NUM'].sum():,.2f}")
        c3.metric("CONTANTI", f"€ {df_storico_cloud[df_storico_cloud['TIPO'] == 'CONTANTI']['IMPORTO_NUM'].sum():,.2f}")
        
        st.dataframe(df_storico_cloud.drop(columns=['IMPORTO_NUM'], errors='ignore'), use_container_width=True, height=450)
        
        st.markdown("---")
        st.markdown("<div class='section-header' style='border-left-color: #DC2626; color: #DC2626;'><i>🗑️</i> ZONA PERICOLO: ELIMINA RICEVUTA</div>", unsafe_allow_html=True)
        
        lista_ric = ["-- Seleziona la ricevuta da cancellare --"]
        for idx, row in df_storico_cloud.iterrows():
            lista_ric.append(f"Riga Excel {idx+2}: Data {row.get('DATA','')} - Ricevuta N.{row.get('NUMERO','')} - {row.get('INTESTATARIO','')}")
            
        da_eliminare = st.selectbox("Seleziona", lista_ric, label_visibility="collapsed")
        
        if da_eliminare != "-- Seleziona la ricevuta da cancellare --":
            if st.button("🚨 CONFERMO: ELIMINA DEFINITIVAMENTE", type="primary"):
                riga_excel = int(da_eliminare.split(":")[0].replace("Riga Excel ", ""))
                riga_df = riga_excel - 2
                
                with st.spinner("Polverizzazione in corso (Sheets + Drive)..."):
                    try:
                        # CERCA IL LINK DRIVE IN MODO INTELLIGENTE IN TUTTA LA RIGA
                        riga_valori = df_storico_cloud.iloc[riga_df].values
                        link_drive = None
                        for val in riga_valori:
                            if "drive.google.com" in str(val):
                                link_drive = str(val)
                                break
                        
                        if link_drive:
                            file_id = estrai_id_drive(link_drive)
                            if file_id:
                                requests.post(URL_WEB_APP, data={"action": "delete", "fileId": file_id})
                        
                        # Elimina da Excel
                        gc = gspread.service_account(filename='credentials.json')
                        sh = gc.open("Database_Junior_Club")
                        sh.worksheet("storico").delete_rows(riga_excel)
                        
                        st.success("Ricevuta eliminata per sempre da Excel e da Drive!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Errore durante l'eliminazione: {e}")
    else:
        st.info("Nessuna ricevuta trovata.")
