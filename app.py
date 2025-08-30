# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date
import os
import io

# --- Configuração da página e injeção de estilo ---
st.set_page_config(
    page_title="Dashboard de RH",
    page_icon="📊",
    layout="wide"
)

# Injeção de CSS para a fonte Inter e estilo customizado (Tema Claro)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #333333;
            background-color: #f0f2f6;
        }

        .stMetric {
            background-color: #ffffff;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
            padding: 1rem;
            transition: transform 0.2s, box-shadow 0.2s;
            text-align: center;
        }
        
        .stMetric:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2), 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        .stRadio > label {
            font-weight: 600;
        }

        .stMultiSelect, .stSlider {
            border-radius: 0.5rem;
        }

        .stApp {
            background-color: #f0f2f6;
        }
    </style>
""", unsafe_allow_html=True)

# --- Caminho padrão do arquivo Excel ---
DEFAULT_EXCEL_PATH = "dados_rh.xlsx"

# --- Função para criar um arquivo Excel de exemplo ---
def create_sample_excel():
    """
    Cria e retorna um arquivo Excel de exemplo em memória.
    """
    data = {
        'Nome Completo': ['Ana Silva', 'Bruno Costa', 'Carlos Mendes', 'Diana Souza', 'Eduarda Pereira', 'Fábio Gomes', 'Gabriel Rocha', 'Helena Martins', 'Isabela Lima', 'João Almeida'],
        'Area': ['Vendas', 'Marketing', 'Vendas', 'Engenharia', 'Vendas', 'Marketing', 'Engenharia', 'Vendas', 'Engenharia', 'Vendas'],
        'Nivel': ['Pleno', 'Senior', 'Junior', 'Pleno', 'Senior', 'Pleno', 'Junior', 'Pleno', 'Senior', 'Junior'],
        'Cargo': ['Vendedor', 'Analista Mkt', 'Vendedor', 'Engenheiro', 'Gerente Vendas', 'Analista Mkt', 'Engenheiro', 'Vendedor', 'Engenheiro', 'Vendedor'],
        'Sexo': ['Feminino', 'Masculino', 'Masculino', 'Feminino', 'Feminino', 'Masculino', 'Masculino', 'Feminino', 'Feminino', 'Masculino'],
        'Data de Nascimento': ['1990-05-15', '1985-11-20', '1998-03-01', '1992-09-22', '1988-07-10', '1995-02-28', '2000-04-12', '1993-08-05', '1987-12-30', '1999-06-18'],
        'Data de Contratacao': ['2018-01-10', '2015-06-25', '2021-09-15', '2019-03-20', '2014-05-01', '2017-08-08', '2022-01-30', '2018-02-14', '2013-10-17', '2020-04-05'],
        'Data de Demissao': [np.nan, '2023-01-20', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, '2023-11-10', np.nan],
        'Salario Base': [4500, 8500, 3200, 7000, 12000, 6000, 4000, 4800, 9500, 3500],
        'Impostos': [1200, 2500, 850, 2100, 3500, 1500, 1000, 1300, 2800, 900],
        'Beneficios': [500, 700, 300, 600, 800, 550, 450, 420, 750, 350],
        'VT': [150, 200, 150, 180, 200, 150, 150, 160, 200, 150],
        'VR': [300, 400, 250, 350, 400, 300, 280, 320, 400, 280],
        'Avaliacao do Funcionario': [8.5, 9.2, 7.8, 9.1, 9.5, 8.0, 7.5, 8.8, 9.0, 8.2]
    }
    df_sample = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_sample.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output

# --- Função para carregar e pré-processar os dados com cache ---
@st.cache_data
def load_data(file_path=None, uploaded_file=None):
    """
    Carrega, limpa e pré-processa os dados de um arquivo Excel.
    Se nenhum arquivo for encontrado/enviado, usa dados de exemplo.
    """
    df = None
    
    # Prioridade 1: Arquivo enviado pelo usuário
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        except Exception as e:
            st.error(f"Erro ao ler o arquivo enviado. Verifique se o formato está correto. Erro: {e}")
            return None
    # Prioridade 2: Caminho padrão
    elif file_path and os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            st.error(f"Erro ao ler o arquivo do caminho padrão. Verifique se o arquivo não está corrompido ou em uso. Erro: {e}")
            return None
    # Prioridade 3: Dados de exemplo (fallback)
    else:
        st.warning("Arquivo de dados não encontrado. Usando dados de exemplo para demonstração.")
        df = pd.read_excel(create_sample_excel(), engine='openpyxl')


    # --- Pré-processamento dos dados ---
    # Renomear colunas para facilitar o uso (opcional, mas boa prática)
    df.columns = [col.replace(' ', '_').replace('.', '').replace('ç', 'c').lower() for col in df.columns]

    # Padronizar colunas de texto (strip e maiúsculas)
    for col in ['nome_completo', 'area', 'cargo', 'nivel', 'sexo', 'status']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    # Converter colunas de data
    for col in ['data_de_nascimento', 'data_de_contratacao', 'data_de_demissao']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Normalizar valores de "Sexo"
    if 'sexo' in df.columns:
        df['sexo'] = df['sexo'].replace({'MASCULINO': 'M', 'FEMININO': 'F'})

    # Garantir que colunas numéricas sejam floats e substituir nulos por 0.0
    for col in ['salario_base', 'impostos', 'beneficios', 'vt', 'vr', 'avaliacao_do_funcionario']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    # --- Criar colunas derivadas ---
    # Idade
    if 'data_de_contratacao' in df.columns:
        today = date.today()
        df['idade'] = df['data_de_contratacao'].apply(
            lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day)) if pd.notna(x) else np.nan
        )

    # Função para calcular a diferença em meses de forma confiável
    def calculate_months_diff(d1, d2):
        if pd.isna(d1) or pd.isna(d2):
            return 0
        return (d2.year - d1.year) * 12 + d2.month - d1.month
    
    # Tempo de Casa (meses) - Corrigido o erro
    if 'data_de_contratacao' in df.columns:
        df['tempo_de_casa_meses'] = df['data_de_contratacao'].apply(
            lambda x: calculate_months_diff(x, pd.to_datetime('now'))
        )
        df['tempo_de_casa_meses'] = df['tempo_de_casa_meses'].apply(lambda x: int(x) if pd.notna(x) else 0)

    # Status (Ativo/Desligado)
    if 'data_de_demissao' in df.columns:
        df['status'] = df['data_de_demissao'].apply(lambda x: 'DESLIGADO' if pd.notna(x) else 'ATIVO')

    # Custo Total Mensal
    custo_cols = ['salario_base', 'impostos', 'beneficios', 'vt', 'vr']
    df['custo_total_mensal'] = df[custo_cols].sum(axis=1)

    return df

# --- Título principal e subtítulo ---
st.title("📊 Dashboard de Recursos Humanos")
st.markdown("Uma visão geral da força de trabalho da empresa.")

# --- Interface de carregamento de dados ---
st.sidebar.header("Carregamento de Dados")
upload_option = st.sidebar.radio(
    "Escolha uma opção de carregamento:",
    ("Fazer upload do arquivo", "Usar arquivo padrão")
)

# Carrega os dados uma vez e armazena em uma variável de estado
if 'original_df' not in st.session_state:
    st.session_state.original_df = load_data()

df_filtered = st.session_state.original_df.copy()

if upload_option == "Fazer upload do arquivo":
    uploaded_file = st.sidebar.file_uploader("Escolha um arquivo Excel (.xlsx)", type="xlsx")
    if uploaded_file:
        df_filtered = load_data(uploaded_file=uploaded_file)
        st.session_state.original_df = df_filtered
elif not os.path.exists(DEFAULT_EXCEL_PATH):
    st.sidebar.info("Arquivo padrão não encontrado. Por favor, baixe o arquivo de exemplo ou faça um upload.")
    
    # Botão de download para o arquivo de exemplo
    excel_sample = create_sample_excel()
    st.sidebar.download_button(
        label="📥 Baixar arquivo de exemplo",
        data=excel_sample,
        file_name="dados_rh_exemplo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.sidebar.markdown("---")

# Se o DataFrame for nulo, significa que houve um erro grave no carregamento
if df_filtered is None or df_filtered.empty:
    st.error("Não foi possível carregar os dados. Verifique o arquivo e tente novamente.")
    st.stop()
    
# --- Barra lateral com filtros ---
st.sidebar.header("Filtros")

# Filtro por Nome Completo
nome_completo_search = st.sidebar.text_input("Buscar por Nome Completo:")
if nome_completo_search:
    df_filtered = df_filtered[df_filtered['nome_completo'].str.contains(nome_completo_search.upper())]

# Multi-select para categorias (agora usando o DataFrame original para as opções)
if 'area' in st.session_state.original_df.columns:
    areas = st.sidebar.multiselect("Área", options=st.session_state.original_df['area'].unique(), default=st.session_state.original_df['area'].unique())
    if areas: # Aplicar filtro apenas se houver seleção
        df_filtered = df_filtered[df_filtered['area'].isin(areas)]
if 'nivel' in st.session_state.original_df.columns:
    niveis = st.sidebar.multiselect("Nível", options=st.session_state.original_df['nivel'].unique(), default=st.session_state.original_df['nivel'].unique())
    if niveis: # Aplicar filtro apenas se houver seleção
        df_filtered = df_filtered[df_filtered['nivel'].isin(niveis)]
if 'cargo' in st.session_state.original_df.columns:
    cargos = st.sidebar.multiselect("Cargo", options=st.session_state.original_df['cargo'].unique(), default=st.session_state.original_df['cargo'].unique())
    if cargos: # Aplicar filtro apenas se houver seleção
        df_filtered = df_filtered[df_filtered['cargo'].isin(cargos)]
if 'sexo' in st.session_state.original_df.columns:
    sexos = st.sidebar.multiselect("Sexo", options=st.session_state.original_df['sexo'].unique(), default=st.session_state.original_df['sexo'].unique())
    if sexos: # Aplicar filtro apenas se houver seleção
        df_filtered = df_filtered[df_filtered['sexo'].isin(sexos)]
if 'status' in st.session_state.original_df.columns:
    status = st.sidebar.multiselect("Status", options=st.session_state.original_df['status'].unique(), default=st.session_state.original_df['status'].unique())
    if status: # Aplicar filtro apenas se houver seleção
        df_filtered = df_filtered[df_filtered['status'].isin(status)]

# Filtros por faixa de valores (sliders)
if 'idade' in st.session_state.original_df.columns and not st.session_state.original_df['idade'].isnull().all():
    min_idade = int(st.session_state.original_df['idade'].min())
    max_idade = int(st.session_state.original_df['idade'].max())
    idade_range = st.sidebar.slider("Faixa de Idade", min_idade, max_idade, (min_idade, max_idade))
    df_filtered = df_filtered[(df_filtered['idade'] >= idade_range[0]) & (df_filtered['idade'] <= idade_range[1])]

if 'salario_base' in st.session_state.original_df.columns and st.session_state.original_df['salario_base'].max() > 0:
    min_salario, max_salario = float(st.session_state.original_df['salario_base'].min()), float(st.session_state.original_df['salario_base'].max())
    salario_range = st.sidebar.slider("Faixa Salarial (R$)", min_salario, max_salario, (min_salario, max_salario))
    df_filtered = df_filtered[(df_filtered['salario_base'] >= salario_range[0]) & (df_filtered['salario_base'] <= salario_range[1])]

# Filtros por data
if 'data_de_contratacao' in st.session_state.original_df.columns and not st.session_state.original_df['data_de_contratacao'].isnull().all():
    min_contratacao = st.session_state.original_df['data_de_contratacao'].min().to_pydatetime()
    max_contratacao = st.session_state.original_df['data_de_contratacao'].max().to_pydatetime()
    contratacao_range = st.sidebar.slider(
        "Período de Contratação",
        min_value=min_contratacao,
        max_value=max_contratacao,
        value=(min_contratacao, max_contratacao),
        format="YYYY-MM-DD"
    )
    df_filtered = df_filtered[(df_filtered['data_de_contratacao'] >= pd.to_datetime(contratacao_range[0])) & (df_filtered['data_de_contratacao'] <= pd.to_datetime(contratacao_range[1]))]
    
if 'data_de_demissao' in st.session_state.original_df.columns and not st.session_state.original_df['data_de_demissao'].isnull().all():
    min_demissao = st.session_state.original_df['data_de_demissao'].min().to_pydatetime()
    max_demissao = st.session_state.original_df['data_de_demissao'].max().to_pydatetime()
    demissao_range = st.sidebar.slider(
        "Período de Demissão",
        min_value=min_demissao,
        max_value=max_demissao,
        value=(min_demissao, max_demissao),
        format="YYYY-MM-DD"
    )
    df_filtered = df_filtered[(df_filtered['data_de_demissao'] >= pd.to_datetime(demissao_range[0])) & (df_filtered['data_de_demissao'] <= pd.to_datetime(demissao_range[1]))]

# --- Verificação de dados após os filtros ---
if df_filtered.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados. Por favor, ajuste os filtros.")
    st.stop()

# --- Seção de KPIs principais ---
st.header("Indicadores Chave de Performance (KPIs)")
kpi_cols = st.columns(4)

# Headcount Ativo
ativo_df = df_filtered[df_filtered['status'] == 'ATIVO']
headcount_ativo = len(ativo_df)
kpi_cols[0].metric(label="Headcount Ativo", value=headcount_ativo)

# Desligados
desligados_df = df_filtered[df_filtered['status'] == 'DESLIGADO']
desligados = len(desligados_df)
kpi_cols[1].metric(label="Desligados", value=desligados)

# Folha de Pagamento
folha_pagamento = ativo_df['salario_base'].sum()
kpi_cols[2].metric(label="Folha de Pagamento", value=f"R$ {folha_pagamento:,.2f}")

# Custo Total
custo_total = ativo_df['custo_total_mensal'].sum()
kpi_cols[3].metric(label="Custo Total Mensal", value=f"R$ {custo_total:,.2f}")

st.markdown("---")

# --- Seção de KPIs de médias ---
st.header("Médias Gerais")
avg_kpi_cols = st.columns(3)

# Idade Média
if 'idade' in ativo_df.columns and not ativo_df['idade'].isnull().all():
    idade_media = ativo_df['idade'].mean()
    avg_kpi_cols[0].metric(label="Idade Média", value=f"{idade_media:.1f} anos")
else:
    avg_kpi_cols[0].metric(label="Idade Média", value="N/A")

# Tempo Médio de Casa
if 'tempo_de_casa_meses' in ativo_df.columns and not ativo_df['tempo_de_casa_meses'].isnull().all():
    tempo_medio_casa = ativo_df['tempo_de_casa_meses'].mean()
    avg_kpi_cols[1].metric(label="Tempo Médio de Casa", value=f"{tempo_medio_casa:.1f} meses")
else:
    avg_kpi_cols[1].metric(label="Tempo Médio de Casa", value="N/A")

# Avaliação Média do Funcionário
if 'avaliacao_do_funcionario' in ativo_df.columns and not ativo_df['avaliacao_do_funcionario'].isnull().all():
    avaliacao_media = ativo_df['avaliacao_do_funcionario'].mean()
    avg_kpi_cols[2].metric(label="Avaliação Média", value=f"{avaliacao_media:.2f}")
else:
    avg_kpi_cols[2].warning("Coluna 'Avaliação' não encontrada.")

st.markdown("---")

# --- Seção de Visualizações Gráficas ---
st.header("Visualizações Gráficas")
graficos_cols = st.columns(2)

# Distribuição de Idade (Histograma)
if 'idade' in df_filtered.columns:
    fig_idade = px.histogram(df_filtered.dropna(subset=['idade']), x="idade", nbins=20, title="Distribuição de Idade",
                             labels={'idade': 'Idade (anos)'}, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_idade.update_layout(bargap=0.1, template="plotly_white")
    graficos_cols[0].plotly_chart(fig_idade, use_container_width=True)

# Distribuição de Salário Base (Boxplot)
if 'salario_base' in df_filtered.columns:
    fig_salario = px.box(df_filtered.dropna(subset=['salario_base']), y="salario_base", title="Distribuição de Salário Base",
                         labels={'salario_base': 'Salário Base (R$)'}, color_discrete_sequence=px.colors.qualitative.Pastel, template="plotly_white")
    fig_salario.update_yaxes(tickprefix="R$ ")
    graficos_cols[1].plotly_chart(fig_salario, use_container_width=True)

# Funcionários por Área (Gráfico de Barras)
if 'area' in df_filtered.columns:
    area_counts = df_filtered['area'].value_counts().reset_index()
    area_counts.columns = ['Área', 'Número de Funcionários']
    fig_area = px.bar(area_counts, x="Área", y="Número de Funcionários", title="Funcionários por Área",
                      text="Número de Funcionários", color_discrete_sequence=px.colors.qualitative.Pastel, template="plotly_white")
    graficos_cols = st.columns(2)
    graficos_cols[0].plotly_chart(fig_area, use_container_width=True)

# Funcionários por Status (Pizza/Donut Chart)
if 'status' in df_filtered.columns:
    status_counts = df_filtered['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Número de Funcionários']
    fig_status = px.pie(status_counts, values="Número de Funcionários", names="Status",
                        title="Distribuição por Status", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel, template="plotly_white")
    graficos_cols[1].plotly_chart(fig_status, use_container_width=True)

# Evolução do headcount por mês de contratação (Linha)
if 'data_de_contratacao' in df_filtered.columns:
    df_evolucao = df_filtered.sort_values('data_de_contratacao').copy()
    df_evolucao['mes_ano_contratacao'] = df_evolucao['data_de_contratacao'].dt.to_period('M').astype(str)
    df_evolucao['headcount'] = df_evolucao.groupby('mes_ano_contratacao').cumcount() + 1
    
    fig_evolucao = px.line(df_evolucao, x="mes_ano_contratacao", y="headcount", title="Evolução do Headcount por Contratação",
                           labels={'mes_ano_contratacao': 'Mês/Ano de Contratação', 'headcount': 'Headcount Acumulado'}, color_discrete_sequence=px.colors.qualitative.Pastel, template="plotly_white")
    st.plotly_chart(fig_evolucao, use_container_width=True)

# --- Tabela final ---
st.header("Dados Filtrados")
st.dataframe(df_filtered)
