# -*- coding: utf-8 -*-
"""Docentes

Modulo com a classe Docentes

"""

import pandas as pd
import os.path

from raw_data import constantes as CONST
from educ_utils import df_inep_utils as DIU

class DocentesVO:
    """
        Classe que trata o arquivo DOCENTES_XX.csv onde XX é a regiao passada
        no metodo init.

        Processa o arquivo gerando:
            dict de docentes | escola | turma
            dict dos professores
    """



    def __init__ (self,regiao : str):
        self.regiao = regiao
        self.dict_docentes = None

    def filtra_docentes(self, df : pd.DataFrame,ano : int) -> pd.DataFrame:
        #filtra o dataframe com as colunas corretas para cada ano
        if ano <= 2009:
            return df.loc[(df.FK_COD_ESTADO == CONST.CO_UF_DISTRITO_FEDERAL)
                            & (df.ID_DEPENDENCIA_ADM == CONST.CO_ENTIDADE_ESTADUAL)]
        elif ano < 2015:
            return df.loc[(df.FK_COD_ESTADO == CONST.CO_UF_DISTRITO_FEDERAL)
                        & (df.ID_TIPO_CONTRATACAO == CONST.CO_CONTRATACAO_CONCURSO)
                        & (df.ID_DEPENDENCIA_ADM == CONST.CO_ENTIDADE_ESTADUAL)]
        else:
            return df.loc[(df.CO_UF == CONST.CO_UF_DISTRITO_FEDERAL)
                        & (df.TP_TIPO_CONTRATACAO == CONST.CO_CONTRATACAO_CONCURSO)
                        & (df.TP_DEPENDENCIA == CONST.CO_ENTIDADE_ESTADUAL)]

    def load_arquivo_docentes(self,ano : str) -> pd.DataFrame:
        #verifica qual arquivo deve ser carregado
        arq_filtrado = ('%sDOCENTES_FILTRADOS_%s.csv' %(CONST.ARQ_PATH,ano))
        if os.path.exists(arq_filtrado):
            return  DIU.ajusta_colunas_int_df_inep(pd.read_csv(arq_filtrado,low_memory=False))
        else:
            arq_csv = ('%s%s/DOCENTES_%s.CSV' %(CONST.ARQ_PATH,ano,self.regiao))
            d = DIU.monta_df_inep(arq_csv)
            d.to_csv(arq_filtrado)
            return d

    def load_dict_docentes(self) -> dict:
        #preenche o dicionario com um DataFrame para cada ano
        return {a :  self.filtra_docentes(self.load_arquivo_docentes(str(a)),int(a))
                                            for a in CONST.ANOS_PESQUISA}

    def get_dict_docentes(self) -> dict:
        #retorna o dicionario preenchendo caso esteja vazio.
        if not self.dict_docentes:
            self.dict_docentes = self.load_dict_docentes()
        return self.dict_docentes
