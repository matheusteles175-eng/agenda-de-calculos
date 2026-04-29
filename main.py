import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# --- 1. CONFIGURAÇÃO E ESTILO (CORREÇÃO DE CORES) ---
st.set_page_config(
    page_title="CheckPoint Shift 🏁", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

st.markdown("""
<style>
    /* FUNDO DO APLICATIVO */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url("https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* CONFIGURAÇÃO DA BARRA LATERAL (TEXTO PRETO PARA CONTRASTE) */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important; /* Um cinza bem clarinho quase branco */
    }
    
    /* Forçar tudo dentro da sidebar a ser PRETO */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* BOTÃO DA SETINHA LÁ EM CIMA (Destacado em Preto/Verde) */
    button[kind="headerNoContext"] {
        background-color: #28a745 !important;
        border-radius: 50% !important;
        width: 55px !important;
        height: 55px !important;
        top: 10px !important;
        left: 10px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important;
    }
    button[kind="headerNoContext"] svg {
        fill: white !important; /* Seta branca dentro do círculo verde */
    }

    /* BOTÕES DENTRO DA SIDEBAR (Texto Preto e Borda) */
    [data-testid="stSidebar"] .stButton>button {
        color: #000000 !important;
        border: 2px solid #000000 !important;
        background-color: transparent !important;
        font-size: 18px !important;
    }

    /* ESTILO DOS CARDS NO PAINEL PRINCIPAL */
    [data-testid="stForm"], .st-expander, .stMetric, div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px !important;
        padding: 25px;
    }
    
    h1, h2, h3, p, label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS ---
def conectar():
    conn = sqlite3.connect("checkpoint_shift_oficial.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT PRIMARY KEY, senha TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS veiculo (usuario TEXT PRIMARY KEY, km_ini REAL, fipe REAL, guardado_ipva REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS metas (id INTEGER PRIMARY KEY, usuario TEXT, item TEXT, valor REAL, guardado REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS ganhos (id INTEGER PRIMARY KEY, usuario TEXT, data TEXT, ganho REAL, gasto REAL, km REAL)")
    conn.commit()
    return conn, cursor

conn, cursor = conectar()

# --- 3. LOGIN E CADASTRO ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; font-size: 40px;'>🏁 CheckPoint Shift</h1>", unsafe_allow_html=True)
    aba_login, aba_cad = st.tabs(["🔑 ENTRAR", "📝 CADASTRAR"])
    
    with aba_login:
        u = st.text_input("Usuário").lower().strip()
        s = st.text_input("Senha", type="password")
        if st.button("ACESSAR"):
            if cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (u, s)).fetchone():
                st.session_state.autenticado, st.session_state.user = True, u
                st.rerun()
            else: st.error("Incorreto.")
            
    with aba_cad:
        nu = st.text_input("Novo Usuário").lower().strip()
        ns = st.text_input("Nova Senha", type="password")
        if st.button("CRIAR CONTA"):
            try:
                cursor.execute("INSERT INTO usuarios VALUES (?,?)", (nu, ns))
                conn.commit(); st.success("✅ Criada!")
            except: st.error("❌ Já existe.")
    st.stop()

user = st.session_state.user
hoje = date.today()

# --- 4. SIDEBAR (BONEQUINHO E CONFIGURAÇÕES) ---
with st.sidebar:
    # Bonequinho em azul para destacar no fundo branco
    st.markdown(f"<h1 style='text-align: center; font-size: 80px; color: #2e77d0 !important;'>👤</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>{user.upper()}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("🚗 RECONFIGURAR CARRO"):
        cursor.execute("DELETE FROM veiculo WHERE usuario=?", (user,))
        conn.commit(); st.rerun()

    if st
