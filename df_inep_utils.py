import pandas as pd
import numpy as np
from tqdm import tqdm

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

def monta_df_docente(arq):
    df = carrega_arquivo_inep(arq)
    df = df.fillna(-1)
    df = ajusta_colunas_int_df_inep(df)
    return df.replace(-1,np.nan)

#monta um dataframe cuja cada linha e um professor
def monta_df_professores(df):
    col_chave = list(df.columns)[1]
    a = df.groupby(col_chave)
    dfa = pd.DataFrame(index=df[col_chave].unique())
    for i,c in tqdm(enumerate(df.columns)):
        if i in range(2,87):
            dfa[c] = a[c].max()
    cols_mun = [c for c in dfa.columns if c in ['CO_MUNICIPIO_NASC','FK_COD_MUNICIPIO_DEND']][0]

    dfa['IN_CIDADE_NATAL'] = dfa[cols_mun] == dfa[cols_mun]
    dfa.IN_CIDADE_NATAL = dfa.IN_CIDADE_NATAL.astype(np.int8)
    pref_col_sit_curso = ''
    for c in dfa.columns:
        if 'TP_SITUACAO_CURSO_' in c:
            pref_col_sit_curso ='TP_SITUACAO_CURSO'
            break
        elif 'ID_SITUACAO_CURSO_' in c:
            pref_col_sit_curso ='ID_SITUACAO_CURSO'
            break

    dfa['NUM_TTL_GRAD'] = (df[f'{pref_col_sit_curso}_1'] == 1).astype(np.int8) + (dfa[f'{pref_col_sit_curso}_2'] == 1).astype(np.int8) + (dfa[f'{pref_col_sit_curso}_3'] == 1).astype(np.int8)
    dfa['NUM_QTD_ESCOLAS'] = df.groupby(col_chave)['PK_COD_ENTIDADE'].nunique().fillna(0)
    dfa['NUM_QTD_TURMAS'] = df.groupby(col_chave)['PK_COD_ENTIDADE'].count().fillna(0)

    dfa = ajusta_colunas_int_df_inep(dfa,vai_printar_cols=False)
    dfa['IN_LECIONA_PUBLICA'] = (df.groupby(col_chave)['ID_DEPENDENCIA_ADM'].min() < 4).fillna(False).astype(np.int8)
    dfa['IN_LECIONA_PRIVADA'] = (df.groupby(col_chave)['ID_DEPENDENCIA_ADM'].max() == 4).fillna(False).astype(np.int8)
    return dfa



def importa_campos(arq):
    re_letras = re.compile('\W')
    ajusta_texto = lambda t: re_letras.sub('',normalize('NFKD', str(t).lower()).encode('ASCII', 'ignore').decode('ASCII'))
    d = pd.read_csv(arq,sep='|',index_col='VARIAVEL').dropna()
    d.DESCRICAO = d.DESCRICAO.astype(str)
    d['DESCRICAO'] = d.DESCRICAO.apply(ajusta_texto)
    return d



#funcoes de De/Para utilizada na exploracao do problema
def de_para_mesmo_nome(df_dados,df_var,n):
    e = df_var.reset_index()[['VARIAVEL']]
    e.columns = [f'VARIAVEL_{n}']
    a = df_dados[['DESCRICAO','NM_ANT_VAR']].reset_index().\
    merge(e,right_on=f'VARIAVEL_{n}',copy=True,left_on='VARIAVEL', suffixes=('_ref','_'+n))
    a[f'NM_VAR_{n}'] = a[f'VARIAVEL_{n}']
    a = a[['VARIAVEL','DESCRICAO',f'NM_VAR_{n}']]
    return a.set_index('VARIAVEL')

def de_para_nome_anterior(df_dados,df_var,n):
    a = df_dados.merge(df_var,left_on='NM_ANT_VAR',right_index=True,suffixes=('_ref','_'+n))
    a[f'NM_VAR_{n}'] = a['NM_ANT_VAR']
    a = a[['DESCRICAO_ref',f'NM_VAR_{n}']]
    a.columns = ['DESCRICAO',f'NM_VAR_{n}']
    return a

