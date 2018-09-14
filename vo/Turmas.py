""" TURMAS

Arquivo com a classe TurmasVO que processa o arquivo TURMAS.CSV

"""

import pandas as pd
import os
import numpy as np

from raw_data import constantes as CONST
from educ_utils import df_inep_utils as DIU
from vo.Escolas import EscolasVO
from vo.Alunos import AlunosVO

class TurmasVO:
    """
        Classe que fornece metodos para processamento do arquivo TURMAS.CSV e
        criacao de um DataFrame com as features das turmas.
    """

    def __init__ (self,escolas : EscolasVO):
        self.df_turmas15 = None
        self.escolas = escolas
        self.df_features_turmas15 = None


    def monta_df_turmas(self) -> pd.DataFrame:
        t15 = DIU.monta_df_inep('%s2015/TURMAS.CSV' %(CONST.ARQ_PATH))
        return t15.loc[t15.CO_ENTIDADE.isin(self.escolas.get_df_escolas().index.values)]

    def get_df_turmas15(self) -> pd.DataFrame:
        if self.df_turmas15 is None:
            self.df_turmas15 = self.monta_df_turmas()
        return self.df_turmas15

    def monta_turno(self,hora : int) -> int:
        #retorna de acordo com o periodo: matutino, vespertino e noturno.
        if hora < 12:
            return 0
        elif hora < 18:
            return 1
        else:
            return 2

    def monta_df_features_turmas15(self):
        #monta o DataFrame com as features
        cols_turma = ['ID_TURMA','TX_HR_INICIAL','NU_DURACAO_TURMA',
                      'NU_MATRICULAS','IN_REGULAR','IN_EJA','IN_PROFISSIONALIZANTE',
                     'NU_DIAS_ATIVIDADE'] +[col for col in self.get_df_turmas15().columns if col.startswith('IN_DISC_')]
        turmas = self.get_df_turmas15()[cols_turma].copy().set_index('ID_TURMA')
        cols_drop = []
        turmas['CO_TURNO'] = pd.Categorical(turmas.TX_HR_INICIAL.apply(self.monta_turno))
        turmas = turmas.merge(
                    pd.get_dummies(turmas.CO_TURNO, prefix='IN_TURNO'),
                    right_index=True,
                    left_index=True)
        cols_drop.append('TX_HR_INICIAL')
        cols_drop.append('CO_TURNO')
        turmas['NU_QTD_DISCIPLINAS'] = np.sum(turmas[
                        [col for col in self.get_df_turmas15().columns
                            if col.startswith('IN_DISC_')]].fillna(0),axis=1)
        cols_drop.extend([col for col in self.get_df_turmas15().columns
                            if col.startswith('IN_DISC_')])
        return turmas.drop(cols_drop,axis=1)

    def get_df_features_turmas15(self):
        if self.df_features_turmas15 is None:
            arq_ft_turmas = CONST.PATH_DF_CSV + 'features_turmas15.csv'
            if os.path.exists(arq_ft_turmas):
                a = pd.read_csv(arq_ft_turmas,low_memory=False)
                print(a.shape)
                print(a.head())
                self.df_features_turmas15 = DIU.ajusta_colunas_int_df_inep(a)
            else:
                self.df_features_turmas15 = self.monta_df_features_turmas15()
                self.df_features_turmas15.to_csv(arq_ft_turmas)
            self.df_features_turmas15.set_index('ID_TURMA')
        return self.df_features_turmas15
