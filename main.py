import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# --- 1. CONFIGURAÇÃO E ESTILO (VISUAL DARK TOTAL) ---
st.set_page_config(
    page_title="CheckPoint Shift 🏁", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

st.markdown("""
<style>
    /* FUNDO DO APLICATIVO */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.9)), 
                    url("https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* A SETINHA (SIDEBAR) - PRETA E VISÍVEL */
    button[kind="headerNoContext"] {
        background-color: #000000 !important;
        color: white !important;
        border-radius: 10px !important;
        width: 60px !important;
        height: 60px !important;
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 999999 !important;
        border: 2px solid #28a745 !important;
    }

    /* LIMPANDO O PANO BRANCO DOS CAMPOS DE DIGITAR */
    input, [data-baseweb="input"], [data-testid="stNumberInput"] div {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    /* TEXTOS E INTERFACE */
    html, body, [class*="st-"], div, p, label {
        font-size: 20px !important; 
        color: white !important;
    }
    
    /* CARDS DE RESULTADO (META/DÉFICIT) */
    .card-meta {
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        border: 4px solid;
    }
    .meta-sucesso { background-color: rgba(0, 255, 127, 0.2); border-color: #00FF7F; color: #00FF7F; }
    .meta-falta { background-color: rgba(255, 75, 75, 0.2); border-color: #FF4B4B; color: #FF4B4B; }

    /* BOTÕES */
    .stButton>button {
        width: 100%; border-radius: 12px; font-weight: bold; 
        font-size: 22px !important; height: 3.5em;
        background-color: #28a745 !important; color: white !important;
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
    st.markdown("<h1 style='text-align: center;'>🏁 CheckPoint Shift</h1>", unsafe_allow_html=True)
    aba_login, aba_cad = st.tabs(["🔑 ENTRAR", "📝 CADASTRAR"])
    with aba_login:
        u = st.text_input("Usuário").lower().strip()
        s = st.text_input("Senha", type="password")
        if st.button("ACESSAR SISTEMA"):
            if cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (u, s)).fetchone():
                st.session_state.autenticado, st.session_state.user = True, u
                st.rerun()
            else: st.error("Incorreto.")
    with aba_cad:
        nu = st.text_input("Novo Usuário").lower().strip()
        ns = st.text_input("Nova Senha", type="password")
        if st.button("CRIAR MINHA CONTA"):
            try:
                cursor.execute("INSERT INTO usuarios VALUES (?,?)", (nu, ns))
                conn.commit(); st.success("✅ Criado!")
            except: st.error("❌ Já existe.")
    st.stop()

user = st.session_state.user
hoje = date.today()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<h1 style='text-align: center; font-size: 100px;'>👤</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>{user.upper()}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚗 RECONFIGURAR CARRO"):
        cursor.execute("DELETE FROM veiculo WHERE usuario=?", (user,))
        conn.commit(); st.rerun()
    if st.button("🚪 SAIR"):
        st.session_state.autenticado = False
        st.rerun()

# --- 5. VEÍCULO ---
v_data = cursor.execute("SELECT * FROM veiculo WHERE usuario=?", (user,)).fetchone()
if v_data is None:
    st.header("⚙️ Configuração")
    with st.form("cfg"):
        f_val = st.number_input("Valor FIPE", value=45000.0)
        k_val = st.number_input("KM Inicial", value=100000.0)
        if st.form_submit_button("CONCLUIR"):
            cursor.execute("INSERT INTO veiculo VALUES (?,?,?,?)", (user, k_val, f_val, 0.0))
            conn.commit(); st.rerun()
    st.stop()

# --- 6. PAINEL ---
st.title(f"🚀 PAINEL DE CONTROLE")
t1, t2, t3 = st.tabs(["📊 IPVA", "💰 GANHOS", "🎯 CAIXINHAS"])

# ABA IPVA
with t1:
    fipe, guardado = v_data[2], v_data[3]
    total_ipva = fipe * 0.04
    st.metric("Estimativa IPVA", f"R$ {total_ipva:.2f}")
    st.metric("Saldo no Fundo", f"R$ {guardado:.2f}")
    val_ipva = st.number_input("Valor R$:", value=0.0, key="ipva_input")
    c1, c2 = st.columns(2)
    if c1.button("📥 DEPOSITAR"):
        cursor.execute("UPDATE veiculo SET guardado_ipva = guardado_ipva + ? WHERE usuario=?", (val_ipva, user))
        conn.commit(); st.rerun()
    if c2.button("📤 ESTORNAR"):
        cursor.execute("UPDATE veiculo SET guardado_ipva = guardado_ipva - ? WHERE usuario=?", (val_ipva, user))
        conn.commit(); st.rerun()

# ABA GANHOS (COM LÓGICA DE META DIÁRIA)
with t2:
    meta_diaria = st.number_input("Sua Meta de Lucro de Hoje (R$):", value=400.0)
    with st.form("form_ganhos", clear_on_submit=True):
        st.subheader("Registrar Faturamento")
        g1, g2, g3 = st.columns(3)
        bruto = g1.number_input("Bruto (R$)")
        gasto = g2.number_input("Gasto (R$)")
        km_r = g3.number_input("KM Rodada")
        if st.form_submit_button("SALVAR DIA"):
            cursor.execute("INSERT INTO ganhos (usuario, data, ganho, gasto, km) VALUES (?,?,?,?,?,?)", 
                           (user, str(hoje), bruto, gasto, km_r))
            conn.commit(); st.rerun()

    # LÓGICA DO PARABÉNS / DÉFICIT
    lucro_hoje = bruto - gasto
    if bruto > 0:
        if lucro_hoje >= meta_diaria:
            passou = lucro_hoje - meta_diaria
            st.markdown(f'<div class="card-meta meta-sucesso"><h1>META BATIDA! 🚀</h1><p style="font-size: 40px;">R$ {lucro_hoje:.2f}</p><p>Parabéns! Você ultrapassou <b>R$ {passou:.2f}</b> da meta!</p></div>', unsafe_allow_html=True)
        else:
            deficit = meta_diaria - lucro_hoje
            st.markdown(f'<div class="card-meta meta-falta"><h1>META EM DÉFICIT ⚠️</h1><p style="font-size: 40px;">R$ {lucro_hoje:.2f}</p><p>Faltam <b>R$ {deficit:.2f}</b> para a meta.</p></div>', unsafe_allow_html=True)

# ABA CAIXINHAS
with t3:
    st.subheader("Objetivos")
    with st.expander("➕ CRIAR META"):
        with st.form("f_meta"):
            nome_m = st.text_input("Item"); valor_m = st.number_input("Total R$")
            if st.form_submit_button("CRIAR"):
                cursor.execute("INSERT INTO metas (usuario, item, valor, guardado) VALUES (?,?,?,?)", (user, nome_m, valor_m, 0.0))
                conn.commit(); st.rerun()
    
    metas_db = pd.read_sql_query(f"SELECT * FROM metas WHERE usuario='{user}'", conn)
    for i, m in metas_db.iterrows():
        with st.container():
            st.write(f"### 🚀 {m['item']}")
            st.progress(min((m['guardado'] or 0)/m['valor'], 1.0) if m['valor'] > 0 else 0)
            v_mov = st.number_input("Valor:", key=f"m_{m['id']}", value=0.0)
            c1, c2, c3 = st.columns(3)
            if c1.button("📥", key=f"in_{m['id']}"):
                cursor.execute("UPDATE metas SET guardado = guardado + ? WHERE id=?", (v_mov, m['id'])); conn.commit(); st.rerun()
            if c2.button("📤", key=f"out_{m['id']}"):
                cursor.execute("UPDATE metas SET guardado = guardado - ? WHERE id=?", (v_mov, m['id'])); conn.commit(); st.rerun()
            if c3.button("🗑️", key=f"del_m_{m['id']}"):
                cursor.execute("DELETE FROM metas WHERE id=?", (m['id'],)); conn.commit(); st.rerun()