def de_para_descricao_igual(df_dados,df_var,n):
    a = df_dados.merge(df_var.reset_index(),right_on='DESCRICAO',left_on='DESCRICAO',suffixes=('_ref','_'+n))
    a[f'NM_VAR_{n}'] = a[f'VARIAVEL']
    a = a[['DESCRICAO',f'NM_VAR_{n}']]
    a.columns = ['DESCRICAO',f'NM_VAR_{n}']
    return a

def monta_de_para(dados,dvar,nm_var):
    #nomes iguais
    v = de_para_mesmo_nome(dados,dvar,nm_var)
    #nome anterior igual
    v = v.append(de_para_nome_anterior(dados.loc[~dados.index.isin(v.index.values)],dvar,nm_var),sort=True)
    #nomes diferentes descricoes iguais
    v = v.append(de_para_descricao_igual(dados.loc[~dados.index.isin(v.index.values)],dvar,nm_var),sort=True)
    return v[f'NM_VAR_{nm_var}']


#Monta df com uma linha por prof/ano
def monta_df_prof_ano(df):
    pss = list(set(df.CO_PESSOA_FISICA.values))
    cols_dfa = ['CO_PESSOA_FISICA', 'ANO', 'CO_AREA_CURSO_1', 'CO_AREA_CURSO_2',
       'CO_AREA_CURSO_3', 'CO_CURSO_1', 'CO_CURSO_2', 'CO_CURSO_3', 'CO_IES_1',
       'CO_IES_2', 'CO_IES_3', 'CO_MUNICIPIO_END', 'CO_MUNICIPIO_NASC',
       'CO_PAIS_ORIGEM', 'CO_UF_END', 'CO_UF_NASC', 'IN_COM_PEDAGOGICA_1',
       'IN_COM_PEDAGOGICA_2', 'IN_COM_PEDAGOGICA_3', 'IN_DISC_ARTES',
       'IN_DISC_ATENDIMENTO_ESPECIAIS', 'IN_DISC_BIOLOGIA', 'IN_DISC_CIENCIAS',
       'IN_DISC_DIVER_SOCIO_CULTURAL', 'IN_DISC_EDUCACAO_FISICA',
       'IN_DISC_ENSINO_RELIGIOSO', 'IN_DISC_FILOSOFIA', 'IN_DISC_FISICA',
       'IN_DISC_GEOGRAFIA', 'IN_DISC_HISTORIA',
       'IN_DISC_INFORMATICA_COMPUTACAO', 'IN_DISC_LIBRAS',
       'IN_DISC_LINGUA_ESPANHOL', 'IN_DISC_LINGUA_INDIGENA',
       'IN_DISC_LINGUA_INGLES', 'IN_DISC_LINGUA_OUTRA',
       'IN_DISC_LINGUA_PORTUGUESA', 'IN_DISC_MATEMATICA', 'IN_DISC_OUTRAS',
       'IN_DISC_PEDAGOGICAS', 'IN_DISC_PROFISSIONALIZANTE', 'IN_DISC_QUIMICA',
       'IN_DOUTORADO', 'IN_ESPECIALIZACAO', 'IN_ESPECIFICO_ANOS_FINAIS',
       'IN_ESPECIFICO_ANOS_INICIAIS', 'IN_ESPECIFICO_CRECHE',
       'IN_ESPECIFICO_ED_ESPECIAL', 'IN_ESPECIFICO_ED_INDIGENA',
       'IN_ESPECIFICO_EJA', 'IN_ESPECIFICO_ENS_MEDIO', 'IN_ESPECIFICO_NENHUM',
       'IN_ESPECIFICO_OUTROS', 'IN_ESPECIFICO_PRE_ESCOLA', 'IN_LICENCIATURA_1',
       'IN_LICENCIATURA_2', 'IN_LICENCIATURA_3', 'IN_MESTRADO',
       'IN_POS_NENHUM', 'NU_ANO', 'NU_ANO_CONCLUSAO_1', 'NU_ANO_CONCLUSAO_2',
       'NU_ANO_CONCLUSAO_3', 'NU_ANO_INICIO_1', 'NU_ANO_INICIO_2',
       'NU_ANO_INICIO_3', 'NU_DIA', 'NU_IDADE', 'NU_MES', 'TP_COR_RACA',
       'TP_ESCOLARIDADE', 'TP_NACIONALIDADE', 'TP_SEXO', 'TP_SITUACAO_CURSO_1',
       'TP_SITUACAO_CURSO_2', 'TP_SITUACAO_CURSO_3', 'TP_TIPO_IES_1',
       'TP_TIPO_IES_2', 'TP_TIPO_IES_3']
    dfa = pd.DataFrame(columns=cols_dfa)
    vls = []
    for a in tqdm(df.ANO.unique()):
        dfa = dfa.append(df.loc[df.ANO == a][cols_dfa].groupby('CO_PESSOA_FISICA').max().reset_index(),sort=True)
    dfa = dfa.set_index(['CO_PESSOA_FISICA','ANO'])
    dfa['IN_CIDADE_NATAL'] = dfa['CO_MUNICIPIO_NASC'] == dfa['CO_MUNICIPIO_END']
    dfa.IN_CIDADE_NATAL = dfa.IN_CIDADE_NATAL.astype(np.int8)
    dfa['NUM_TTL_GRAD'] = (dfa[f'TP_SITUACAO_CURSO_1'] == 1).astype(np.int8) + (dfa[f'TP_SITUACAO_CURSO_2'] == 1).astype(np.int8) + (dfa[f'TP_SITUACAO_CURSO_3'] == 1).astype(np.int8)
    dfa['NUM_QTD_ESCOLAS'] = df.groupby(['CO_PESSOA_FISICA','ANO'])['CO_ENTIDADE'].nunique().fillna(0)
    dfa['NUM_QTD_TURMAS'] = df.groupby(['CO_PESSOA_FISICA','ANO'])['ID_TURMA'].count().fillna(0)

    dfa['IN_LECIONA_PUBLICA'] = (df.groupby(['CO_PESSOA_FISICA','ANO'])['TP_DEPENDENCIA'].min() < 4).fillna(False).astype(np.int8)
    dfa['IN_LECIONA_PRIVADA'] = (df.groupby(['CO_PESSOA_FISICA','ANO'])['TP_DEPENDENCIA'].max() == 4).fillna(False).astype(np.int8)
    #dfa.fillna(-1)
    #dfa = ajusta_colunas_int_df_inep(dfa,vai_printar_cols=False)
    return dfa





