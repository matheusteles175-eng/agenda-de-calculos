import streamlit as st
import pandas as pd
import os
from datetime import date, time, datetime

# --- CONFIGURAÇÃO DA PÁGINA (Muda o nome e o ícone na aba) ---
st.set_page_config(
    page_title="Calculadora de Ganhos", 
    page_icon="🚖", 
    layout="centered"
)

# --- REMOVER MARCAS DO STREAMLIT (Esconde Menu e Rodapé) ---
estilo_customizado = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    #stDecoration {display:none;}
    </style>
"""
st.markdown(estilo_customizado, unsafe_allow_html=True)

ARQUIVO_USUARIOS = "usuarios.csv"

# --- FUNÇÕES DE SUPORTE ---
def carregar_usuarios():
    if os.path.exists(ARQUIVO_USUARIOS):
        return pd.read_csv(ARQUIVO_USUARIOS, dtype=str)
    else:
        df = pd.DataFrame([{"usuario": "matheus", "senha": "123"}])
        df.to_csv(ARQUIVO_USUARIOS, index=False)
        return df

if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = ""

# --- TELA DE ACESSO ---
def tela_acesso():
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🚖 Painel do Motorista</h1>", unsafe_allow_html=True)
    aba1, aba2 = st.tabs(["Entrar", "Criar Conta"])
    df_usuarios = carregar_usuarios()

    with aba1:
        u_login = st.text_input("Usuário", key="login_user").strip().lower()
        s_login = st.text_input("Senha", type="password", key="login_pass").strip()
        if st.button("Entrar no Painel", use_container_width=True):
            user_match = df_usuarios[(df_usuarios['usuario'].str.lower() == u_login) & (df_usuarios['senha'] == s_login)]
            if not user_match.empty:
                st.session_state.logado = True
                st.session_state.usuario_atual = u_login
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    with aba2:
        novo_u = st.text_input("Novo Usuário", key="cad_user").strip().lower()
        novo_s = st.text_input("Nova Senha", type="password", key="cad_pass").strip()
        if st.button("Criar Minha Conta", use_container_width=True):
            if novo_u == "" or novo_s == "":
                st.error("Preencha todos os campos!")
            elif novo_u in df_usuarios['usuario'].str.lower().values:
                st.error("Este usuário já existe!")
            else:
                novo_reg = pd.DataFrame([{"usuario": novo_u, "senha": novo_s}])
                pd.concat([df_usuarios, novo_reg], ignore_index=True).to_csv(ARQUIVO_USUARIOS, index=False)
                st.success("Conta criada! Já pode fazer login.")

# --- PAINEL PRINCIPAL ---
if st.session_state.logado:
    user = st.session_state.usuario_atual
    arq_dados = f"dados_{user}.csv"
    arq_meta = f"meta_{user}.txt"

    if os.path.exists(arq_meta):
        with open(arq_meta, "r") as f:
            try: meta_atual = float(f.read())
            except: meta_atual = 0.0
    else: meta_atual = 0.0

    st.sidebar.write(f"👤 Motorista: **{user.capitalize()}**")
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.usuario_atual = ""
        st.rerun()

    st.title("📊 Gestão de Ganhos")

    if os.path.exists(arq_dados):
        df_dados = pd.read_csv(arq_dados)
        for col in ['Ganho', 'Gasto', 'KM']:
            if col not in df_dados.columns: df_dados[col] = 0.0
            df_dados[col] = pd.to_numeric(df_dados[col], errors='coerce').fillna(0.0)
        if 'H_Inicio' not in df_dados.columns: df_dados['H_Inicio'] = "06:00"
        if 'H_Fim' not in df_dados.columns: df_dados['H_Fim'] = "11:00"
    else:
        df_dados = pd.DataFrame(columns=["Data", "Ganho", "Gasto", "KM", "H_Inicio", "H_Fim"])

    with st.container(border=True):
        st.subheader("🎯 Configuração Diária")
        input_meta = st.number_input("Sua Meta Diária (R$)", min_value=0.0, value=meta_atual, step=10.0)
        if input_meta != meta_atual:
            with open(arq_meta, "w") as f: f.write(str(input_meta))
            st.rerun()

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        val_ganho = c1.number_input("Ganho Bruto (R$)", min_value=0.0, step=1.0)
        val_gasto = c2.number_input("Gasto (R$)", min_value=0.0, step=1.0)
        val_km = c3.number_input("KM Rodado", min_value=0.0, step=1.0)
        
        ch1, ch2 = st.columns(2)
        val_h_ini = ch1.time_input("Horário de Início", value=time(6, 0))
        val_h_fim = ch2.time_input("Horário de Término", value=time(11, 0))
        
        if st.button("➕ SALVAR REGISTRO", use_container_width=True, type="primary"):
            hoje_data = date.today().strftime("%d/%m/%Y")
            nova_linha = pd.DataFrame({
                "Data": [hoje_data], "Ganho": [val_ganho], "Gasto": [val_gasto], "KM": [val_km],
                "H_Inicio": [val_h_ini.strftime("%H:%M")], "H_Fim": [val_h_fim.strftime("%H:%M")]
            })
            df_dados = pd.concat([df_dados, nova_linha], ignore_index=True)
            df_dados.to_csv(arq_dados, index=False)
            st.success("Salvo!")
            st.rerun()

    hoje_hoje = date.today().strftime("%d/%m/%Y")
    df_hoje = df_dados[df_dados['Data'] == hoje_hoje]
    total_bruto = df_hoje['Ganho'].sum()
    total_km = df_hoje['KM'].sum()
    saldo_liquido = total_bruto - df_hoje['Gasto'].sum()
    
    horas_totais = 0.0
    for _, linha in df_hoje.iterrows():
        try:
            t_ini = datetime.strptime(linha['H_Inicio'], "%H:%M")
            t_fim = datetime.strptime(linha['H_Fim'], "%H:%M")
            dif = (t_fim - t_ini).total_seconds() / 3600
            if dif < 0: dif += 24
            horas_totais += dif
        except: continue

    val_km_medio = total_bruto / total_km if total_km > 0 else 0
    val_hora_media = total_bruto / horas_totais if horas_totais > 0 else 0

    cor_box = "#28a745" if saldo_liquido >= input_meta and input_meta > 0 else "#dc3545" if input_meta > 0 else "#444444"
    st.markdown(f"""
        <div style="background-color: {cor_box}; padding: 25px; border-radius: 15px; text-align: center; color: white; margin-bottom: 20px;">
            <p style="margin: 0; opacity: 0.8;">Saldo Líquido de Hoje</p>
            <h1 style="margin: 0; font-size: 3em;">R$ {saldo_liquido:.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("KM Hoje", f"{total_km:.1f} km")
    col_m2.metric("R$ por KM", f"R$ {val_km_medio:.2f}")
    col_m3.metric("R$ por Hora", f"R$ {val_hora_media:.2f}")

    if not df_dados.empty:
        st.markdown("---")
        st.subheader("📜 Histórico")
        for i, registro in df_dados.iloc[::-1].head(10).iterrows():
            with st.container(border=True):
                c_inf, c_val, c_btn = st.columns([1.5, 2, 0.5])
                with c_inf:
                    st.write(f"📅 **{registro['Data']}**")
                    st.write(f"⏰ {registro['H_Inicio']} - {registro['H_Fim']}")
                with c_val:
                    lucro = float(registro['Ganho']) - float(registro['Gasto'])
                    st.write(f"💰 Lucro: **R$ {lucro:.2f}**")
                    st.write(f"🚗 {registro['KM']} km")
                with c_btn:
                    if st.button("🗑️", key=f"del_{i}"):
                        df_dados = df_dados.drop(i).to_csv(arq_dados, index=False)
                        st.rerun()
else:
    tela_acesso()
