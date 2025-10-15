import streamlit as st
import pandas as pd
from io import BytesIO
from modules.data_processing import process_data
import unidecode
import plotly.express as px

import streamlit as st
import streamlit.components.v1 as components
import os
import signal
import tempfile




st.set_page_config(page_title="Realocação de Avaliadores", layout="wide")
st.title("📋 Programa de Realocação de Avaliadores")

def inicializar_session_state():
    defaults = {
        'avaliadores': None,
        'trabalhos': None,
        'contagem_area': None,
        'selecionado_para_atribuicao': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

inicializar_session_state()

if all(k in st.session_state and st.session_state[k] is not None for k in ['avaliadores', 'trabalhos', 'contagem_area']):
    st.write("✅ Avaliação pronta.")


# Upload
st.sidebar.header("🔄 Upload dos Arquivos")
avaliadores_file = st.sidebar.file_uploader("Carregar Avaliadores (.xlsx)", type=["xlsx"])
trabalhos_file = st.sidebar.file_uploader("Carregar Trabalhos Aprovados (.xlsx)", type=["xlsx"])

st.sidebar.markdown("---")
exibir_graficos = st.sidebar.checkbox("📊 Ativar Gerador de Gráficos")

max_trabalhos = st.sidebar.number_input("Qtd. máxima de trabalhos por avaliador", min_value=1, max_value=20, value=3)

selected_sheet = None
if trabalhos_file:
    xls = pd.ExcelFile(trabalhos_file)
    sheets = xls.sheet_names
    selected_sheet = st.sidebar.selectbox("Selecione a aba dos Trabalhos:", sheets)

if avaliadores_file and trabalhos_file and selected_sheet:
    st.success(f"Aba '{selected_sheet}' selecionada para os Trabalhos.")

    avaliadores_df = pd.read_excel(avaliadores_file)
    trabalhos_df = pd.read_excel(trabalhos_file, sheet_name=selected_sheet, skiprows=0)

    st.subheader("📑 Dados Carregados")
    st.write("**Avaliadores:**")
    st.dataframe(avaliadores_df)
    st.write(f"**Trabalhos Aprovados - Aba: {selected_sheet}**")
    st.dataframe(trabalhos_df)

    if st.button("🚀 Realocar Avaliadores"):
        avaliadores, trabalhos, contagem_area = process_data(avaliadores_df, trabalhos_df, max_trabalhos)

        st.session_state.avaliadores = avaliadores
        st.session_state.trabalhos = trabalhos
        st.session_state.contagem_area = contagem_area

        st.success("✅ Realocação concluída com sucesso!")

# Exibir os dados realocados
if st.session_state.avaliadores is not None:
    st.subheader("📈 Trabalhos Aprovados com Avaliadores")
    st.dataframe(st.session_state.trabalhos)

    st.subheader("📊 Avaliadores")
    st.dataframe(st.session_state.avaliadores)

    # Exibir total de trabalhos por área
    st.subheader("🗂️ Total de Trabalhos por Área")
    total_por_area = st.session_state.trabalhos.groupby('Área do conhecimento').size().reset_index(name='Total de Trabalhos')
    st.dataframe(total_por_area)

    # Exibir trabalhos sem avaliador
    st.subheader("📌 Resumo: Trabalhos sem Avaliador por Área")
    if st.session_state.contagem_area.empty:
        st.success("✅ Todos os trabalhos possuem avaliadores!")
    else:
        st.dataframe(st.session_state.contagem_area)

    # --- Pesquisa de avaliadores por área ---
    st.subheader("🔎 Buscar Avaliadores por Área do Conhecimento")
    area_pesquisa = st.text_input("Digite o nome da área para buscar avaliadores:")

    if area_pesquisa.strip():
        area_pesquisa_norm = unidecode.unidecode(area_pesquisa.strip().lower())

        def tem_relacao(area_avaliador):
            if pd.isna(area_avaliador):
                return False
            areas = str(area_avaliador).split(",")
            return any(
                area_pesquisa_norm in unidecode.unidecode(area.strip().lower())
                for area in areas
            )

        avaliadores_relacionados = st.session_state.avaliadores[
            st.session_state.avaliadores['Áreas possíveis de avaliações'].apply(tem_relacao)
        ]

        if not avaliadores_relacionados.empty:
            st.write(f"**Avaliadores relacionados à área '{area_pesquisa}':**")


            # Criar uma tabela customizada com botão
            for idx, avaliador in avaliadores_relacionados.iterrows():
                col1, col2, col3, col4 = st.columns([3, 3, 2, 1])

                col1.write(avaliador['Nome:'])
                col2.write(avaliador['Centro de Ensino/Setor'])
                col3.write(avaliador['QUANTIDADE_DE_TRABALHOS'])

                if col4.button("➕", key=f"add_{avaliador['Nome:']}"):
                    st.session_state.selecionado_para_atribuicao = avaliador['Nome:']
                    st.success(f"Avaliador {avaliador['Nome:']} selecionado para atribuição.")

            st.write("---")
            st.write("**Legenda da Tabela:**")
            st.markdown("""
            - **Nome:** Nome do Avaliador
            - **Centro:** Centro de Ensino/Setor
            - **Qtd Trabalhos:** Quantidade de Trabalhos atribuídos
            - **➕:** Botão para selecionar o avaliador
            """)

            if st.session_state.selecionado_para_atribuicao:

                st.markdown(f"### Selecionar Trabalho para: **{st.session_state.selecionado_para_atribuicao}**")

                avaliador_nome = st.session_state.selecionado_para_atribuicao.lower().strip()

                trabalhos_disponiveis = st.session_state.trabalhos[
                    (st.session_state.trabalhos['Área do conhecimento'].str.lower() == area_pesquisa_norm) &
                    (st.session_state.trabalhos['Avaliador'] == "Sem avaliador") &
                    (st.session_state.trabalhos['Orientador'].str.lower().str.strip() != avaliador_nome) &
                    (st.session_state.trabalhos['Nome'].str.lower().str.strip() != avaliador_nome)
                ]

                if trabalhos_disponiveis.empty:
                    st.warning("Não há trabalhos disponíveis nesta área para alocação manual.")
                else:
                    trabalho_opcao = st.selectbox(
                        "Selecione um trabalho para atribuir:",
                        options=trabalhos_disponiveis['Título']
                    )

                    if st.button("✅ Confirmar Atribuição"):
                        idx_trabalho = trabalhos_disponiveis[trabalhos_disponiveis['Título'] == trabalho_opcao].index[0]
                        idx_avaliador = st.session_state.avaliadores[
                            st.session_state.avaliadores['Nome:'] == st.session_state.selecionado_para_atribuicao
                        ].index[0]

                        st.session_state.trabalhos.at[idx_trabalho, 'Avaliador'] = st.session_state.selecionado_para_atribuicao
                        st.session_state.trabalhos.at[idx_trabalho, 'Centro de Ensino/Setor'] = st.session_state.avaliadores.at[idx_avaliador, 'Centro de Ensino/Setor']
                        st.session_state.avaliadores.at[idx_avaliador, 'QUANTIDADE_DE_TRABALHOS'] += 1

                        # Atualiza contagem de trabalhos sem avaliador
                        trabalhos_sem_avaliador = st.session_state.trabalhos[
                            st.session_state.trabalhos['Avaliador'] == "Sem avaliador"
                        ]
                        st.session_state.contagem_area = trabalhos_sem_avaliador.groupby('Área do conhecimento').size().reset_index(name='Quantidade')

                        st.session_state.selecionado_para_atribuicao = None

                        st.success(f"Trabalho '{trabalho_opcao}' atribuído com sucesso para {st.session_state.selecionado_para_atribuicao}!")
                        st.rerun()

        else:
            st.warning("Nenhum avaliador encontrado para esta área.")

    # Botão para download
    # output = BytesIO()
    # with pd.ExcelWriter(output, engine='openpyxl') as writer:
    #     st.session_state.avaliadores.to_excel(writer, sheet_name='Avaliadores', index=False)
    #     st.session_state.trabalhos.to_excel(writer, sheet_name='Trabalhos Aprovados', index=False)
    #     st.session_state.contagem_area.to_excel(writer, sheet_name='Trabalhos sem Avaliador', index=False)
    #     total_por_area.to_excel(writer, sheet_name='Total por Área', index=False)
    # output.seek(0)

    # st.download_button(
    #     label="📥 Baixar Resultado Excel",
    #     data=output,
    #     file_name='resultado_avaliadores.xlsx',
    #     mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    # )
    # Salvar o arquivo original dos trabalhos em disco temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(trabalhos_file.getbuffer())
        tmp_path = tmp.name

    # Adicionar novas abas ao arquivo original
    with pd.ExcelWriter(tmp_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        st.session_state.avaliadores.to_excel(writer, sheet_name='Avaliadores', index=False)
        st.session_state.trabalhos.to_excel(writer, sheet_name='Trabalhos Aprovados', index=False)
        st.session_state.contagem_area.to_excel(writer, sheet_name='Trabalhos sem Avaliador', index=False)
        total_por_area.to_excel(writer, sheet_name='Total por Área', index=False)

    # Ler o arquivo final para BytesIO
    with open(tmp_path, "rb") as f:
        output = BytesIO(f.read())

    st.download_button(
        label="📥 Baixar Resultado Excel",
        data=output,
        file_name='resultado_avaliadores.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    if exibir_graficos and st.session_state.avaliadores is not None:
        st.header("📊 Gerador de Gráficos")

        aba_dados = st.selectbox("Selecione o conjunto de dados para o gráfico:", 
                                ['Avaliadores', 'Trabalhos Aprovados', 'Trabalhos sem Avaliador', 'Total por Área'])

        if aba_dados == 'Avaliadores':
            df_grafico = st.session_state.avaliadores
        elif aba_dados == 'Trabalhos Aprovados':
            df_grafico = st.session_state.trabalhos
        elif aba_dados == 'Trabalhos sem Avaliador':
            df_grafico = st.session_state.contagem_area
        else:
            df_grafico = total_por_area

        st.write("📄 Visualização dos dados selecionados:")
        st.dataframe(df_grafico.head())

        colunas_disponiveis = df_grafico.columns.tolist()
        col_x = st.selectbox("🧩 Coluna para o eixo X:", colunas_disponiveis)
        col_y = st.selectbox("🧩 Coluna para o eixo Y:", colunas_disponiveis)

        tipo_grafico = st.selectbox("📈 Tipo de gráfico:", ["Barras", "Linha", "Pizza", "Dispersão"])
        tema = st.selectbox("🎨 Tema do gráfico:", ["plotly", "ggplot2", "seaborn", "simple_white", "plotly_dark"])

        if st.button("🚀 Gerar Gráfico"):
            fig = None
            if tipo_grafico == "Barras":
                fig = px.bar(df_grafico, x=col_x, y=col_y, template=tema)
            elif tipo_grafico == "Linha":
                fig = px.line(df_grafico, x=col_x, y=col_y, template=tema)
            elif tipo_grafico == "Pizza":
                fig = px.pie(df_grafico, names=col_x, values=col_y, template=tema)
            elif tipo_grafico == "Dispersão":
                fig = px.scatter(df_grafico, x=col_x, y=col_y, template=tema)

            if fig:
                st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Por favor, carregue os dois arquivos e escolha uma aba para iniciar.")

