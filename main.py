import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# --- 1. CONFIGURAÇÃO E ESTILO (LIMPEZA E DESTAQUES) ---
st.set_page_config(
    page_title="CheckPoint Shift 🏁", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

st.markdown("""
<style>
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

    /* REMOÇÃO DE PANOS BRANCOS DOS INPUTS */
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

    html, body, [class*="st-"], div, p, label { font-size: 20px !important; color: white !important; }
    .stButton>button {
        width: 100%; border-radius: 12px; font-weight: bold; font-size: 22px !important; height: 3.5em;
        background-color: rgba(255, 255, 255, 0.1) !important; color: white !important; border: 1px solid rgba(255, 255, 255, 0.4) !important;
    }
    .stButton>button:hover { background-color: #28a745 !important; border: none !important; }
</style>
""", unsafe_allow_html=True)

def conectar():
    # VOLTEI PARA O NOME DO SEU BANCO ANTERIOR PARA O LOGIN FUNCIONAR
    conn = sqlite3.connect("checkpoint_shift_mateus.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT PRIMARY KEY, senha TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS veiculo (usuario TEXT PRIMARY KEY, km_ini REAL, km_alvo REAL, custo REAL, fipe REAL, guardado_ipva REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS metas (id INTEGER PRIMARY KEY, usuario TEXT, item TEXT, valor REAL, data TEXT, guardado REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS ganhos (id INTEGER PRIMARY KEY, usuario TEXT, data TEXT, ganho REAL, gasto REAL, km REAL, h_ini TEXT, h_fim TEXT)")
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
            # Verifica no banco de dados se o usuário existe
            user_db = cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (u, s)).fetchone()
            if user_db:
                st.session_state.autenticado, st.session_state.user = True, u
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos.")
    with tab_c:
        nu = st.text_input("Novo Usuário").lower()
        ns = st.text_input("Nova Senha", type="password")
        if st.button("CRIAR CONTA"):
            try:
                cursor.execute("INSERT INTO usuarios VALUES (?,?)", (nu, ns))
                conn.commit(); st.success("✅ Conta criada! Agora faça o login.")
            except: st.error("❌ Erro: Usuário já existe.")
    st.stop()

user = st.session_state.user
hoje = date.today()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>👤</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{user.upper()}</h3>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚗 RECONFIGURAR CARRO"):
        cursor.execute("DELETE FROM veiculo WHERE usuario=?", (user,))
        conn.commit(); st.rerun()
    if st.button("🚪 SAIR"):
        st.session_state.autenticado = False
        st.rerun()

# --- CARREGAR DADOS DO VEÍCULO ---
v_data = cursor.execute("SELECT * FROM veiculo WHERE usuario=?", (user,)).fetchone()
if v_data is None:
    st.header("⚙️ Configuração Inicial")
    with st.form("cfg"):
        f_val = st.number_input("Valor FIPE", value=45000.0)
        k_val = st.number_input("KM Atual", value=100000.0)
        if st.form_submit_button("SALVAR"):
            cursor.execute("INSERT INTO veiculo VALUES (?,?,?,?,?,?)", (user, k_val, k_val+10000, 350.0, f_val, 0.0))
            conn.commit(); st.rerun()
    st.stop()

# --- ABAS ---
t1, t2, t3 = st.tabs(["📊 IPVA", "💰 GANHOS & METAS", "🎯 CAIXINHAS"])

with t2:
    col_meta1, col_meta2 = st.columns([2, 1])
    meta_diaria = col_meta1.number_input("Sua Meta Diária de Lucro (R$):", value=400.0)
    
    with st.form("ganho_diario", clear_on_submit=True):
        st.subheader("Registrar Trabalho")
        g1, g2 = st.columns(2)
        v_bruto = g1.number_input("Ganhos Brutos")
        v_gastos = g2.number_input("Gastos")
        if st.form_submit_button("💾 SALVAR DIA"):
            cursor.execute("INSERT INTO ganhos (usuario, data, ganho, gasto, km, h_ini, h_fim) VALUES (?,?,?,?,?,?,?)", 
                           (user, str(hoje), v_bruto, v_gastos, 0, "08:00", "18:00"))
            conn.commit(); st.rerun()

    lucro_hoje = v_bruto - v_gastos
    if v_bruto > 0: # Só mostra o card se tiver lançado algo hoje
        if lucro_hoje >= meta_diaria:
            passou = lucro_hoje - meta_diaria
            st.markdown(f'<div class="card-meta meta-sucesso"><h1>META BATIDA! 🚀</h1><p style="font-size: 50px; font-weight: bold;">R$ {lucro_hoje:.2f}</p><p>Parabéns! Você ultrapassou <b>R$ {passou:.2f}</b> da meta!</p></div>', unsafe_allow_html=True)
        else:
            deficit = meta_diaria - lucro_hoje
            st.markdown(f'<div class="card-meta meta-falta"><h1>META EM DÉFICIT ⚠️</h1><p style="font-size: 50px; font-weight: bold;">R$ {lucro_hoje:.2f}</p><p>Faltam <b>R$ {deficit:.2f}</b> para a meta.</p></div>', unsafe_allow_html=True)

    st.subheader("📜 Histórico")
    df = pd.read_sql_query(f"SELECT * FROM ganhos WHERE usuario='{user}' ORDER BY id DESC LIMIT 5", conn)
    for i, r in df.iterrows():
        lucro_item = r['ganho'] - r['gasto']
        cor = "#00FF7F" if lucro_item >= meta_diaria else "#FF4B4B"
        st.markdown(f"📅 {r['data']} | Lucro: <b style='color:{cor}'>R$ {lucro_item:.2f}</b>", unsafe_allow_html=True)

with t1:
    fipe, guardado = v_data[4], v_data[5]
    total_ipva = fipe * 0.04
    st.metric("Total IPVA", f"R$ {total_ipva:.2f}")
    st.metric("Guardado", f"R$ {guardado:.2f}")
    v_ipva = st.number_input("Valor R$:", key="ipva_v", value=0.0)
    c1, c2 = st.columns(2)
    if c1.button("📥 DEPOSITAR IPVA"):
        cursor.execute("UPDATE veiculo SET guardado_ipva = guardado_ipva + ? WHERE usuario=?", (v_ipva, user))
        conn.commit(); st.rerun()
    if c2.button("📤 ESTORNAR IPVA"):
        cursor.execute("UPDATE veiculo SET guardado_ipva = guardado_ipva - ? WHERE usuario=?", (v_ipva, user))
        conn.commit(); st.rerun()

with t3:
    st.subheader("🎯 Caixinhas")
    with st.expander("➕ NOVA META"):
        with st.form("m_form"):
            it = st.text_input("Objetivo"); v = st.number_input("Valor")
            if st.form_submit_button("CRIAR"):
                cursor.execute("INSERT INTO metas (usuario, item, valor, data, guardado
