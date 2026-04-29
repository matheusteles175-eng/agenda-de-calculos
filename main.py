import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# --- 1. CONFIGURAÇÃO E ESTILO (LIMPEZA TOTAL E DESTAQUES) ---
st.set_page_config(
    page_title="CheckPoint Shift 🏁", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

st.markdown("""
<style>
    /* FUNDO DO APP */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url("https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* SETINHA DO MENU - VERDE E VISÍVEL */
    button[kind="headerNoContext"] {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 999999 !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.7) !important;
        border: 2px solid white !important;
    }
    button[kind="headerNoContext"] svg { fill: white !important; width: 35px !important; height: 35px !important; }

    /* REMOÇÃO DE PANOS BRANCOS */
    input, [data-baseweb="input"], .stNumberInput div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: none !important;
    }
    
    /* CARDS DE META (DÉFICIT E SUCESSO) */
    .card-meta {
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        border: 3px solid;
    }
    .meta-sucesso { background-color: rgba(0, 255, 127, 0.15); border-color: #00FF7F; color: #00FF7F; }
    .meta-falta { background-color: rgba(255, 75, 75, 0.15); border-color: #FF4B4B; color: #FF4B4B; }

    /* TEXTOS E BOTÕES */
    html, body, [class*="st-"], div, p, label { font-size: 20px !important; color: white !important; }
    .stButton>button {
        width: 100%; border-radius: 12px; font-weight: bold; font-size: 22px !important; height: 3.5em;
        background-color: rgba(255, 255, 255, 0.1) !important; color: white !important; border: 1px solid rgba(255, 255, 255, 0.4) !important;
    }
    .stButton>button:hover { background-color: #28a745 !important; border: none !important; }
</style>
""", unsafe_allow_html=True)

def conectar():
    conn = sqlite3.connect("checkpoint_shift_vfinal.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT PRIMARY KEY, senha TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS veiculo (usuario TEXT PRIMARY KEY, fipe REAL, guardado_ipva REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS ganhos (id INTEGER PRIMARY KEY, usuario TEXT, data TEXT, ganho REAL, gasto REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS metas (id INTEGER PRIMARY KEY, usuario TEXT, item TEXT, valor REAL, guardado REAL)")
    conn.commit()
    return conn, cursor

conn, cursor = conectar()

# --- LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🏁 CheckPoint Shift</h1>", unsafe_allow_html=True)
    tab_l, tab_c = st.tabs(["🔑 ENTRAR", "📝 CADASTRAR"])
    with tab_l:
        u = st.text_input("Usuário").lower().strip()
        s = st.text_input("Senha", type="password")
        if st.button("ACESSAR"):
            if cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (u, s)).fetchone():
                st.session_state.autenticado, st.session_state.user = True, u
                st.rerun()
    with tab_c:
        nu = st.text_input("Novo Usuário").lower()
        ns = st.text_input("Nova Senha", type="password")
        if st.button("CRIAR CONTA"):
            try:
                cursor.execute("INSERT INTO usuarios VALUES (?,?)", (nu, ns))
                conn.commit(); st.success("Pronto! Faça login.")
            except: st.error("Erro no cadastro.")
    st.stop()

user = st.session_state.user
hoje = date.today()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>👤</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{user.upper()}</h3>", unsafe_allow_html=True)
    if st.button("🚪 SAIR"):
        st.session_state.autenticado = False
        st.rerun()

# --- PAINEL ---
t1, t2, t3 = st.tabs(["📊 IPVA", "💰 GANHOS & METAS", "🎯 CAIXINHAS"])

with t2:
    col_meta1, col_meta2 = st.columns([2, 1])
    meta_diaria = col_meta1.number_input("Sua Meta Diária de Lucro (R$):", value=400.0)
    
    with st.form("ganho_diario", clear_on_submit=True):
        st.subheader("Registrar Trabalho de Hoje")
        g1, g2 = st.columns(2)
        v_bruto = g1.number_input("Ganhos Brutos")
        v_gastos = g2.number_input("Gastos")
        if st.form_submit_button("💾 SALVAR DIA"):
            cursor.execute("INSERT INTO ganhos (usuario, data, ganho, gasto) VALUES (?,?,?,?)", (user, str(hoje), v_bruto, v_gastos))
            conn.commit(); st.rerun()

    # Lógica de Meta e Déficit
    lucro_hoje = v_bruto - v_gastos
    
    if lucro_hoje >= meta_diaria:
        passou = lucro_hoje - meta_diaria
        st.markdown(f"""
            <div class="card-meta meta-sucesso">
                <h1>META BATIDA! 🚀</h1>
                <p style="font-size: 50px; font-weight: bold;">R$ {lucro_hoje:.2f}</p>
                <p>Parabéns! Você ultrapassou <b>R$ {passou:.2f}</b> da sua meta de R$ {meta_diaria:.2f}!</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        deficit = meta_diaria - lucro_hoje
        st.markdown(f"""
            <div class="card-meta meta-falta">
                <h1>META EM DÉFICIT ⚠️</h1>
                <p style="font-size: 50px; font-weight: bold;">R$ {lucro_hoje:.2f}</p>
                <p>Você está em déficit de <b>R$ {deficit:.2f}</b> para atingir a meta.</p>
            </div>
        """, unsafe_allow_html=True)

    # Histórico
    st.subheader("📜 Últimos Dias")
    df = pd.read_sql_query(f"SELECT * FROM ganhos WHERE usuario='{user}' ORDER BY id DESC LIMIT 5", conn)
    for i, r in df.iterrows():
        with st.container():
            lucro_item = r['ganho'] - r['gasto']
            cor = "#00FF7F" if lucro_item >= meta_diaria else "#FF4B4B"
            st.markdown(f"📅 {r['data']} | Lucro: <b style='color:{cor}'>R$ {lucro_item:.2f}</b>", unsafe_allow_html=True)

# (As outras abas IPVA e Caixinhas permanecem com sua lógica normal de depósito/saque)
