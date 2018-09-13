"""
    Modulo com a classe AlunosVO para processamento do arquivo MATRICULAS_XX.csv
"""

import numpy as np
import os
import pandas as pd

from vo.Docentes import DocentesVO
from vo.Escolas import EscolasVO
from raw_data import constantes as CONST
from educ_utils import df_inep_utils as DIU

class AlunosVO:
    """
        Classe com metodos para tratar o arquivo MATRICULAS_XX, onde XX é a
        região escolhida, e gerar um DataFrame de features dos alunos.
    """

    def __init__(self,regiao : str, docentes : DocentesVO, escolas : EscolasVO):
        self.regiao = regiao
        self.docentes = docentes
        self.escolas = escolas
        self.dict_matriculas = None
        self.dict_alunos = None
        self.df_features_alunos_15 = None

    def filtra_df_turmas(self, turmas_interesse : np.array,df : pd.DataFrame,ano : int) -> pd.DataFrame:
        #filtra de acordo com o ano
        if ano < 2015:
            return df.loc[df.PK_COD_TURMA.isin(turmas_interesse)]
        else:
            return df.loc[df.ID_TURMA.isin(turmas_interesse)]

    def load_matriculas(self,ano:str,turmas_interesse : np.array) -> pd.DataFrame:
        #carrega o csv das matriculas ou monta um DataFrame filtrado
        arq_filtrado = ('%MATRICULAS_FILTRADAS_%s.csv' %(CONST.ARQ_PATH,ano))
        if os.path.exists(arq_filtrado):
            return DIU.ajusta_colunas_int_df_inep(pd.read_csv(arq_filtrado,low_memory=False))
        else:
            a = DIU.monta_df_inep('%s%s/MATRICULA_%s.CSV' %(CONST.ARQ_PATH,ano,self.regiao))
            a = self.filtra_df_turmas(turmas_interesse,a,int(ano))
            a.to_csv(arq_filtrado)
            return a

    def monta_dict_matriculas(self) -> dict:
        #monta um dict cuja chave é o ano e os valores é um Dataframe com todas
        #as matrículas das escolas de interesse.
        turmas_interesse = self.docentes.get_dict_docentes()[2015]\
                            .loc[self.docentes.get_dict_docentes()[2015]\
                            .CO_ENTIDADE.isin(self.escolas.get_df_escolas().index)].ID_TURMA.unique()
        return {a : self.load_matriculas(str(a),turmas_interesse) for a in CONST.ANOS_PESQUISA}

    def get_dict_matriculas (self) -> dict:
        #retorna o dicionário preenchido
        if self.dict_matriculas is None:
            self.dict_matriculas = self.monta_dict_matriculas()
        return self.dict_matriculas

    def filtra_df_alunos(self, ano : int, df : pd.DataFrame, alunos_interesse : np.array) -> pd.DataFrame:
        #filtra os alunos de acordo com o ano.
        if ano < 2015:
            return df.loc[df.FK_COD_ALUNO.isin(alunos_interesse)]
        else:
            return df.loc[df.CO_PESSOA_FISICA.isin(alunos_interesse)]

    def load_alunos(self,ano : str,alunos_interesse : np.array) -> pd.DataFrame:
        #carrega o csv das alunos ou monta um DataFrame filtrado
        arq_filtrado = ('%ALUNOS_FILTRADOS_%s.csv' %(CONST.ARQ_PATH,ano))
        if os.path.exists(arq_filtrado):
            return DIU.ajusta_colunas_int_df_inep(pd.read_csv(arq_filtrado,low_memory=False))
        else:
            a = DIU.monta_df_inep('%s%s/MATRICULA_%s.CSV' %(CONST.ARQ_PATH,ano,self.regiao))
            a = self.filtra_df_alunos(alunos_interesse,a,int(ano))
            a.to_csv(arq_filtrado)
            return a

    def monta_dict_alunos(self) -> dict:
        #monta um dict cuja chave é o ano e o valor é um DataFrame com os dados
        #dos alunos que estudavam nas turmas do dict_matriculas de 2015.
        alunos_interesse = self.get_dict_matriculas()[2015].CO_PESSOA_FISICA.unique()
        return {a : self.load_alunos(str(a),alunos_interesse) for a in CONST.ANOS_PESQUISA}

    def get_dict_alunos(self) -> dict:
        if self.dict_alunos is None:
            self.dict_alunos = self.monta_dict_alunos()
        return self.dict_alunos

    def monta_features_alunos(aln15 : pd.DataFrame) -> pd.DataFrame:
        #Criação de features de alunos
        idd_max_etapa = {
            1  : 4, 2  : 6,  4  : 7, 5  : 8, 6  : 9, 7  : 10, 8  : 11, 9  : 12,
            10 : 13, 11 : 14, 14 : 7, 15 : 8, 16 : 9, 17 : 10, 18 : 11, 19 : 12,
            20 : 13, 21 : 14, 41 : 15, 25 : 16, 26 : 17, 27 : 18, 28 : 19,
            30 : 16, 31 : 17, 32 : 18, 33 : 19, 35 : 16, 36 : 17, 37 : 18, 38 : 19
        }
        cd = []
        aln15['IN_IDD_CORRETA'] = aln15.apply(lambda lin:
                                        lin['NU_IDADE_REFERENCIA'] <= idd_max_etapa[lin['TP_ETAPA_ENSINO']]
                                        if lin['TP_ETAPA_ENSINO'] in idd_max_etapa.keys()
                                              else 0,axis=1).astype(np.int8)
        cd.append('TP_ETAPA_ENSINO')
        aln15['IN_NATURAL_DF'] = (aln15.CO_UF_NASC == 53).astype(np.int8)
        cd.append('CO_UF_NASC')
        aln15['IN_RESIDE_DF'] = (aln15.CO_UF_END == 53).astype(np.int8)
        cd.append('CO_UF_END')
        aln15['NU_ANOS_TURMA'] = 1
        aln15['NU_ANOS_ESCOLA'] = 1
        aln15['NU_ANOS_REDE_PBC_DF'] = 1
        for k in anos_psq[:-2]:
            v = alunos_df[k]
            #display(f'{k} - {v.shape} / {aln15.loc[aln15.NU_ANOS_TURMA == 0].shape}')
            a = aln15[['CO_PESSOA_FISICA','ID_TURMA']].merge(v[['FK_COD_ALUNO','PK_COD_TURMA']],
                        left_on = ['CO_PESSOA_FISICA','ID_TURMA'],
                        right_on = ['FK_COD_ALUNO','PK_COD_TURMA'])[['CO_PESSOA_FISICA','ID_TURMA']]
            aln15.loc[(aln15.CO_PESSOA_FISICA.isin(a.CO_PESSOA_FISICA)) &
                      (aln15.NU_ANOS_TURMA == 1),'NU_ANOS_TURMA'] = 2015 - k

            a = aln15[['CO_PESSOA_FISICA','CO_ENTIDADE']].merge(v[['FK_COD_ALUNO','PK_COD_ENTIDADE']],
                        left_on = ['CO_PESSOA_FISICA','CO_ENTIDADE'],
                        right_on = ['FK_COD_ALUNO','PK_COD_ENTIDADE'])
            aln15.loc[(aln15.CO_PESSOA_FISICA.isin(a.CO_PESSOA_FISICA)) &
                      (aln15.NU_ANOS_ESCOLA == 1),'NU_ANOS_ESCOLA'] = 2015 - k

            aln15.loc[(aln15.CO_PESSOA_FISICA.isin(v.loc[v.ID_DEPENDENCIA_ADM_ESC == 2].FK_COD_ALUNO.values)) &
                      (aln15.NU_ANOS_REDE_PBC_DF == 1),'NU_ANOS_REDE_PBC_DF'] = 2015 - k

        aln15['NU_PROP_VIDA_ESCOLA'] = (aln15['NU_ANOS_ESCOLA']/aln15['NU_IDADE_REFERENCIA'].clip_lower(1))
        aln15['NU_PROP_VIDA_REDE_PBC'] = (aln15['NU_ANOS_REDE_PBC_DF']/aln15['NU_IDADE_REFERENCIA'].clip_lower(1))
        aln15['IN_MULHER'] = (aln15['TP_SEXO'] == 2).astype(np.int8)
        cd.append('TP_SEXO')
        aln15['TP_COR_RACA'] = aln15.TP_COR_RACA.astype(np.int8)
        aln15 = aln15.merge(pd.get_dummies(aln15.TP_COR_RACA.astype(np.int8),prefix='IN_TP_COR_RACA',dtype=np.int8),right_index=True,left_index=True)
        cd.append('TP_COR_RACA')
        aln15['TP_ETAPA_AGREGADA'] = aln15.TP_ETAPA_AGREGADA.fillna(0).astype(np.int8)
        aln15 = aln15.merge(pd.get_dummies(aln15.TP_ETAPA_AGREGADA,prefix='IN_TP_ETAPA_AGREGADA',dtype=np.int8),right_index=True,left_index=True)
        #1 - Educação Infantil (etapas 1 e 2)
        #2 - Anos Iniciais do Ensino Fundamental (etapas 4, 5, 6, 7, 14, 15, 16, 17 e 18)
        #3 - Anos Finais do Ensino Fundamental (etapas 8, 9, 10, 11, 19, 20, 21 e 41)
        #4 - Ensino Médio Propedêutico (etapas 25, 26, 27, 28 e 29)
        #5 - Ensino Médio - Normal/Magistério (etapas 35, 36, 37 e 38)
        #6 - Curso técnico integrado (Ensino Médio integrado - etapas 30, 31, 32, 33 e 34)
        #7 - Educação Profissional (etapas 39, 40 e 68)
        #8 - EJA - Ensino Fundamental (etapas 65, 69, 70 e 73)
        #9 - EJA - Ensino Médio (etapas 67, 71 e 74)

        aln15['IN_TP_ETAPA_AGREGADA_INFANTIL'] = (aln15.IN_TP_ETAPA_AGREGADA_1 +
                                               aln15.IN_TP_ETAPA_AGREGADA_2).astype(np.int8)
        aln15['IN_TP_ETAPA_AGREGADA_PROFSS'] = (aln15.IN_TP_ETAPA_AGREGADA_6 +
                                               aln15.IN_TP_ETAPA_AGREGADA_7).astype(np.int8)
        aln15['IN_TP_ETAPA_AGREGADA_EJA'] = (aln15.IN_TP_ETAPA_AGREGADA_8 +
                                               aln15.IN_TP_ETAPA_AGREGADA_9).astype(np.int8)
        cd.append('IN_TP_ETAPA_AGREGADA_1')
        cd.append('IN_TP_ETAPA_AGREGADA_2')
        cd.append('IN_TP_ETAPA_AGREGADA_6')
        cd.append('IN_TP_ETAPA_AGREGADA_7')
        cd.append('IN_TP_ETAPA_AGREGADA_8')
        cd.append('IN_TP_ETAPA_AGREGADA_9')
        cd.append('TP_ETAPA_AGREGADA')
        return aln15.drop(cd,axis=1)

    def monta_df_features_alunos15(self) -> pd.DataFrame:
        #monta um dataframe com features dos alunos matriculados em 2015
        cols_mtr = ['ID_MATRICULA','CO_PESSOA_FISICA',
                    'NU_IDADE_REFERENCIA','NU_DURACAO_TURMA',
                    'NU_DUR_ATIV_COMP_MESMA_REDE',
                    'NU_DUR_ATIV_COMP_OUTRAS_REDES',
                    'NU_DUR_AEE_MESMA_REDE',
                    'NU_DUR_AEE_OUTRAS_REDES',
                    'NU_DIAS_ATIVIDADE',
                    'TP_SEXO','TP_COR_RACA',
                    'CO_UF_NASC','CO_UF_END',
                    'TP_ZONA_RESIDENCIAL',
                    'IN_TRANSPORTE_PUBLICO',
                    'IN_TRANSP_VANS_KOMBI','IN_TRANSP_MICRO_ONIBUS',
                    'IN_TRANSP_ONIBUS','IN_TRANSP_BICICLETA',
                    'IN_TRANSP_TR_ANIMAL','IN_TRANSP_OUTRO_VEICULO',
                    'IN_TRANSP_EMBAR_ATE5','IN_TRANSP_EMBAR_5A15',
                    'IN_TRANSP_EMBAR_15A35','IN_TRANSP_EMBAR_35',
                    'IN_TRANSP_TREM_METRO','IN_NECESSIDADE_ESPECIAL',
                    'IN_CEGUEIRA','IN_BAIXA_VISAO',
                    'IN_SURDEZ','IN_DEF_AUDITIVA',
                    'IN_SURDOCEGUEIRA','IN_DEF_FISICA',
                    'IN_DEF_INTELECTUAL','IN_DEF_MULTIPLA',
                    'IN_AUTISMO','IN_SINDROME_ASPERGER',
                    'IN_SINDROME_RETT','IN_TRANSTORNO_DI',
                    'IN_SUPERDOTACAO','IN_RECURSO_LEDOR',
                    'IN_RECURSO_TRANSCRICAO','IN_RECURSO_INTERPRETE',
                    'IN_RECURSO_LIBRAS','IN_RECURSO_LABIAL',
                    'IN_RECURSO_BRAILLE','IN_RECURSO_AMPLIADA_16',
                    'IN_RECURSO_AMPLIADA_20','IN_RECURSO_AMPLIADA_24',
                    'IN_RECURSO_NENHUM',
                    'TP_MEDIACAO_DIDATICO_PEDAGO','IN_ESPECIAL_EXCLUSIVA',
                    'IN_REGULAR','IN_EJA',
                    'IN_PROFISSIONALIZANTE','TP_ETAPA_ENSINO',
                    'TP_ETAPA_AGREGADA','ID_TURMA', 'CO_ENTIDADE'
                    ]
        a = self.get_dict_alunos()[2015][cols_mtr].copy()
        indice = ['CO_PESSOA_FISICA','ID_TURMA','CO_ENTIDADE','ID_MATRICULA']
        return a.set_index(indice)


    def get_df_features_alunos_15(self):
        arq_features_alunos = ('%salunos_todas_ft.csv' %CONST.PATH_DF_CSV)
        if self.df_features_alunos_15 is None:
            if os.path.exists(arq_features_alunos):
                self.df_features_alunos_15 = DIU.ajusta_colunas_int_df_inep( pd.read_csv(arq_features_alunos,index_col=['CO_PESSOA_FISICA','ID_TURMA','CO_ENTIDADE','ID_MATRICULA']))
            else:
                self.df_features_alunos_15 = self.monta_df_features_alunos15()
                self.df_features_alunos_15.to_csv(arq_features_alunos)
        return self.df_features_alunos_15
