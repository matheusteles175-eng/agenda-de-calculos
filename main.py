import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# --- 1. CONFIGURAÇÃO E ESTILO (LIMPEZA TOTAL DE "PANOS BRANCOS") ---
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
    
    /* DESTAQUE DA SETINHA (SIDEBAR) - VERDE VIBRANTE */
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
    button[kind="headerNoContext"] svg {
        fill: white !important;
        width: 35px !important;
        height: 35px !important;
    }

    /* REMOVENDO PANOS BRANCOS DE CAMPOS E BOTÕES */
    input, [data-baseweb="input"], [data-baseweb="base-input"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    /* TIRA O BRANCO AO CLICAR NOS CAMPOS */
    div[data-baseweb="input"] > div {
        background-color: transparent !important;
        color: white !important;
    }

    /* TEXTOS E INTERFACE GRANDES */
    html, body, [class*="st-"], div, p, label {
        font-size: 20px !important; 
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab"] { 
        font-size: 24px !important; 
        font-weight: bold; 
        color: white !important;
    }

    /* CARDS ESTILO VIDRO TRANSPARENTE */
    [data-testid="stForm"], .st-expander, .stMetric, div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px !important;
        padding: 25px;
    }

    /* BOTÕES GIGANTES E SEM FUNDO BRANCO */
    .stButton>button {
        width: 100%; border-radius: 12px; font-weight: bold; 
        font-size: 22px !important; height: 3.5em;
        background-color: rgba(255, 255, 255, 0.1) !important; 
        color: white !important; 
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
    }
    .stButton>button:hover { 
        background-color: #28a745 !important; 
        color: white !important; 
        border: none !important;
    }
    
    /* CORRIGE O FUNDO BRANCO DENTRO DOS FORMULÁRIOS */
    div[data-testid="stForm"] {
        background-color: rgba(0, 0, 0, 0.3) !important;
    }
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
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>🏁 CheckPoint Shift</h1>", unsafe_allow_html=True)
    aba_login, aba_cad = st.tabs(["🔑 ENTRAR", "📝 CADASTRAR"])
    
    with aba_login:
        u = st.text_input("Usuário").lower().strip()
        s = st.text_input("Senha", type="password")
        if st.button("ACESSAR SISTEMA"):
            if cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (u, s)).fetchone():
                st.session_state.autenticado, st.session_state.user = True, u
                st.rerun()
            else: st.error("Usuário ou senha incorretos.")
            
    with aba_cad:
        nu = st.text_input("Novo Usuário").lower().strip()
        ns = st.text_input("Nova Senha", type="password")
        if st.button("CRIAR MINHA CONTA"):
            try:
                cursor.execute("INSERT INTO usuarios VALUES (?,?)", (nu, ns))
                conn.commit(); st.success("✅ Conta criada! Volte para a aba ENTRAR.")
            except: st.error("❌ Este usuário já existe.")
    st.stop()

user = st.session_state.user
hoje = date.today()

