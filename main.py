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
    # --- ÁREA LATERAL ---
    st.sidebar.markdown(f"### 👤 {st.session_state.usuario_atual.capitalize()}")
    
    # --- NOVIDADE: DEFINIR META ---
    st.sidebar.markdown("---")
    meta_diaria = st.sidebar.number_input("🎯 Sua Meta Diária (R$)", min_value=0.0, value=300.0, step=10.0)
    
    if st.sidebar.button("Sair do Sistema"):
        st.session_state.logado = False
        st.rerun()

    st.title(f"📊 Painel de Controle")
    
    arq_dados = f"dados_{st.session_state.usuario_atual.lower()}.csv"
    df_dados = pd.read_csv(arq_dados) if os.path.exists(arq_dados) else pd.DataFrame(columns=["Data", "Ganho", "Gasto"])

    # --- FORMULÁRIO DE LANÇAMENTO ---
    with st.container(border=True):
        st.subheader("📝 Novo Lançamento")
        col_g, col_p = st.columns(2)
        with col_g:
            g = st.number_input("Ganho (R$)", min_value=0.0, step=10.0, key="input_ganho")
        with col_p:
            p = st.number_input("Gasto (R$)", min_value=0.0, step=10.0, key="input_gasto")
        
        if st.button("➕ SALVAR REGISTRO", use_container_width=True, type="primary"):
            nova_linha = pd.DataFrame({"Data": [date.today().strftime("%d/%m/%Y")], "Ganho": [g], "Gasto": [p]})
            df_dados = pd.concat([df_dados, nova_linha], ignore_index=True)
            df_dados.to_csv(arq_dados, index=False)
            st.success("Dados gravados!")
            st.rerun()

    # --- MÉTRICAS COM LÓGICA DE META ---
    if not df_dados.empty:
        # Filtra apenas os dados de HOJE para a meta
        hoje = date.today().strftime("%d/%m/%Y")
        df_hoje = df_dados[df_dados['Data'] == hoje]
        
        ganho_hoje = df_hoje['Ganho'].sum()
        gasto_hoje = df_hoje['Gasto'].sum()
        saldo_hoje = ganho_hoje - gasto_hoje
        
        # Cor da meta
        cor_meta = "#28a745" if saldo_hoje >= meta_diaria else "#dc3545"
        label_meta = "✅ META ATINGIDA!" if saldo_hoje >= meta_diaria else "❌ ABAIXO DA META"

        st.markdown(f"### Resumo de Hoje ({hoje})")
        
        # Mostra o Saldo de Hoje com a cor dinâmica
        st.markdown(f"""
            <div style="background-color: {cor_meta}; padding: 20px; border-radius: 10px; text-align: center;">
                <h2 style="color: white; margin: 0;">R$ {saldo_hoje:.2f}</h2>
                <strong style="color: white;">{label_meta} (Meta: R$ {meta_diaria:.2f})</strong>
            </div>
        """, unsafe_allow_html=True)

        # Outras métricas gerais
        col1, col2 = st.columns(2)
        col1.metric("Total Ganhos (Geral)", f"R$ {df_dados['Ganho'].sum():.2f}")
        col2.metric("Total Gastos (Geral)", f"R$ {df_dados['Gasto'].sum():.2f}")

        # --- HISTÓRICO ---
        st.markdown("---")
        st.subheader("🗓️ Histórico de Lançamentos")
        
        for i, row in df_dados.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([1.5, 2, 2, 0.5])
                c1.write(f"**{row['Data']}**")
                c2.markdown(f"<span style='color: #28a745;'>▲ R$ {row['Ganho']:.2f}</span>", unsafe_allow_html=True)
                c3.markdown(f"<span style='color: #dc3545;'>▼ R$ {row['Gasto']:.2f}</span>", unsafe_allow_html=True)
                if c4.button("🗑️", key=f"del_{i}"):
                    df_dados = df_dados.drop(i).to_csv(arq_dados, index=False)
                    st.rerun()
    else:
        st.info("Ainda não existem dados. Comece lançando seus ganhos acima!")
else:
    tela_acesso()
