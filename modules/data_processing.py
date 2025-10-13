import pandas as pd
import re
import numpy as np
from unidecode import unidecode
from io import BytesIO
import random

def process_data(avaliadores, trabalhos_aprovados, maximo):
    # trabalhos_aprovados = trabalhos_aprovados.loc[trabalhos_aprovados['Resultado'] == 'APROVADA']
    print("Colunas do DataFrame trabalhos_aprovados:")
    print(trabalhos_aprovados.columns.tolist())
    trabalhos_aprovados = trabalhos_aprovados[['Nome', 'Título',"CPF","Email", 'Área do conhecimento', 'Centro de ensino',"Orientador","Trilha","Dia","Horário"]]
    
    trabalhos_aprovados['Avaliador']="Sem avaliador"
    trabalhos_aprovados["Centro de Ensino/Setor"]=""
    trabalhos_aprovados['Área do conhecimento'] = trabalhos_aprovados['Área do conhecimento'].apply(lambda x: unidecode(x))



    avaliadores = avaliadores[['Nome:','Áreas possíveis de avaliações',"E-mail","Centro de Ensino/Setor"]]
    avaliadores['QUANTIDADE_DE_TRABALHOS'] = 0
    avaliadores['Quantidade de Áreas'] = avaliadores['Áreas possíveis de avaliações'].str.count(',') + 1



    quantidade_trabalhos_por_area =trabalhos_aprovados.groupby('Área do conhecimento').size().reset_index(name='Quantidade de Trabalhos')
    quantidade_trabalhos_por_area['Possíveis Avaliadores'] = ''
    quantidade_trabalhos_por_area['Quantidade de avaliadores por área'] = 0
    quantidade_trabalhos_por_area['Quantidade por avaliadores'] = 0

    for _, row in quantidade_trabalhos_por_area.iterrows():

        area_conhecimento = row['Área do conhecimento']
        avaliadores_correspondentes = avaliadores[
            avaliadores['Áreas possíveis de avaliações'].apply(
                lambda value: any(unidecode(area_conhecimento.strip().lower()) == unidecode(part.strip().lower()) for part in re.split(',|-', value))
            )
        ]

        lista_das_pociscoes_dos_avaliadores = list(avaliadores_correspondentes.index)

        lista_das_pociscoes_dos_trabalhos = list(trabalhos_aprovados[trabalhos_aprovados['Área do conhecimento']==area_conhecimento].index)

        if len(lista_das_pociscoes_dos_avaliadores) !=0:
            condicao=(trabalhos_aprovados['Área do conhecimento'].apply(unidecode) == unidecode(area_conhecimento))#verifica se é a mesma área

            quantidade_de_avaliadores = len(lista_das_pociscoes_dos_avaliadores)
            quantidade_de_trabalho_da_area_conhecimento = len(trabalhos_aprovados[condicao])
            media = quantidade_de_trabalho_da_area_conhecimento//quantidade_de_avaliadores
            resto = quantidade_de_trabalho_da_area_conhecimento - (media *  quantidade_de_avaliadores)
            trabalho_inicio=0
            sobra_de_trabalhos_atribuitos=0

            for index_avaliador in range(len(lista_das_pociscoes_dos_avaliadores)):
                nome_avaliador = avaliadores.iloc[lista_das_pociscoes_dos_avaliadores[index_avaliador]]["Nome:"]
                centro_avaliador = avaliadores.iloc[lista_das_pociscoes_dos_avaliadores[index_avaliador]]["Centro de Ensino/Setor"]
                #  trabalhos_aprovados["Centro de Ensino/Setor"]
                cont_atribuido=0
                sobra_de_trabalhos_atribuitos=0
                trabalhos_para_avaliar_nao_foi_orientador = trabalhos_aprovados[
                    (
                        trabalhos_aprovados['Orientador'].str.strip().str.lower() != nome_avaliador.strip().lower()
                        ) & (
                        trabalhos_aprovados['Nome'].str.strip().str.lower() != nome_avaliador.strip().lower()
                        ) & (trabalhos_aprovados['Avaliador'] == "Sem avaliador")]
                
                lista_das_pociscoes_dos_trabalhos_nao_foi_orientador = list(
                trabalhos_para_avaliar_nao_foi_orientador[
                trabalhos_para_avaliar_nao_foi_orientador['Área do conhecimento']==area_conhecimento].index
                )
                
                intersection = list(set(lista_das_pociscoes_dos_trabalhos).intersection(set(lista_das_pociscoes_dos_trabalhos_nao_foi_orientador)))
                
                while True:
                    if (trabalho_inicio > len(intersection)):
                        trabalho_inicio=0
                        break
                    total_de_trabalhos_atribuitos_ao_avaliador = avaliadores.loc[
                        avaliadores['Nome:']==avaliadores.iloc[
                            lista_das_pociscoes_dos_avaliadores[index_avaliador]]["Nome:"],
                        'QUANTIDADE_DE_TRABALHOS'].values[0]
                    
                    
                    
                    if int(total_de_trabalhos_atribuitos_ao_avaliador) >= int(maximo):
                        
                        trabalho_inicio=0
                        sobra_de_trabalhos_atribuitos = media - cont_atribuido
                        if sobra_de_trabalhos_atribuitos > 0:
                            resto+=sobra_de_trabalhos_atribuitos
                        break

                    if cont_atribuido >= media:
                        trabalho_inicio=0
                        # if (resto > 0) and (len(intersection) >0):
                        #     trabalhos_aprovados.loc[intersection[trabalho_inicio], 'Avaliador'] = nome_avaliador
                        #     trabalhos_aprovados.loc[intersection[trabalho_inicio], 'Centro de Ensino/Setor']=centro_avaliador
                        #     avaliadores.loc[
                        #         avaliadores['Nome:']==avaliadores.loc[lista_das_pociscoes_dos_avaliadores[index_avaliador],"Nome:"],'QUANTIDADE_DE_TRABALHOS'
                        #         ] +=1
                            
                        #     trabalho_inicio+=1
                        #     cont_atribuido+=1
                        #     resto-=1
                        if (resto > 0) and (trabalho_inicio < len(intersection)):

                            trabalhos_aprovados.loc[intersection[trabalho_inicio], 'Avaliador'] = nome_avaliador
                            trabalhos_aprovados.loc[intersection[trabalho_inicio], 'Centro de Ensino/Setor'] = centro_avaliador
                            avaliadores.loc[
                                avaliadores['Nome:'] == avaliadores.loc[lista_das_pociscoes_dos_avaliadores[index_avaliador], "Nome:"],
                                'QUANTIDADE_DE_TRABALHOS'
                            ] += 1

                            trabalho_inicio += 1
                            cont_atribuido += 1
                            resto -= 1
                        
                        break
                    if trabalho_inicio >= len(intersection):
                        break
                    trabalhos_aprovados.loc[intersection[trabalho_inicio], 'Avaliador'] = nome_avaliador
                    trabalhos_aprovados.loc[intersection[trabalho_inicio], 'Centro de Ensino/Setor']=centro_avaliador
                    avaliadores.loc[
                        avaliadores['Nome:']==avaliadores.loc[lista_das_pociscoes_dos_avaliadores[index_avaliador],"Nome:"],'QUANTIDADE_DE_TRABALHOS'
                        ] +=1
                    
                    trabalho_inicio+=1
                    cont_atribuido+=1


            trabalho_inicio=0
            sobra_de_trabalhos_atribuitos=0
            for index_avaliador in range(len(lista_das_pociscoes_dos_avaliadores)):
                nome_avaliador = avaliadores.iloc[lista_das_pociscoes_dos_avaliadores[index_avaliador]]["Nome:"]
                centro_avaliador = avaliadores.iloc[lista_das_pociscoes_dos_avaliadores[index_avaliador]]["Centro de Ensino/Setor"]
                cont_atribuido=0
                sobra_de_trabalhos_atribuitos=0
                trabalhos_para_avaliar_nao_foi_orientador = trabalhos_aprovados[
                    (trabalhos_aprovados['Orientador'] != nome_avaliador)
                    & (
                        trabalhos_aprovados['Nome'].str.strip().str.lower() != nome_avaliador.strip().lower()
                        ) & (trabalhos_aprovados['Avaliador'] == "Sem avaliador")]
                lista_das_pociscoes_dos_trabalhos_nao_foi_orientador = list(
                    trabalhos_para_avaliar_nao_foi_orientador[trabalhos_para_avaliar_nao_foi_orientador['Área do conhecimento']==area_conhecimento].index
                    )
                
                intersection = list(set(lista_das_pociscoes_dos_trabalhos).intersection(set(lista_das_pociscoes_dos_trabalhos_nao_foi_orientador)))
                if len(intersection) == 0:
                    break

                while ((trabalho_inicio < len(intersection)) ):
                    total_de_trabalhos_atribuitos_ao_avaliador = avaliadores.loc[avaliadores['Nome:']==avaliadores.iloc[lista_das_pociscoes_dos_avaliadores[index_avaliador]]["Nome:"],'QUANTIDADE_DE_TRABALHOS'].values[0]

                    if total_de_trabalhos_atribuitos_ao_avaliador >= int(maximo):
                        break
                    if trabalho_inicio >= len(intersection):
                        break

                    trabalhos_aprovados.loc[intersection[trabalho_inicio], 'Avaliador'] = nome_avaliador
                    trabalhos_aprovados.loc[intersection[trabalho_inicio], 'Centro de Ensino/Setor']=centro_avaliador
                    avaliadores.loc[
                        avaliadores['Nome:']==avaliadores.loc[lista_das_pociscoes_dos_avaliadores[index_avaliador],"Nome:"],'QUANTIDADE_DE_TRABALHOS'
                        ] +=1
                    
                    trabalho_inicio+=1
                    cont_atribuido+=1


    trabalhos_sem_avaliador = trabalhos_aprovados[trabalhos_aprovados['Avaliador'] == "Sem avaliador"]
    contagem_por_area = trabalhos_sem_avaliador.groupby('Área do conhecimento').size().reset_index(name='Quantidade')
    return avaliadores, trabalhos_aprovados, contagem_por_area

def salvar_resultados(avaliadores, trabalhos_aprovados, contagem_por_area):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        avaliadores.to_excel(writer, sheet_name='Avaliadores', index=False)
        trabalhos_aprovados.to_excel(writer, sheet_name='Trabalhos Aprovados', index=False)
        contagem_por_area.to_excel(writer, sheet_name='Área sem Avaliador', index=False)

    output.seek(0)
    return output