def monta_df_professores_vs17_resu(df):
    col_chave = list(df.columns)[1]
    pref_col_sit_curso ='TP_SITUACAO_CURSO'
    colunas = [col_chave,'CO_MUNICIPIO_NASC','CO_MUNICIPIO_END','CO_ENTIDADE','TP_DEPENDENCIA','TP_COR_RACA'] + [f'{pref_col_sit_curso}_{i}' for i in [1,2,3]]
    dfa = df[colunas].groupby(col_chave).max()

    dfa['IN_CIDADE_NATAL'] = dfa['CO_MUNICIPIO_END'] == dfa['CO_MUNICIPIO_NASC']
    dfa.IN_CIDADE_NATAL = dfa.IN_CIDADE_NATAL.astype(np.int8)

    dfa['NUM_TTL_GRAD'] = (dfa[f'{pref_col_sit_curso}_1'] == 1).astype(np.int8) + (dfa[f'{pref_col_sit_curso}_2'] == 1).astype(np.int8) + (dfa[f'{pref_col_sit_curso}_3'] == 1).astype(np.int8)
    dfa['NUM_QTD_ESCOLAS'] = df.groupby(col_chave)['CO_ENTIDADE'].nunique().fillna(0)
    dfa['NUM_QTD_TURMAS'] = df.groupby(col_chave)['CO_ENTIDADE'].count().fillna(0)

    dfa = ajusta_colunas_int_df_inep(dfa,vai_printar_cols=False)
    dfa['IN_LECIONA_PUBLICA'] = (df.groupby(col_chave)['TP_DEPENDENCIA'].min() < 4).fillna(False).astype(np.int8)
    dfa['IN_LECIONA_PRIVADA'] = (df.groupby(col_chave)['TP_DEPENDENCIA'].max() == 4).fillna(False).astype(np.int8)
    return dfa







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
