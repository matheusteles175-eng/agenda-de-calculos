import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# --- 1. CONFIGURAÇÃO E ESTILO (SOLUÇÃO DEFINITIVA) ---
st.set_page_config(
    page_title="CheckPoint Shift 🏁", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

st.markdown("""
<style>
    /* FUNDO DO APP */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.9)), 
                    url("https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
    }
    
    /* A SETINHA (BOTÃO DA SIDEBAR) - PRETA E DESTAQUE */
    button[kind="headerNoContext"] {
        background-color: #000000 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        width: 55px !important;
        height: 55px !important;
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 999999 !important;
        border: 2px solid #28a745 !important;
    }

    /* MATANDO O PANO BRANCO/CINZA DOS CAMPOS DE DIGITAR */
    /* Agora o fundo onde digita é PRETO e a letra é BRANCA */
    input, [data-baseweb="input"], [data-testid="stNumberInput"] div {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #28a745 !important;
        font-size: 24px !important;
        font-weight: bold !important;
    }
    
    /* AJUSTE DOS BOTÕES DE + E - DO LADO DO NÚMERO */
    [data-testid="stNumberInput"] button {
        background-color: #28a745 !important;
        color: white !important;
    }

    /* TEXTOS DE TÍTULO E RÓTULOS */
    label, p, h1, h2, h3 {
        color: white !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }

    /* CARDS DE META (MAIORES) */
    .card-meta {
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        border: 5px solid;
    }
    .meta-sucesso { background-color: #004d26; border-color: #00FF7F; color: #00FF7F; }
    .meta-falta { background-color: #4d0000; border-color: #FF4B4B; color: #FF4B4B; }

    /* BOTÃO SALVAR / ENTRAR */
    .stButton>button {
        width: 100%; border-radius: 12px; font-weight: 900; 
        font-size: 24px !important; height: 3.5em;
        background-color: #28a745 !important; color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS (USANDO O SEU ORIGINAL) ---
def conectar():
    conn = sqlite3.connect("checkpoint_shift_mateus.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT PRIMARY KEY, senha TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS veiculo (usuario TEXT PRIMARY KEY, km_ini REAL, km_alvo REAL, custo REAL, fipe REAL, guardado_ipva REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS metas (id INTEGER PRIMARY KEY, usuario TEXT, item TEXT, valor REAL, data TEXT, guardado REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS ganhos (id INTEGER PRIMARY KEY, usuario TEXT, data TEXT, ganho REAL, gasto REAL, km REAL, h_ini TEXT, h_fim TEXT)")
    conn.commit()
    return conn, cursor

conn, cursor = conectar()

# --- 3. LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🏁 CHECKPOINT SHIFT</h1>", unsafe_allow_html=True)
    t_login, t_cad = st.tabs(["🔑 ENTRAR", "📝 CADASTRAR"])
    with t_login:
        u = st.text_input("USUÁRIO").lower().strip()
        s = st.text_input("SENHA", type="password")
        if st.button("ACESSAR PAINEL"):
            if cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (u, s)).fetchone():
                st.session_state.autenticado, st.session_state.user = True, u
                st.rerun()
    with t_cad:
        nu = st.text_input("NOVO USUÁRIO").lower()
        ns = st.text_input("SENHA ", type="password")
        if st.button("CRIAR CONTA"):
            try:
                cursor.execute("INSERT INTO usuarios VALUES (?,?)", (nu, ns))
                conn.commit(); st.success("CONTA CRIADA!")
            except: st.error("ERRO: USUÁRIO JÁ EXISTE.")
    st.stop()

# --- 4. PAINEL PRINCIPAL ---
user = st.session_state.user
hoje = date.today()

with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>👤</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{user.upper()}</h3>", unsafe_allow_html=True)
    if st.button("SAIR DO SISTEMA"):
        st.session_state.autenticado = False
        st.rerun()

# VEÍCULO
v_data = cursor.execute("SELECT * FROM veiculo WHERE usuario=?", (user,)).fetchone()
if not v_data:
    st.header("⚙️ CONFIGURAÇÃO DO CARRO")
    with st.form("cfg_carro"):
        f = st.number_input("VALOR FIPE DO CARRO", value=45000.0)
        k = st.number_input("KM ATUAL DO VEÍCULO", value=100000.0)
        if st.form_submit_button("SALVAR CONFIGURAÇÃO"):
            cursor.execute("INSERT INTO veiculo VALUES (?,?,?,?,?,?)", (user, k, k+10000, 350.0, f, 0.0))
            conn.commit(); st.rerun()
    st.stop()

tab1, tab2, tab3 = st.tabs(["📊 IPVA", "💰 GANHOS", "🎯 CAIXINHAS"])

with tab2:
    meta_val = st.number_input("META DIÁRIA (R$)", value=400.0)
    with st.form("add_ganho"):
        col1, col2 = st.columns(2)
        b = col1.number_input("GANHO BRUTO (R$)")
        g = col2.number_input("GASTOS (R$)")
        if st.form_submit_button("REGISTRAR DIA"):
            cursor.execute("INSERT INTO ganhos (usuario, data, ganho, gasto, km, h_ini, h_fim) VALUES (?,?,?,?,?,?,?)", (user, str(hoje), b, g, 0, "0", "0"))
            conn.commit(); st.rerun()
            
    lucro = b - g
    if b > 0:
        if lucro >= meta_val:
            passou = lucro - meta_val
            st.markdown(f'<div class="card-meta meta-sucesso"><h1>META BATIDA! 🚀</h1><p style="font-size: 40px;">R$ {lucro:.2f}</p><p>PARABÉNS! VOCÊ ULTRAPASSOU <b>R$ {passou:.2f}</b> DA META!</p></div>', unsafe_allow_html=True)
        else:
            deficit = meta_val - lucro
            st.markdown(f'<div class="card-meta meta-falta"><h1>DÉFICIT ⚠️</h1><p style="font-size: 40px;">R$ {lucro:.2f}</p><p>FALTAM <b>R$ {deficit:.2f}</b> PARA A META.</p></div>', unsafe_allow_html=True)
