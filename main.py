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

# Estilo CSS para tirar o pano branco e destacar a setinha
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url("https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* Botão da Sidebar (Setinha) destacado */
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
        border: 2px solid white !important;
    }
    
    /* Pano branco nos inputs: removido */
    input, [data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }

    /* Cards de Meta */
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
        background-color: rgba(255, 255, 255, 0.1) !important; color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS ---
def conectar():
    # Usando o nome do banco que você já tinha dados
    conn = sqlite3.connect("checkpoint_shift_mateus.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT PRIMARY KEY, senha TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS veiculo (usuario TEXT PRIMARY KEY, km_ini REAL, km_alvo REAL, custo REAL, fipe REAL, guardado_ipva REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS metas (id INTEGER PRIMARY KEY, usuario TEXT, item TEXT, valor REAL, data TEXT, guardado REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS ganhos (id INTEGER PRIMARY KEY, usuario TEXT, data TEXT, ganho REAL, gasto REAL, km REAL, h_ini TEXT, h_fim TEXT)")
    conn.commit()
    return conn, cursor

conn, cursor = conectar()

# --- 3. LOGIN / AUTENTICAÇÃO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🏁 CheckPoint Shift")
    t_login, t_cad = st.tabs(["🔑 Entrar", "📝 Cadastrar"])
    
    with t_login:
        u = st.text_input("Usuário").lower().strip()
        s = st.text_input("Senha", type="password")
        if st.button("LOGAR"):
            check = cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (u, s)).fetchone()
            if check:
                st.session_state.autenticado = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Dados incorretos.")
                
    with t_cad:
        nu = st.text_input("Novo Usuário").lower()
        ns = st.text_input("Nova Senha", type="password")
        if st.button("CRIAR"):
            try:
                cursor.execute("INSERT INTO usuarios VALUES (?,?)", (nu, ns))
                conn.commit()
                st.success("Criado!")
            except:
                st.error("Erro ou usuário já existe.")
    st.stop()

# --- 4. CÓDIGO DO PAINEL (Lógica de Meta e Abas) ---
user = st.session_state.user
hoje = date.today()

# Sidebar com bonequinho
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>👤</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{user.upper()}</h3>", unsafe_allow_html=True)
    if st.button("SAIR"):
        st.session_state.autenticado = False
        st.rerun()

# Pegar dados do veículo
v_data = cursor.execute("SELECT * FROM veiculo WHERE usuario=?", (user,)).fetchone()
if not v_data:
    st.warning("Configure seu carro primeiro.")
    with st.form("car"):
        f = st.number_input("Fipe", value=40000.0)
        k = st.number_input("KM", value=100000.0)
        if st.form_submit_button("Salvar"):
            cursor.execute("INSERT INTO veiculo VALUES (?,?,?,?,?,?)", (user, k, k+10000, 350.0, f, 0.0))
            conn.commit()
            st.rerun()
    st.stop()

# Abas principais
tab1, tab2, tab3 = st.tabs(["📊 IPVA", "💰 GANHOS", "🎯 CAIXINHAS"])

with tab2:
    meta = st.number_input("Meta Diária (R$)", value=400.0)
    with st.form("dia"):
        b = st.number_input("Bruto")
        g = st.number_input("Gastos")
        if st.form_submit_button("Salvar"):
            cursor.execute("INSERT INTO ganhos (usuario, data, ganho, gasto, km, h_ini, h_fim) VALUES (?,?,?,?,?,?,?)", (user, str(hoje), b, g, 0, "08", "18"))
            conn.commit()
            st.rerun()
            
    lucro = b - g
    if b > 0:
        if lucro >= meta:
            p = lucro - meta
            st.markdown(f'<div class="card-meta meta-sucesso"><h1>META BATIDA! 🚀</h1><p>Lucro: R$ {lucro:.2f}</p><p>Parabéns! Passou R$ {p:.2f} da meta!</p></div>', unsafe_allow_html=True)
        else:
            d = meta - lucro
            st.markdown(f'<div class="card-meta meta-falta"><h1>DÉFICIT ⚠️</h1><p>Lucro: R$ {lucro:.2f}</p><p>Faltam R$ {d:.2f} para a meta.</p></div>', unsafe_allow_html=True)

with tab1:
    st.write(f"Saldo IPVA: R$ {v_data[5]:.2f}")
    val = st.number_input("Valor", key="ipva")
    if st.button("Depositar"):
        cursor.execute("UPDATE veiculo SET guardado_ipva = guardado_ipva + ? WHERE usuario=?", (val, user))
        conn.commit()
        st.rerun()

with tab3:
    st.write("Suas metas aqui.")
