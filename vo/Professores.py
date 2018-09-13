
import pandas as pd
import numpy as np
import os

from raw_data import constantes as CONST
from educ_utils import df_inep_utils as DIU

class ProfessoresVO:

    """"
        Classe que a partir do dicionario de docentes tem metodos para montar um
        DataFrame de professores.
    """

    cols_prof = [
    'CO_PESSOA_FISICA','NU_IDADE_REFERENCIA','TP_SEXO',
    'TP_COR_RACA','CO_UF_NASC',
    'CO_UF_END',
    'TP_ZONA_RESIDENCIAL','IN_POSSUI_NEC_ESPECIAL',
    'IN_CEGUEIRA','IN_BAIXA_VISAO',
    'IN_SURDEZ','IN_DEF_AUDITIVA',
    'IN_SURDOCEGUEIRA','IN_DEF_FISICA',
    'IN_DEF_INTELECTUAL','IN_DEF_MULTIPLA',
    'TP_ESCOLARIDADE',
    'TP_SITUACAO_CURSO_1','CO_AREA_CURSO_1',
    'IN_LICENCIATURA_1','IN_COM_PEDAGOGICA_1','TP_TIPO_IES_1',
    'TP_SITUACAO_CURSO_2','CO_AREA_CURSO_2',
    'IN_LICENCIATURA_2',
    'IN_COM_PEDAGOGICA_2','TP_TIPO_IES_2',
    'TP_SITUACAO_CURSO_3','CO_AREA_CURSO_3','IN_LICENCIATURA_3',
    'IN_COM_PEDAGOGICA_3','TP_TIPO_IES_3',
    'IN_ESPECIALIZACAO','IN_MESTRADO',
    'IN_DOUTORADO','IN_POS_NENHUM'
    ]


    def __init__ (self):
        self.df_prof_15 = None

    def get_df_prof_15(self,dict_docente : dict) -> pd.DataFrame:
        #retorna os professores de 2015 filtrados a partir do dicionario de docentes
        #caso ainda nao tenha sido preenchido manda montar.
        if self.df_prof_15 is None:
            arq_filtrado = CONST.ARQ_PATH + 'PROFESSORES_FILTRADOS.csv'
            if os.path.exists(arq_filtrado):
                self.df_prof_15 = \
                    DIU.ajusta_colunas_int_df_inep\
                        (
                            pd.read_csv(arq_filtrado,index_col='CO_PESSOA_FISICA')
                        )
            else:
                self.df_prof_15 = \
                    self.monta_features_professores \
                        (
                            self.filtra_df_docente(dict_docente),
                            dict_docente
                        )
                self.df_prof_15.to_csv(arq_filtrado)
            #preenche o nulos
            for c in self.df_prof_15.columns:
                if not c.startswith('NU'):
                    self.df_prof_15[c] = self.df_prof_15[c].fillna(0)
        return self.df_prof_15

    def filtra_df_docente(self,dict_docente : dict) -> pd.DataFrame:
        #monta um DF cuja chave e o Codigo do Professor e que os professores deram
        #aula em 2015 E 2017 E (2013 ou 2014)
        df = dict_docente[2015][ProfessoresVO.cols_prof].drop_duplicates()
        return df.loc[
                       (
                          (df.CO_PESSOA_FISICA.isin(dict_docente[2013].FK_COD_DOCENTE))
                        | (df.CO_PESSOA_FISICA.isin(dict_docente[2014].FK_COD_DOCENTE))
                       )
                     & (df.CO_PESSOA_FISICA.isin(dict_docente[2017].CO_PESSOA_FISICA))
                      ]

    def monta_nu_cursos_area (self,cd_area : int,df : pd.DataFrame):
        #soma as graduacoes em determinada area
        return (df.CO_AREA_CURSO_1.fillna(0).astype(np.int8) == np.int8(cd_area)).astype(np.int8) \
              +(df.CO_AREA_CURSO_2.fillna(0).astype(np.int8) == np.int8(cd_area)).astype(np.int8) \
              +(df.CO_AREA_CURSO_3.fillna(0).astype(np.int8) == np.int8(cd_area)).astype(np.int8)

    def monta_features_professores(self,df : pd.DataFrame,dict_docente : dict) -> pd.DataFrame:
        #cria features para o Dataframe de professores
        cols_drop = []
        df['IN_MORA_ZONA_URBANA'] = (df.TP_ZONA_RESIDENCIAL == 1).astype(np.int8)
        cols_drop.append('TP_ZONA_RESIDENCIAL')
        df['IN_NASCEU_DF'] = \
            (df.CO_UF_NASC == CONST.CO_UF_DISTRITO_FEDERAL).astype(np.int8)
        cols_drop.append('CO_UF_NASC')
        df['IN_MORA_DF'] = \
            (df.CO_UF_END == CONST.CO_UF_DISTRITO_FEDERAL).astype(np.int8)
        cols_drop.append('CO_UF_END')
        df['IN_MULHER'] = (df.TP_SEXO == 2).astype(np.int8)
        cols_drop.append('TP_SEXO')
        df['NU_QTD_GRAD'] = \
            (df.TP_SITUACAO_CURSO_1 == 1).astype(np.int8) \
          + (df.TP_SITUACAO_CURSO_2 == 1).astype(np.int8) \
          + (df.TP_SITUACAO_CURSO_3 == 1).astype(np.int8)
        cols_drop.append('TP_SITUACAO_CURSO_1')
        cols_drop.append('TP_SITUACAO_CURSO_2')
        cols_drop.append('TP_SITUACAO_CURSO_3')
        df['NU_QTD_GRAD_PBC'] = \
            (df.TP_TIPO_IES_1 == 1).astype(np.int8) \
          + (df.TP_TIPO_IES_2 == 1).astype(np.int8) \
          + (df.TP_TIPO_IES_3 == 1).astype(np.int8)
        df['NU_QTD_GRAD_PRIV'] = \
            (df.TP_TIPO_IES_1 == 2).astype(np.int8) \
          + (df.TP_TIPO_IES_2 == 2).astype(np.int8) \
          + (df.TP_TIPO_IES_3 == 2).astype(np.int8)
        cols_drop.append('TP_TIPO_IES_1')
        cols_drop.append('TP_TIPO_IES_2')
        cols_drop.append('TP_TIPO_IES_3')
        df['NU_QTD_LICENCIATURA'] = \
            (df.IN_LICENCIATURA_1 == 1).astype(np.int8) \
          + (df.IN_LICENCIATURA_2 == 1).astype(np.int8) \
          + (df.IN_LICENCIATURA_3 == 1).astype(np.int8)
        cols_drop.append('IN_LICENCIATURA_1')
        cols_drop.append('IN_LICENCIATURA_2')
        cols_drop.append('IN_LICENCIATURA_3')
        df['NU_QTD_COM_PEDAGOGICA'] = \
            (df.IN_COM_PEDAGOGICA_1 == 1).astype(np.int8) \
          + (df.IN_COM_PEDAGOGICA_2 == 1).astype(np.int8) \
          + (df.IN_COM_PEDAGOGICA_3 == 1).astype(np.int8)
        cols_drop.append('IN_COM_PEDAGOGICA_1')
        cols_drop.append('IN_COM_PEDAGOGICA_2')
        cols_drop.append('IN_COM_PEDAGOGICA_3')
        for a in CONST.ANOS_PESQUISA:
            if a < 2014:
                df['IN_PROF_%s' %str(a)] = df.CO_PESSOA_FISICA.isin(dict_docente[a].FK_COD_DOCENTE.values)
        df['NU_ANO_PRIM_CENSO'] = \
            df.apply(lambda x: \
                         2007 if x['IN_PROF_2007'] == 1 \
                         else \
                         2009 if x['IN_PROF_2009'] == 1 \
                         else
                         2011 if x['IN_PROF_2011'] == 1 \
                         else
                         2013 if x['IN_PROF_2013'] == 1 \
                         else 2014 \
                         ,axis=1)
        cols_drop.append('IN_PROF_2007')
        cols_drop.append('IN_PROF_2009')
        cols_drop.append('IN_PROF_2011')
        cols_drop.append('IN_PROF_2013')
        df['NU_GRAD_AREA_EDUCACAO']    = \
                    pd.Series(self.monta_nu_cursos_area(1,df))
        df['NU_GRAD_AREA_HUMANIDADES'] = \
                    pd.Series(self.monta_nu_cursos_area(2,df))
        df['NU_GRAD_AREA_SOCIAIS']  = \
                    pd.Series(self.monta_nu_cursos_area(3,df))
        df['NU_GRAD_AREA_MATEMATICA']  = \
                    pd.Series(self.monta_nu_cursos_area(4,df))
        df['NU_GRAD_AREA_ENGENHARIA']  = \
                    pd.Series(self.monta_nu_cursos_area(5,df))
        df['NU_GRAD_AREA_AGRICULTURA'] = \
                    pd.Series(self.monta_nu_cursos_area(6,df))
        df['NU_GRAD_AREA_SERVICOS']    = \
                    pd.Series(self.monta_nu_cursos_area(7,df))
        df['NU_GRAD_AREA_SAUDE']       = \
                    pd.Series(self.monta_nu_cursos_area(8,df))
        df['NU_GRAD_AREA_OUTROS']      = \
                    pd.Series(self.monta_nu_cursos_area(9,df))
        cols_drop.append('CO_AREA_CURSO_1')
        cols_drop.append('CO_AREA_CURSO_2')
        cols_drop.append('CO_AREA_CURSO_3')
        df = df.merge(
                        pd.get_dummies(
                            df.TP_COR_RACA,
                            prefix='TP_COR_RACA',
                            dtype=np.int8
                          ),
                        right_index=True,
                        left_index=True
                    )
        cols_drop.append('TP_COR_RACA')
        for a in CONST.ANOS_PESQUISA[:-1]:
            df['NU_QTD_TURMAS_INFANT_%s' %(str(a))] = \
                    df.merge \
                        ( \
                           ProfessoresVO.monta_por_tip_serie(dict_docente[a],'INFANT',a,nivel_escola=False),
                           on='CO_PESSOA_FISICA',
                           how='left',
                           suffixes=('','_y')
                        )[f'NU_QTD_TURMAS_INFANT_{a}'].fillna(0)
            df['NU_QTD_TURMAS_MEDIO_%s' %(str(a))] = \
                    df.merge \
                        (\
                           ProfessoresVO.monta_por_tip_serie(dict_docente[a],'MEDIO',a,nivel_escola=False),
                           on='CO_PESSOA_FISICA',
                           how='left',
                           suffixes=('','_y')
                        )[f'NU_QTD_TURMAS_MEDIO_{a}'].fillna(0)
        cols_drop.extend([c for c in df.columns if c.endswith('_y')])

        a,b = pd.qcut(
                     df.NU_IDADE_REFERENCIA.unique(),
                     5,
                     retbins=True,
                     labels=['Muito jovem','Jovem','Meia idade', 'Idoso','Melhor idade']
                    )
        df['CLSC_QTL_NU_IDADE_REFERENCIA'] = \
            pd.cut(
                    df.NU_IDADE_REFERENCIA,
                    bins=b,
                    labels=False,
                    include_lowest=True
                  )
        df.set_index('CO_PESSOA_FISICA',inplace=True)
        df['NU_QTD_ESCOLAS_2015'] = \
            dict_docente[2015].groupby('CO_PESSOA_FISICA')['CO_ENTIDADE'].nunique()
        df.drop(cols_drop,axis=1,inplace=True)
        return df


    def monta_por_tip_serie(df : pd.DataFrame,tip,ano : int,nivel_escola=True):
        #Conta quantas turmas ha por tipo.
        qtds = None
        series = {
            'INFANT' : [1,2,3],
            'MEDIO' : list(range(25,39))
        }
        cols_base = []
        if ano < 2015:
            cols_base = ['FK_COD_DOCENTE','PK_COD_ENTIDADE'] if nivel_escola else ['FK_COD_DOCENTE']
            qtds = df.loc[df.FK_COD_ETAPA_ENSINO.isin(series[tip])].groupby(cols_base)[['PK_COD_TURMA']].nunique()
        else:
            cols_base = ['CO_PESSOA_FISICA','CO_ENTIDADE'] if nivel_escola else ['CO_PESSOA_FISICA']
            qtds = df.loc[df.TP_ETAPA_ENSINO.isin(series[tip])].groupby(cols_base)[['ID_TURMA']].nunique()

        cols_base = ['CO_PESSOA_FISICA','CO_ENTIDADE'] if nivel_escola else ['CO_PESSOA_FISICA']
        qtds.reset_index(inplace=True)
        qtds.columns =  cols_base + ['NU_QTD_TURMAS_%s_%s' %(tip,str(ano))]
        return qtds
