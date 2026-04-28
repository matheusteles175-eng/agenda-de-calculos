import streamlit as st
import pandas as pd
import os
from datetime import date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Calculadora de Ganhos", page_icon="🚖")

ARQUIVO_USUARIOS = "usuarios.csv"

# FUNÇÃO PARA GERENCIAR USUÁRIOS
def carregar_usuarios():
    if os.path.exists(ARQUIVO_USUARIOS):
        return pd.read_csv(ARQUIVO_USUARIOS)
    else:
        df = pd.DataFrame([{"usuario": "matheus", "senha": "123"}])
        df.to_csv(ARQUIVO_USUARIOS, index=False)
        return df

if "logado" not in st.session_state:
    st.session_state.logado = False

# TELA DE LOGIN E CADASTRO
def tela_acesso():
    st.title("🚖 Sistema de Ganhos")
    aba1, aba2 = st.tabs(["Entrar", "Criar Conta"])
    df_usuarios = carregar_usuarios()

    with aba1:
        u = st.text_input("Usuário").lower()
        s = st.text_input("Senha", type="password")
        if st.button("Login"):
            user_match = df_usuarios[(df_usuarios['usuario'] == u) & (df_usuarios['senha'] == str(s))]
            if not user_match.empty:
                st.session_state.logado = True
                st.session_state.usuario_atual = u
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    with aba2:
        novo_u = st.text_input("Novo Usuário").lower()
        novo_s = st.text_input("Nova Senha", type="password")
        if st.button("Cadastrar"):
            if novo_u in df_usuarios['usuario'].values:
                st.error("Usuário já existe!")
            else:
                novo_reg = pd.DataFrame([{"usuario": novo_u, "senha": str(novo_s)}])
                pd.concat([df_usuarios, novo_reg]).to_csv(ARQUIVO_USUARIOS, index=False)
                st.success("Conta criada! Agora faça login.")

# ÁREA DO MOTORISTA
if st.session_state.logado:
    st.sidebar.write(f"Logado como: **{st.session_state.usuario_atual}**")
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title(f"📊 Painel de {st.session_state.usuario_atual.capitalize()}")
    arq_dados = f"dados_{st.session_state.usuario_atual}.csv"
    
    df = pd.read_csv(arq_dados) if os.path.exists(arq_dados) else pd.DataFrame(columns=["Data", "Ganho", "Gasto"])

    with st.form("lancamento"):
        g = st.number_input("Ganhos (R$)", min_value=0.0)
        p = st.number_input("Gastos (R$)", min_value=0.0)
        if st.form_submit_button("Salvar"):
            nova_linha = pd.DataFrame({"Data": [date.today().strftime("%d/%m/%Y")], "Ganho": [g], "Gasto": [p]})
            pd.concat([df, nova_linha]).to_csv(arq_dados, index=False)
            st.success("Gravado!")
            st.rerun()

    if not df.empty:
        st.metric("Saldo Total", f"R$ {(df['Ganho'].sum() - df['Gasto'].sum()):.2f}")
        st.dataframe(df)
else:
    tela_acesso()
