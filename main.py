import streamlit as st
import pandas as pd
import os
from datetime import date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Calculadora de Ganhos", page_icon="🚖", layout="centered")

ARQUIVO_USUARIOS = "usuarios.csv"

def carregar_usuarios():
    if os.path.exists(ARQUIVO_USUARIOS):
        return pd.read_csv(ARQUIVO_USUARIOS, dtype=str)
    else:
        df = pd.DataFrame([{"usuario": "matheus", "senha": "123"}])
        df.to_csv(ARQUIVO_USUARIOS, index=False)
        return df

if "logado" not in st.session_state:
    st.session_state.logado = False

def tela_acesso():
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🚖 Sistema de Ganhos</h1>", unsafe_allow_html=True)
    aba1, aba2 = st.tabs(["Entrar", "Criar Conta"])
    df_usuarios = carregar_usuarios()

    with aba1:
        u = st.text_input("Usuário", key="login_user").strip()
        s = st.text_input("Senha", type="password", key="login_pass").strip()
        if st.button("Entrar no Painel", use_container_width=True):
            sucesso = False
            for index, row in df_usuarios.iterrows():
                if str(row['usuario']).lower() == u.lower() and str(row['senha']) == s:
                    sucesso = True
                    break
            if sucesso:
                st.session_state.logado = True
                st.session_state.usuario_atual = u
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    with aba2:
        novo_u = st.text_input("Novo Usuário", key="cad_user").strip()
        novo_s = st.text_input("Nova Senha", type="password", key="cad_pass").strip()
        if st.button("Criar Minha Conta", use_container_width=True):
            if novo_u == "" or novo_s == "":
                st.error("Preencha todos os campos!")
            elif novo_u.lower() in df_usuarios['usuario'].str.lower().values:
                st.error("Este usuário já existe!")
            else:
                novo_reg = pd.DataFrame([{"usuario": novo_u, "senha": str(novo_s)}])
                pd.concat([df_usuarios, novo_reg], ignore_index=True).to_csv(ARQUIVO_USUARIOS, index=False)
                st.success("Conta criada!")

if st.session_state.logado:
    usuario_path = st.session_state.usuario_atual.lower()
    arq_dados = f"dados_{usuario_path}.csv"
    arq_meta = f"meta_{usuario_path}.txt"

    # Carregar meta salva
    if os.path.exists(arq_meta):
        with open(arq_meta, "r") as f:
            try: meta_atual = float(f.read())
            except: meta_atual = 0.0
    else:
        meta_atual = 0.0

    st.sidebar.write(f"👤 Motorista: **{st.session_state.usuario_atual.capitalize()}**")
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title(f"📊 Gestão de Ganhos")

    # --- FORMULÁRIO DE LANÇAMENTO COM CAMPO DE META ---
    df_dados = pd.read_csv(arq_dados) if os.path.exists(arq_dados) else pd.DataFrame(columns=["Data", "Ganho", "Gasto"])

    with st.container(border=True):
        st.subheader("📝 Lançamento Diário")
        
        # Campo de Meta - Fica no topo e atualiza a memória
        nova_meta = st.number_input("🎯 Defina sua Meta do Dia (R$)", min_value=0.0, value=meta_atual, step=10.0)
        if nova_meta != meta_atual:
            with open(arq_meta, "w") as f:
                f.write(str(nova_meta))
            st.rerun()

        st.markdown("---")
        
        col_g, col_p = st.columns(2)
        g = col_g.number_input("Ganho (R$)", min_value=0.0, step=1.0, key="ganho_input")
        p = col_p.number_input("Gasto (R$)", min_value=0.0, step=1.0, key="gasto_input")
        
        if st.button("➕ SALVAR E CALCULAR", use_container_width=True, type="primary"):
            nova_linha = pd.DataFrame({"Data": [date.today().strftime("%d/%m/%Y")], "Ganho": [g], "Gasto": [p]})
            df_dados =
                         
