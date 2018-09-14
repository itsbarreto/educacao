import pandas as pd
import numpy as np
from tqdm import tqdm
from IPython.core.display import display, HTML
from matplotlib import pyplot as plt
import seaborn as sns
def carrega_arquivo_inep(arq,cols=None):
    return pd.read_csv(arq,encoding='latin1',low_memory=False, sep='|',usecols=cols)

#reduz o tamanho para economizar memoria
def ajusta_colunas_int_df_inep(df, vai_printar_cols = False):
    ls_itips = [np.int8,np.int16,np.int32,np.int64]
    ls_ftips = [np.float16,np.float32,np.float64]
    for c in df.columns:
        try:
            if c.startswith('IN_') or c.startswith('ID_'):
                m = int(max(df[c].values))
                try:
                    for t in ls_itips:
                        if m < np.iinfo(t).max():
                            df[c] = df[c].astype(t)
                    break;
                except:
                    pass
            if df[c].dtype in ls_ftips:
                m = df[c].max()
                for t in ls_ftips:
                    if m < np.finfo(t).max:
                        df[c] = df[c].astype(t)
                        break;
            elif df[c].dtype in ls_itips:
                m = df[c].max()
                for t in ls_itips:
                    if m < np.iinfo(t).max:
                        df[c] = df[c].astype(t)
                        break;
        except Exception as e:
            pass
        if vai_printar_cols:
            print(f'{c}: {df[c].dtype}')
    return df


def monta_df_inep(arq):
    df = carrega_arquivo_inep(arq)
    df = df.fillna(-1)
    df = ajusta_colunas_int_df_inep(df)
    return df.replace(-1,np.nan)



def monta_por_tip_ensino(df,tip,dcr,ano):
    qtds = None
    if ano < 2015:
        qtds = df.loc[df.FK_COD_MOD_ENSINO == tip].groupby(['FK_COD_DOCENTE','PK_COD_ENTIDADE'])[['PK_COD_TURMA']].nunique()
    elif tip == 1:
        qtds = df.groupby(['CO_PESSOA_FISICA','CO_ENTIDADE'])[['IN_REGULAR']].sum()
    elif tip == 3:
        qtds = df.groupby(['CO_PESSOA_FISICA','CO_ENTIDADE'])[['IN_EJA']].sum()
    qtds.reset_index(inplace=True)
    qtds.columns = ['CO_PESSOA_FISICA','CO_ENTIDADE',f'NU_QTD_TURMAS_{dcr}_{ano}']
    return qtds

def monta_por_tip_serie(df,tip,ano,nivel_escola=True):
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
    qtds.columns =  cols_base + [f'NU_QTD_TURMAS_{tip}_{ano}']
    return qtds