# --- 4. SIDEBAR (BONEQUINHO E CONFIGURAÇÕES) ---
with st.sidebar:
    st.markdown(f"<h1 style='text-align: center; font-size: 100px; margin-bottom: 0;'>👤</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; margin-top: 0;'>{user.upper()}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("🚗 RECONFIGURAR CARRO"):
        cursor.execute("DELETE FROM veiculo WHERE usuario=?", (user,))
        conn.commit(); st.rerun()

    if st.button("🚪 SAIR DO APP"):
        st.session_state.autenticado = False
        st.rerun()

    st.markdown("---")
    if st.button("⚠️ APAGAR TUDO"):
        cursor.execute("DELETE FROM ganhos WHERE usuario=?", (user,))
        cursor.execute("DELETE FROM metas WHERE usuario=?", (user,))
        cursor.execute("DELETE FROM veiculo WHERE usuario=?", (user,))
        conn.commit(); st.rerun()

# --- 5. LÓGICA DO VEÍCULO ---
v_data = cursor.execute("SELECT * FROM veiculo WHERE usuario=?", (user,)).fetchone()
if v_data is None:
    st.header("⚙️ Configuração do Carro")
    with st.form("cfg"):
        f_val = st.number_input("Valor FIPE do Veículo", value=45000.0)
        k_val = st.number_input("KM Inicial", value=100000.0)
        if st.form_submit_button("CONCLUIR CONFIGURAÇÃO"):
            cursor.execute("INSERT INTO veiculo VALUES (?,?,?,?)", (user, k_val, f_val, 0.0))
            conn.commit(); st.rerun()
    st.stop()

# --- 6. PAINEL PRINCIPAL ---
st.title(f"🚀 PAINEL DE CONTROLE")
t1, t2, t3 = st.tabs(["📊 IPVA", "💰 GANHOS", "🎯 CAIXINHAS"])

# ABA IPVA
with t1:
    fipe, guardado = v_data[2], v_data[3]
    total_ipva = fipe * 0.04
    st.metric("Estimativa IPVA", f"R$ {total_ipva:.2f}")
    st.metric("Saldo no Fundo", f"R$ {guardado:.2f}")
    
    val_ipva = st.number_input("Valor para movimentar (R$):", value=0.0, key="ipva_input")
    c1, c2 = st.columns(2)
    if c1.button("📥 DEPOSITAR"):
        cursor.execute("UPDATE veiculo SET guardado_ipva = guardado_ipva + ? WHERE usuario=?", (val_ipva, user))
        conn.commit(); st.rerun()
    if c2.button("📤 ESTORNAR"):
        cursor.execute("UPDATE veiculo SET guardado_ipva = guardado_ipva - ? WHERE usuario=?", (val_ipva, user))
        conn.commit(); st.rerun()

# ABA GANHOS
with t2:
    with st.form("form_ganhos", clear_on_submit=True):
        st.subheader("Registrar Faturamento")
        g1, g2, g3 = st.columns(3)
        bruto = g1.number_input("Bruto (R$)")
        gasto = g2.number_input("Gasto (R$)")
        km_r = g3.number_input("KM Rodada")
        if st.form_submit_button("SALVAR DIA"):
            cursor.execute("INSERT INTO ganhos (usuario, data, ganho, gasto, km) VALUES (?,?,?,?,?)", 
                           (user, str(hoje), bruto, gasto, km_r))
            conn.commit(); st.rerun()

    df_g = pd.read_sql_query(f"SELECT * FROM ganhos WHERE usuario='{user}' ORDER BY id DESC", conn)
    for i, r in df_g.iterrows():
        with st.container():
            col_t, col_d = st.columns([4, 1])
            col_t.markdown(f"📅 **{r['data']}** | Lucro: **R$ {r['ganho']-r['gasto']:.2f}**")
            if col_d.button("🗑️", key=f"del_g_{r['id']}"):
                cursor.execute("DELETE FROM ganhos WHERE id=?", (r['id'],))
                conn.commit(); st.rerun()

# ABA CAIXINHAS
with t3:
    st.subheader("Seus Objetivos")
    with st.expander("➕ CRIAR META"):
        with st.form("f_meta"):
            nome_m = st.text_input("O que você quer comprar?"); valor_m = st.number_input("Preço Total")
            if st.form_submit_button("CRIAR CAIXINHA"):
                cursor.execute("INSERT INTO metas (usuario, item, valor, guardado) VALUES (?,?,?,?)", (user, nome_m, valor_m, 0.0))
                conn.commit(); st.rerun()
    
    metas_db = pd.read_sql_query(f"SELECT * FROM metas WHERE usuario='{user}'", conn)
    for i, m in metas_db.iterrows():
        with st.container():
            st.write(f"### 🚀 {m['item']}")
            st.progress(min((m['guardado'] or 0)/m['valor'], 1.0) if m['valor'] > 0 else 0)
            v_mov = st.number_input("Valor da Operação:", key=f"m_{m['id']}", value=0.0)
            c1, c2, c3 = st.columns(3)
            if c1.button("📥", key=f"in_{m['id']}"):
                cursor.execute("UPDATE metas SET guardado = guardado + ? WHERE id=?", (v_mov, m['id'])); conn.commit(); st.rerun()
            if c2.button("📤", key=f"out_{m['id']}"):
                cursor.execute("UPDATE metas SET guardado = guardado - ? WHERE id=?", (v_mov, m['id'])); conn.commit(); st.rerun()
            if c3.button("🗑️", key=f"del_m_{m['id']}"):
                cursor.execute("DELETE FROM metas WHERE id=?", (m['id'],)); conn.commit(); st.rerun()
