
""" ESCOLAS
Modulo para tratamento do arquivo ESCOLAS.csv
"""

import os
import pandas as pd
from glob import glob
from raw_data import constantes as CONST
from educ_utils import df_inep_utils as DIU
from vo import SetorCensitario

class EscolasVO:
    """
        Classe que possui metodos para gerar um dicionario com todas as escolas
        dos anos de pesquisa e um DataFrame com todas as escolas de 2015
    """
    cols_escola = [
                'CO_ENTIDADE',
                'IN_LOCAL_FUNC_PREDIO_ESCOLAR', 'TP_OCUPACAO_PREDIO_ESCOLAR',
                'IN_LOCAL_FUNC_SALAS_EMPRESA', 'IN_LOCAL_FUNC_SOCIOEDUCATIVO',
                'IN_LOCAL_FUNC_UNID_PRISIONAL','IN_LOCAL_FUNC_PRISIONAL_SOCIO',
                'IN_LOCAL_FUNC_TEMPLO_IGREJA','IN_LOCAL_FUNC_CASA_PROFESSOR',
                'IN_LOCAL_FUNC_GALPAO','IN_LOCAL_FUNC_SALAS_OUTRA_ESC',
                'IN_LOCAL_FUNC_OUTROS','IN_PREDIO_COMPARTILHADO',
                'IN_AGUA_FILTRADA','IN_AGUA_REDE_PUBLICA',
                'IN_AGUA_POCO_ARTESIANO','IN_AGUA_CACIMBA',
                'IN_AGUA_FONTE_RIO', 'IN_AGUA_INEXISTENTE',
                'IN_ENERGIA_REDE_PUBLICA', 'IN_ENERGIA_GERADOR',
                'IN_ENERGIA_OUTROS', 'IN_ENERGIA_INEXISTENTE',
                'IN_ESGOTO_REDE_PUBLICA','IN_ESGOTO_FOSSA',
                'IN_ESGOTO_INEXISTENTE','IN_LIXO_COLETA_PERIODICA',
                'IN_LIXO_QUEIMA','IN_LIXO_JOGA_OUTRA_AREA',
                'IN_LIXO_RECICLA','IN_LIXO_ENTERRA',
                'IN_LIXO_OUTROS','IN_SALA_DIRETORIA',
                'IN_SALA_PROFESSOR','IN_LABORATORIO_INFORMATICA',
                'IN_LABORATORIO_CIENCIAS','IN_SALA_ATENDIMENTO_ESPECIAL',
                'IN_QUADRA_ESPORTES_COBERTA','IN_QUADRA_ESPORTES_DESCOBERTA',
                'IN_QUADRA_ESPORTES','IN_COZINHA', 'IN_BIBLIOTECA','IN_SALA_LEITURA',
                'IN_BIBLIOTECA_SALA_LEITURA', 'IN_PARQUE_INFANTIL',
                'IN_BERCARIO', 'IN_BANHEIRO_FORA_PREDIO',
                'IN_BANHEIRO_DENTRO_PREDIO','IN_BANHEIRO_EI',
                'IN_BANHEIRO_PNE','IN_DEPENDENCIAS_PNE',
                'IN_SECRETARIA','IN_BANHEIRO_CHUVEIRO',
                'IN_REFEITORIO', 'IN_DESPENSA',
                'IN_ALMOXARIFADO', 'IN_AUDITORIO',
                'IN_PATIO_COBERTO', 'IN_PATIO_DESCOBERTO',
                'IN_ALOJAM_ALUNO', 'IN_ALOJAM_PROFESSOR',
                'IN_AREA_VERDE', 'IN_LAVANDERIA',
                'IN_DEPENDENCIAS_OUTRAS', 'NU_SALAS_EXISTENTES',
                'NU_SALAS_UTILIZADAS', 'IN_EQUIP_TV',
                'IN_EQUIP_VIDEOCASSETE', 'IN_EQUIP_DVD',
                'IN_EQUIP_PARABOLICA', 'IN_EQUIP_COPIADORA',
                'IN_EQUIP_RETROPROJETOR', 'IN_EQUIP_IMPRESSORA',
                'IN_EQUIP_IMPRESSORA_MULT','IN_EQUIP_SOM',
                'IN_EQUIP_MULTIMIDIA','IN_EQUIP_FAX',
                'IN_EQUIP_FOTO','IN_COMPUTADOR',
                'NU_COMPUTADOR','NU_COMP_ADMINISTRATIVO',
                'NU_COMP_ALUNO','IN_INTERNET',
                'IN_BANDA_LARGA','NU_FUNCIONARIOS',
                'IN_ALIMENTACAO','TP_AEE',
                'TP_ATIVIDADE_COMPLEMENTAR', 'IN_FUNDAMENTAL_CICLOS',
                'IN_MATERIAL_ESP_QUILOMBOLA', 'IN_MATERIAL_ESP_INDIGENA',
                'IN_MATERIAL_ESP_NAO_UTILIZA', 'IN_EDUCACAO_INDIGENA',
                'IN_BRASIL_ALFABETIZADO', 'IN_FINAL_SEMANA',
                'IN_FORMACAO_ALTERNANCIA'
            ]

    def __init__(self,dict_docentes : dict):
        self.dict_escolas = None
        self.df_escolas = None
        self.dict_docentes = dict_docentes

    def get_dict_escolas(self):
        #Retorna um dict cuja chave sao anos e os valores sao DataFrames
        if self.dict_escolas is None:
            self.dict_escolas = self.monta_dict_escolas()
        return self.dict_escolas

    def monta_dict_escolas(self) -> dict:
        #monta um dicionario com os anos como chave e com os DataFrames como valores
        return {a : self.filtra_escolas(self.carrega_csv_escolas(str(a)),int(a))
                    for a in CONST.ANOS_PESQUISA}
    def filtra_escolas(self, df : pd.DataFrame,ano : int) -> pd.DataFrame:
        #filtra o dataframe com as colunas corretas para cada ano
        if ano < 2015:
            return df.loc[(df.FK_COD_ESTADO == CONST.CO_UF_DISTRITO_FEDERAL)
                        & (df.ID_DEPENDENCIA_ADM == CONST.CO_ENTIDADE_ESTADUAL)]
        else:
            return df.loc[(df.CO_UF == CONST.CO_UF_DISTRITO_FEDERAL)
                        & (df.TP_DEPENDENCIA == CONST.CO_ENTIDADE_ESTADUAL)]

    def carrega_csv_escolas(self,ano : str)->pd.DataFrame:
        #carrega CSV das escolas do Distrito Federal
        arq_filtrado = ('%sESCOLAS_FILTRADAS_%s.csv' %(CONST.ARQ_PATH,ano))
        if os.path.exists(arq_filtrado):
            return  DIU.ajusta_colunas_int_df_inep(pd.read_csv(arq_filtrado,low_memory=False))
        else:
            arq_csv = ('%s%s/ESCOLAS.CSV' %(CONST.ARQ_PATH,ano))
            d = DIU.monta_df_inep(arq_csv)
            d.to_csv(arq_filtrado)
            return d



    def monta_features_escolas(self,fte : pd.DataFrame) -> pd.DataFrame:
        #cria novas features para o DataFrame de escolas
        fte['NU_PCT_SALAS_UTILIZADAS'] = fte.NU_SALAS_UTILIZADAS/fte.NU_SALAS_EXISTENTES
        cd = ['NU_SALAS_UTILIZADAS']
        fte['NU_PROP_FUNS_SALAS_UTZD'] = fte.NU_FUNCIONARIOS/fte.NU_SALAS_UTILIZADAS
        fte['NU_PROP_CPU_SALAS_UTZD'] = fte.NU_COMPUTADOR/fte.NU_SALAS_UTILIZADAS
        fte['NU_PRIM_ANO_CENSO'] = 0
        for a in CONST.ANOS_PESQUISA[:-1]:
            cp = 'CO_PESSOA_FISICA' if a >= 2015 else 'FK_COD_DOCENTE'
            ce = 'CO_ENTIDADE' if a >= 2015 else 'PK_COD_ENTIDADE'
            np = self.dict_docentes[a].loc[self.dict_docentes[a][ce].isin(self.get_dict_escolas()[a][ce].values)].groupby(ce)[[cp]].nunique().reset_index()
            np.columns = ['CO_ENTIDADE','qtd']
            fte[f'NU_TTL_PROF_{a}'] = fte.merge(np,on='CO_ENTIDADE',how='left')['qtd'].values
            fte.loc[fte.CO_ENTIDADE.isin(self.get_dict_escolas()[a][ce]) & fte.NU_PRIM_ANO_CENSO == 0,'NU_PRIM_ANO_CENSO'] = a

        fte['NU_DIF_QTD_DOCENTES_13_14'] = fte[f'NU_TTL_PROF_2013'] - fte[f'NU_TTL_PROF_2014']
        fte['NU_DIF_QTD_DOCENTES_14_15'] = fte[f'NU_TTL_PROF_2014'] - fte[f'NU_TTL_PROF_2015']
        fte['NU_PROP_PROF_FUNC_2015'] = fte.NU_TTL_PROF_2015 / fte.NU_FUNCIONARIOS
        return fte.drop(cd,axis=1)

    def monta_features_geo_escolas(self,df : pd.DataFrame) -> pd.DataFrame:
        #Criação de features a partir dos dados dos Setores Censitários

        #Agrupa setores censitários por escola
        dg = df.groupby('CO_ENTIDADE')
        b = dg[[col for col in df.columns if col.startswith('qtd_')]].sum()
        set_agp_esc = pd.DataFrame()
        #contagens
        set_agp_esc['NU_QTD_SETORES_CENSITARIOS'] = dg['CO_SETOR_CENSITARIO'].nunique()
        #medias
        set_agp_esc['NU_MEDIA_DISTANCIA_ESCOLA_SETOR'] = dg['DISTANCIA_SETOR_ENTIDADE'].mean()
        #medianas
        set_agp_esc['NU_MEDIANA_RENDA_MEDIA'] = dg['renda_media_dom'].median()
        set_agp_esc['NU_MEDIANA_QTD_DOMICILIOS'] = dg['qtd_domicilios'].median()
        set_agp_esc['NU_MEDIANA_QTD_PESSOAS'] = dg['qtd_pessoas'].median()
        #somas
        set_agp_esc['NU_SOMA_QTD_DOMICILIOS'] = b['qtd_domicilios']
        set_agp_esc['NU_SOMA_QTD_PESSOAS'] = b['qtd_pessoas']
        #proporcoes
        set_agp_esc['NU_PROP_DOM_ALUGADOS'] = b['qtd_alugados']/b['qtd_domicilios']
        set_agp_esc['NU_PROP_DOM_CEDIDOS'] = b['qtd_cedidos']/b['qtd_domicilios']
        set_agp_esc['NU_PROP_DOM_EM_AQUISICAO'] = b['qtd_em_aquisicao']/b['qtd_domicilios']
        set_agp_esc['NU_PROP_DOM_RENDA_PERCAPITA_ACIMA_5SM'] = b['qtd_dom_renda_max_per_mais_5sm']/b['qtd_domicilios']
        set_agp_esc['NU_PROP_DOM_RENDA_PERCAPITA_ABXO_1SM'] = b['qtd_dom_renda_per_cap_abx_1sm']/b['qtd_domicilios']
        set_agp_esc['NU_PROP_PSS_MULHERES'] = b['qtd_mulheres']/b['qtd_pessoas']
        set_agp_esc['NU_PROP_PSS_MULHERES_RSP'] = b['qtd_mulheres_resp']/b['qtd_pessoas']
        set_agp_esc['NU_PROP_PSS_ABXO_12ANOS'] = b['qtd_pss_abx_12']/b['qtd_pessoas']
        set_agp_esc['NU_PROP_PSS_ACIMA_65ANOS'] = b['qtd_pss_acima_65']/b['qtd_pessoas']
        set_agp_esc['NU_PROP_PSS_ACIMA_90ANOS'] = b['qtd_pss_acima_90']/b['qtd_pessoas']
        return set_agp_esc

    def monta_geo_df_escolas(self,df : pd.DataFrame) -> pd.DataFrame:
        geo_esc = DIU.ajusta_colunas_int_df_inep( pd.read_csv('%slclz_df/DADOS_ESCOLAS_PUBLICAS.csv' %CONST.CSV_PATH,index_col='CO_ENTIDADE'))
        df = df.merge(geo_esc.loc[geo_esc.PREC_BOA==1][['LAT','LONG']],
                                    left_on='CO_ENTIDADE',
                                    right_index=True)
        dsc = SetorCensitario.dados_setor_censitario(('%slclz_df/censo_df/dados/' %CONST.CSV_PATH),
                                     glob(('%slclz_df/censo_df/*.shp' %(CONST.CSV_PATH)))[0],
                                     df)
        #remove registros nulos
        dsc = self.monta_features_geo_escolas(dsc.dropna().drop_duplicates())
        #ajuste de tipos para otimizar o uso da memória
        for col in dsc.columns:
            if col.startswith('NU_MEDIA') or col.startswith('NU_PROP'):
                dsc[col] = dsc[col].astype(np.float16)
            else:
                dsc[col] = dsc[col].astype(np.int16)
        dsc.index = dsc.index.astype(np.int64)
        df = df.drop(['LAT','LONG'],axis=1).merge(dsc,left_index=True,right_index=True)
        return df

    def monta_df_escolas(self) -> pd.DataFrame:
        #monta o dataframe de escolas
        df_escolas = self.get_dict_escolas()[2015].copy()[EscolasVO.cols_escola].drop_duplicates()
        df_escolas = self.monta_features_escolas(df_escolas)
        df_escolas = self.monta_geo_df_escolas(df_escolas)
        return df_escolas.set_index('CO_ENTIDADE')

    def get_df_escolas(self) -> pd.DataFrame:
        #monta o dataframe caso seja necessario.
        if self.df_escolas is None:
            arq_filtrado = ('%sESCOLAS_MODELAGEM_DF.csv' %(CONST.ARQ_PATH))
            if os.path.exists(arq_filtrado):
                self.df_escolas = DIU.ajusta_colunas_int_df_inep(pd.read_csv(arq_filtrado,low_memory=False,index_col='CO_ENTIDADE'))
            else:
                self.df_escolas = self.monta_df_escolas()
        return self.df_escolas
