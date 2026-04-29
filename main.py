import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# --- 1. CONFIGURAÇÃO E ESTILO ---
st.set_page_config(
    page_title="CheckPoint Shift 🏁", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

st.markdown("""
<style>
    /* FUNDO GERAL DO APP */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url("https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* SETINHA DA SIDEBAR (SUPER DESTAQUE) */
    button[kind="headerNoContext"] {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 50% !important;
        width: 65px !important;
        height: 65px !important;
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 999999 !important;
        border: 3px solid white !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.8) !important;
    }
    button[kind="headerNoContext"] svg { fill: white !important; width: 35px !important; height: 35px !important; }

    /* REMOVENDO PANOS BRANCOS DE TUDO */
    input, [data-baseweb="input"], .stNumberInput div, .stTextInput div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    
    /* NOMES DA ABA DE CONFIGURAÇÃO (PRETO NEGRITO) */
    .stForm label, .stForm p, .cfg-label {
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 22px !important;
        text-shadow: none !important;
    }
    
    /* FUNDO DA ABA DE CONFIGURAÇÃO (PARA DAR CONTRASTE COM O PRETO) */
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.8) !important; /* Fundo claro para o texto preto aparecer */
        border-radius: 20px;
    }

    /* CARDS DE META */
    .card-meta {
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        border: 4px solid;
    }
    .meta-sucesso { background-color: rgba(0, 255, 127, 0.2); border-color: #00FF7F; color: #00FF7F; }
    .meta-falta { background-color: rgba(255, 75, 75, 0.2); border-color: #FF4B4B; color: #FF4B4B; }

    /* FONTES GERAIS */
    html, body, [class*="st-"], div, p, label { font-size: 20px !important; color: white; }
    
    .stButton>button {
        width: 100%; border-radius: 12px; font-weight: bold; font-size: 22px !important; height: 3.5em;
        background-color: rgba(255, 255, 255, 0.15) !important; color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS ---
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
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🏁 CheckPoint Shift")
    t_login, t_cad = st.tabs(["🔑 ENTRAR", "📝 CADASTRAR"])
    with t_login:
        u = st.text_input("Usuário").lower().strip()
        s = st.text_input("Senha", type="password")
        if st.button("LOGAR NO PAINEL"):
            check = cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (u, s)).fetchone()
            if check:
                st.session_state.autenticado = True
                st.session_state.user = u
                st.rerun()
            else: st.error("Dados incorretos.")
    with t_cad:
        nu = st.text_input("Novo Usuário").lower()
        ns = st.text_input("Senha", type="password")
        if st.button("CADASTRAR"):
            try:
                cursor.execute("INSERT INTO usuarios VALUES (?,?)", (nu, ns))
                conn.commit(); st.success("Conta criada!")
            except: st.error("Erro ou usuário já existe.")
    st.stop()

# --- 4. PAINEL ---
user = st.session_state.user
hoje = date.today()

with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>👤</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>PERFIL: {user.upper()}</h3>", unsafe_allow_html=True)
    if st.button("SAIR DO APP"):
        st.session_state.autenticado = False
        st.rerun()

# Pegar dados do veículo ou configurar
v_data = cursor.execute("SELECT * FROM veiculo WHERE usuario=?", (user,)).fetchone()
if not v_data:
    st.header("⚙️ CONFIGURAÇÃO DO CARRO")
    with st.form("car"):
        st.markdown("<p class='cfg-label'>VALOR FIPE DO CARRO</p>", unsafe_allow_html=True)
        f = st.number_input("fipe_input", label_visibility="collapsed", value=45000.0)
        st.markdown("<p class='cfg-label'>KM ATUAL DO VEÍCULO</p>", unsafe_allow_html=True)
        k = st.number_input("km_input", label_visibility="collapsed", value=100000.0)
        if st.form_submit_button("SALVAR CONFIGURAÇÃO"):
            cursor.execute("INSERT INTO veiculo VALUES (?,?,?,?,?,?)", (user, k, k+10000, 350.0, f, 0.0))
            conn.commit(); st.rerun()
    st.stop()

tab1, tab2, tab3 = st.tabs(["📊 IPVA", "💰 GANHOS & METAS", "🎯 CAIXINHAS"])

with tab2:
    meta_diaria = st.number_input("Qual sua meta de hoje? (R$)", value=400.0)
    with st.form("registro_dia"):
        st.markdown("<p style='color:black; font-weight:bold;'>Ganhos Brutos (R$)</p>", unsafe_allow_html=True)
        b = st.number_input("b", label_visibility="collapsed")
        st.markdown("<p style='color:black; font-weight:bold;'>Total de Gastos (R$)</p>", unsafe_allow_html=True)
        g = st.number_input("g", label_visibility="collapsed")
        if st.form_submit_button("SALVAR REGISTRO"):
            cursor.execute("INSERT INTO ganhos (usuario, data, ganho, gasto, km, h_ini, h_fim) VALUES (?,?,?,?,?,?,?)", (user, str(hoje), b, g, 0, "0", "0"))
            conn.commit(); st.rerun()
            
    lucro = b - g
    if b > 0:
        if lucro >= meta_diaria:
            passou = lucro - meta_diaria
            st.markdown(f'''
                <div class="card-meta meta-sucesso">
                    <h1>META BATIDA! 🚀</h1>
                    <p style="font-size: 40px; font-weight: bold;">R$ {lucro:.2f}</p>
                    <p>Parabéns! Você ultrapassou <b>R$ {passou:.2f}</b> da sua meta!</p>
                </div>
            ''', unsafe_allow_html=True)
        else:
            deficit = meta_diaria - lucro
            st.markdown(f'''
                <div class="card-meta meta-falta">
                    <h1>DÉFICIT ⚠️</h1>
                    <p style="font-size: 40px; font-weight: bold;">R$ {lucro:.2f}</p>
                    <p>Faltam <b>R$ {deficit:.2f}</b> para atingir a meta.</p>
                </div>
            ''', unsafe_allow_html=True)

with tab1:
    st.metric("Saldo IPVA", f"R$ {v_data[5]:.2f}")
    val_ipva = st.number_input("Valor Operação", key="ipva")
    if st.button("DEPOSITAR NO IPVA"):
        cursor.execute("UPDATE veiculo SET guardado_ipva = guardado_ipva + ? WHERE usuario=?", (val_ipva, user))
        conn.commit(); st.rerun()
