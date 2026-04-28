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

    # Carrega a meta da memória com segurança
    if os.path.exists(arq_meta):
        with open(arq_meta, "r") as f:
            try:
                meta_atual = float(f.read())
            except:
                meta_atual = 0.0
    else:
        meta_atual = 0.0

    st.sidebar.write(f"👤 Motorista: **{st.session_state.usuario_atual.capitalize()}**")
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title(f"📊 Gestão de Ganhos")

    # Tenta ler os dados, se não existir cria um vazio
    if os.path.exists(arq_dados):
        df_dados = pd.read_csv(arq_dados)
        df_dados['Ganho'] = pd.to_numeric(df_dados['Ganho'], errors='coerce').fillna(0.0)
        df_dados['Gasto'] = pd.to_numeric(df_dados['Gasto'], errors='coerce').fillna(0.0)
    else:
        df_dados = pd.DataFrame(columns=["Data", "Ganho", "Gasto"])

    # --- FORMULÁRIO DE LANÇAMENTO ---
    with st.container(border=True):
        st.subheader("🎯 Configuração Diária")
        
        # Campo de Meta que salva na memória
        nova_meta = st.number_input("Defina sua Meta Diária (R$)", min_value=0.0, value=meta_atual, step=10.0)
        if nova_meta != meta_atual:
            with open(arq_meta, "w") as f:
                f.write(str(nova_meta))
            st.rerun()

        st.markdown("---")
        col_g, col_p = st.columns(2)
        g = col_g.number_input("Ganho de Agora (R$)", min_value=0.0, step=1.0)
        p = col_p.number_input("Gasto de Agora (R$)", min_value=0.0, step=1.0)
        
        if st.button("➕ SALVAR REGISTRO", use_container_width=True, type="primary"):
            hoje_data = date.today().strftime("%d/%m/%Y")
            nova_linha = pd.DataFrame({"Data": [hoje_data], "Ganho": [g], "Gasto": [p]})
            df_dados = pd.concat([df_dados, nova_linha], ignore_index=True)
            df_dados.to_csv(arq_dados, index=False)
            st.success("Gravado!")
            st.rerun()

    # --- CÁLCULO E RESULTADO VISUAL ---
    hoje_str = date.today().strftime("%d/%m/%Y")
    df_hoje = df_dados[df_dados['Data'] == hoje_str]
    saldo_hoje = df_hoje['Ganho'].sum() - df_hoje['Gasto'].sum()

    # Define cor e texto baseado na meta
    if nova_meta > 0:
        if saldo_hoje >= nova_meta:
            cor_fundo = "#28a745" # Verde
            texto_status = "✅ META BATIDA!"
        else:
            cor_fundo = "#dc3545" # Vermelho
            texto_status = "❌ AINDA FALTA PARA A META"
    else:
        cor_fundo = "#444444" # Cinza
        texto_status = "🎯 DIGITE UMA META ACIMA"

    st.markdown(f"""
        <div style="background-color: {cor_fundo}; padding: 30px; border-radius: 15px; text-align: center; color: white;">
            <p style="margin: 0; opacity: 0.8;">Saldo de Hoje</p>
            <h1 style="margin: 0; font-size: 3.5em;">R$ {saldo_hoje:.2f}</h1>
            <p style="font-weight: bold; font-size: 1.2em; margin-top: 10px;">{texto_status}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- HISTÓRICO ---
    if not df_dados.empty:
        st.write("### 📜 Histórico Recente")
        for i, row in df_dados.iloc[::-1].head(5).iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 1, 0.4])
                c1.write(f"📅 {row['Data']}")
                lucro = float(row['Ganho']) - float(row['Gasto'])
                c2.write(f"💰 Lucro: R$ {lucro:.2f}")
                if c3.button("🗑️", key=f"del_{i}"):
                    df_dados = df_dados.drop(i)
                    df_dados.to_csv(arq_dados, index=False)
                    st.rerun()
else:
    tela_acesso()
    
