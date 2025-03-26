# ==============================
# 📦 DASHBOARD PROVIMENTO 07 – CORREGEDORIA NRC 2025
# ==============================

import streamlit as st
import pandas as pd
import altair as alt

# ========== CONFIGURAÇÃO GLOBAL ==========
st.set_page_config(
    page_title="📊 Registro Civil - NRC 2025",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CABEÇALHO ==========
col1, col2 = st.columns([6, 1])
with col1:
    st.title("📊 Relatório Registro Civil – Unidade Interligada PROV 07")
    st.subheader("📄 Dados Obrigatórios – PROV 07/2021 – CGJ")
with col2:
    st.image("https://raw.githubusercontent.com/jesusmjunior/dashboard-registro-civil-prov07/main/CGX.png", width=120)

# ========== AVISO ==========
st.warning("🚨 UNIDADE INTERLIGADA! Preencha os dados do Provimento 07/2021.", icon="⚠️")
st.markdown("[📝 Acessar Formulário Obrigatório](https://forms.gle/vETZAjAStN3F9YHx9)")

# ========== EXPANDER - SOBRE ==========
with st.expander("ℹ️ Sobre o Provimento 07/2021"):
    st.markdown("""
    A instalação de unidades interligadas em hospitais é obrigatória. Os registros devem ser enviados mensalmente até o dia 10 via [Formulário Online](https://forms.gle/vETZAjAStN3F9YHx9).

    **Desembargador José Jorge Figueiredo dos Anjos**  
    *Corregedor-Geral da Justiça (Biênio 2024-2026)*
    """)

# ========== CONFIGURAR LINKS DAS PLANILHAS ==========
sheet_ids = {
    "base": "1k_aWceBCN_V0VaRJa1Jw42t6hfrER4T4bE2fS88mLDI",
    "subregistro": "1UD1B9_5_zwd_QD0drE1fo3AokpE6EDnYTCwywrGkD-Y",
    "csv_publicado": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtKiqlosLL5_CJgGom7BlWpFYExhLTQEjQT_Pdgnv3uEYMlWPpsSeaxfjqy0IxTluVlKSpcZ1IoXQY/pub?output=csv"
}

def build_url(sheet_id, aba):
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba}"

sheet_urls = {
    "CAIXA DE ENTRADA": build_url(sheet_ids["base"], "Respostas ao formulário 2"),
    "QUANTITATIVO (2024 E 2025)": build_url(sheet_ids["base"], "QUANTITATIVO (2024 E 2025)"),
    "FILTRADOS": build_url(sheet_ids["base"], "(NÃO ALTERE OS FILTROS OU DADOS)"),
    "RECEBIMENTO POR MUNICÍPIO": build_url(sheet_ids["base"], "Página11"),
    "STATUS DE RECEBIMENTO": build_url(sheet_ids["base"], "STATUS DE RECEBIMENTO"),
    "GRAPH SITE": build_url(sheet_ids["base"], "GRAPH SITE"),
    "DADOS ORGANIZADOS": build_url(sheet_ids["base"], "DADOS ORGANIZADOS"),
    "SUB-REGISTRO": build_url(sheet_ids["subregistro"], "subregistro"),
    "DADOS COMPLETOS": sheet_ids["csv_publicado"],
    "ANÁLISE DE STATUS": build_url(sheet_ids["base"], "Respostas ao formulário 2")
}

# ========== CACHE DE CARREGAMENTO ==========
@st.cache_data(ttl=3600)
def carregar_planilha(aba):
    df = pd.read_csv(sheet_urls[aba], low_memory=False, dtype=str)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    return df, "Planilha Pública Online (CSV)"

# ========== SIDEBAR ==========
st.sidebar.header("📂 Selecione os Dados")
aba_selecionada = st.sidebar.radio("Aba:", list(sheet_urls.keys()))

df, origem = carregar_planilha(aba_selecionada)
st.caption(f"Fonte dos dados: {origem}")

# ========== FILTROS ==========
if aba_selecionada in [
    "CAIXA DE ENTRADA", "FILTRADOS", "RECEBIMENTO POR MUNICÍPIO",
    "STATUS DE RECEBIMENTO", "DADOS ORGANIZADOS", "SUB-REGISTRO", "DADOS COMPLETOS"
]:
    if "MUNICÍPIO" in df.columns:
        municipio = st.sidebar.selectbox("Filtrar por Município:", ["Todos"] + sorted(df["MUNICÍPIO"].dropna().unique()))
        if municipio != "Todos":
            df = df[df["MUNICÍPIO"] == municipio]

    if "Ano" in df.columns:
        ano = st.sidebar.selectbox("Filtrar por Ano:", ["Todos"] + sorted(df["Ano"].dropna().unique()))
        if ano != "Todos":
            df = df[df["Ano"] == ano]

# ========== ANÁLISE DE STATUS ==========
if aba_selecionada == "ANÁLISE DE STATUS":
    st.header("📊 Análise de Cumprimento")

    df["Mês"] = pd.to_numeric(df["Mês"], errors="coerce")
    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
    municipios_unicos = df["MUNICÍPIO"].dropna().unique()

    municipio_sel = st.sidebar.selectbox("Município:", municipios_unicos)
    df_mun = df[df["MUNICÍPIO"] == municipio_sel]

    total_envios = df_mun.shape[0]
    meses_enviados = df_mun["Mês"].nunique()
    pendentes = 12 - meses_enviados

    st.metric("📩 Total de Envios", total_envios)
    st.metric("📅 Meses Pendentes", pendentes)

    duplicados = df_mun[df_mun.duplicated(subset=["Mês", "Ano"], keep=False)]
    if not duplicados.empty:
        st.warning("⚠️ Registros duplicados detectados")
        st.dataframe(duplicados)

    graf = df_mun.groupby("Mês").size().reset_index(name="Total")
    chart = alt.Chart(graf).mark_bar().encode(
        x=alt.X("Mês:O"), y=alt.Y("Total:Q"), tooltip=["Mês", "Total"]
    ).properties(title="Envios por Mês")
    st.altair_chart(chart, use_container_width=True)

    st.subheader("📄 Registros Detalhados")
    st.dataframe(df_mun, use_container_width=True)

else:
    st.dataframe(df, height=1000, use_container_width=True)

# ========== DOWNLOAD ==========
csv_completo = df.to_csv(index=False, encoding="utf-8-sig")
st.sidebar.download_button("📥 Baixar CSV", data=csv_completo, file_name=f"{aba_selecionada}.csv", mime="text/csv")
