import pandas as pd
import shapefile
from shapely.geometry import shape
from shapely.geometry import Point, Polygon
import numpy as np
from glob import glob
from tqdm import tqdm
from geopy.distance import vincenty
#Passos,
#01. achar setores das redondezas
#02. achar dados desses setores


def acha_lista_coord(f):
    try:
        return f.shape.__geo_interface__['coordinates'][0],f
    except Exception as e:
        for c in f:
            return acha_lista_coord(c)

def dados_setor_censitario(path_csv,arq_shp,escolas):
    importa_df_censo = lambda arq, cols: pd.read_csv('%s'%arq,sep=';',usecols=cols,encoding='latin1',dtype={'Cod_setor' : np.int64})


    dados_censo = {}
    cols_dom01 = ['Cod_setor', 'Situacao_setor','V002', 'V006','V007','V008','V009','V010','V011']
    df_dm1 = importa_df_censo('%sDomicilio01_DF.csv'%(path_csv),cols_dom01)
    df_dm1.replace(to_replace='X', value='0',inplace=True)
    for c in df_dm1.columns:
        df_dm1[c] = df_dm1[c].astype(np.int64)
    dados_censo['dom01'] = {'cols' : cols_dom01, 'dados' : df_dm1, 'linha' : None}
    del cols_dom01,df_dm1

    cols_pss12 = ['Cod_setor','V019']+[ 'V' + str(i).zfill(3) for i in range(1,4)]
    df_pss12 = importa_df_censo('%sPessoa12_DF.csv'%(path_csv),cols_pss12)
    df_pss12.replace(to_replace='X', value='0',inplace=True)
    for c in df_pss12.columns:
        df_pss12[c] = df_pss12[c].astype(np.int64)
    dados_censo['pss12'] = {'cols' : cols_pss12, 'dados' : df_pss12, 'linha' : None}
    del cols_pss12,df_pss12

    cols_pss13 = ['Cod_setor']+[ 'V' + str(i).zfill(3) for i in range(22,135)]
    df_pss13 = importa_df_censo('%sPessoa13_DF.csv'%(path_csv),cols_pss13)
    df_pss13.replace(to_replace='X', value='0',inplace=True)
    for c in df_pss13.columns:
        df_pss13[c] = df_pss13[c].astype(np.int64)
    df_pss13['pop_ttl'] = df_pss13[[c for c in cols_pss13 if c.startswith('V')]].sum(axis=1)
    dados_censo['pss13'] = {'cols' : cols_pss13, 'dados' : df_pss13, 'linha' : None}
    del cols_pss13,df_pss13

    cols_dr1 = ['Cod_setor','V002']+[ 'V' + str(i).zfill(3) for i in range(5,15)]
    df_dr1 = importa_df_censo('%sDomicilioRenda_DF.csv'%(path_csv),cols_dr1)
    df_dr1.replace(to_replace='X', value='0',inplace=True)
    for c in df_dr1.columns:
        df_dr1[c] = df_dr1[c].astype(np.int64)
    dados_censo['dr1'] = {'cols' : cols_dr1, 'dados' : df_dr1, 'linha' : None}
    del cols_dr1,df_dr1

    cols_ent1 = ['Cod_setor', 'V001']
    df_ent1 = importa_df_censo('%sEntorno01_DF.csv'%(path_csv),cols_ent1)
    df_ent1.replace(to_replace='X', value='0',inplace=True)
    for c in df_ent1.columns:
        df_ent1[c] = df_ent1[c].astype(np.int64)
    dados_censo['ent1'] = {'cols' : cols_ent1, 'dados' : df_ent1, 'linha' : None}
    del cols_ent1,df_ent1

    cols_ent2 = ['Cod_setor']+[ 'V' + str(i).zfill(3) for i in range(262,274)]
    df_ent2 = importa_df_censo('%sEntorno02_DF.csv'%(path_csv),cols_ent2)
    df_ent2.replace(to_replace='X', value='0',inplace=True)
    for c in df_ent2.columns:
        df_ent2[c] = df_ent2[c].astype(np.int64)
    dados_censo['ent2'] = {'cols' : cols_ent2, 'dados' : df_ent2, 'linha' : None}
    del cols_ent2,df_ent2

    cols_ent3 = ['Cod_setor','V422']
    df_ent3 = importa_df_censo('%sEntorno03_DF.csv'%(path_csv),cols_ent3)
    df_ent3.replace(to_replace='X', value='0',inplace=True)
    for c in df_ent3.columns:
        df_ent3[c] = df_ent3[c].astype(np.int64)
    dados_censo['ent3'] = {'cols' : cols_ent3, 'dados' : df_ent3, 'linha' : None}
    del cols_ent3,df_ent3

    calcula_dados = lambda area: {
        'sit_setor' : dados_censo['dom01']['linha']['Situacao_setor'].values[0] if not dados_censo['dom01']['linha'] is None else np.nan,
        'densidade_demografica' :  area/int(dados_censo['pss13']['linha']['pop_ttl'].values[0]) if not dados_censo['pss13']['linha'] is None and int(dados_censo['pss13']['linha']['pop_ttl'].values[0]) > 0 else 0,
        'area_media_domicilio' : area/int(dados_censo['dom01']['linha']['V002'].values[0])  if not dados_censo['dom01']['linha'] is None and int(dados_censo['dom01']['linha']['V002'].values[0])>0 else np.nan,
        'qtd_domicilios' : int(dados_censo['dom01']['linha']['V002'].values[0])  if not dados_censo['dom01']['linha'] is None else np.nan,
        'qtd_quitados' : int(dados_censo['dom01']['linha']['V006'].values[0])  if not dados_censo['dom01']['linha'] is None else np.nan,
        'qtd_em_aquisicao' : int(dados_censo['dom01']['linha']['V007'].values[0])  if not dados_censo['dom01']['linha'] is None else np.nan,
        'qtd_alugados' : int(dados_censo['dom01']['linha']['V008'].values[0])  if not dados_censo['dom01']['linha'] is None else np.nan,
        'qtd_cedidos' : int(dados_censo['dom01']['linha']['V009'].values[0]) + int(dados_censo['dom01']['linha']['V010'].values[0])  if not dados_censo['dom01']['linha'] is None else np.nan,
        'renda_media_dom' : int(dados_censo['dr1']['linha']['V002'].values[0])/int(dados_censo['dom01']['linha']['V002'].values[0]) if not dados_censo['dom01']['linha'] is None and int(dados_censo['dom01']['linha']['V002'].values[0])>0 else np.nan,
        'qtd_dom_renda_per_cap_abx_1sm' : np.sum([int(dados_censo['dr1']['linha']['V'+str(i).zfill(3)]) for i in range(5,9)])  if not dados_censo['dr1']['linha'] is None else np.nan,
        'qtd_dom_renda_max_per_mais_5sm' : np.sum([int(dados_censo['dr1']['linha']['V'+str(i).zfill(3)]) for i in range(12,14)])  if not dados_censo['dr1']['linha'] is None else np.nan,
        'qtd_dom_renda_per_cap_abx_1sm_vizinhos' : np.sum(dados_censo['ent2']['linha'][['V'+str(i).zfill(3) for i in range(262,268)]].values) if not dados_censo['ent2']['linha'] is None else np.nan,
        'qtd_pessoas' : dados_censo['pss13']['linha']['pop_ttl'].values[0] if not dados_censo['pss13']['linha'] is None else np.nan,
        'qtd_pessoas_vizinhos' : int(dados_censo['ent3']['linha']['V422'].values[0]) if not dados_censo['ent3']['linha'] is None else np.nan,
        'qtd_dom_vizinhos' : int(dados_censo['ent1']['linha']['V001']) if not dados_censo['ent1']['linha'] is None else np.nan,
        'qtd_mulheres_resp' : int(dados_censo['pss12']['linha']['V003'])  if not dados_censo['pss12']['linha'] is None else np.nan,
        'qtd_mulheres' : int(dados_censo['pss12']['linha']['V001'])  if not dados_censo['pss12']['linha'] is None else np.nan,
        'qtd_pss_abx_12' : np.sum(dados_censo['pss13']['linha'][['V'+str(i).zfill(3) for i in range(22,46)]].values)  if not dados_censo['pss13']['linha'] is None else np.nan,
        'qtd_pss_acima_65' : np.sum(dados_censo['pss13']['linha'][['V'+str(i).zfill(3) for i in range(99,135)]].values)   if not dados_censo['pss13']['linha'] is None else np.nan,
        'qtd_pss_acima_90' : np.sum(dados_censo['pss13']['linha'][['V'+str(i).zfill(3) for i in range(124,135)]].values)   if not dados_censo['pss13']['linha'] is None else np.nan
    }
    escolas['MENOR_DIST'] = escolas.apply(lambda x: min([vincenty((x['LONG'],x['LAT']), (e[2],e[1])).km for e in escolas[['CO_ENTIDADE','LAT','LONG']].values if x['CO_ENTIDADE'] != e[0]]),axis=1)
    sf_df = shapefile.Reader(arq_shp)
    escolas_setores = []
    for f in tqdm(sf_df.shapeRecords()):
        lc, feat = acha_lista_coord(f)
        pol = Polygon(lc)
        area = shape(feat.shape).area
        for k,v in dados_censo.items():
            try:
                dados_censo[k]['linha'] = v['dados'].loc[v['dados']['Cod_setor'] == np.int64(feat.record[1])]
                if dados_censo[k]['linha'].shape[0] == 0:
                    dados_censo[k]['linha'] = None
            except Exception as e:
                dados_censo[k]['linha'] == None
                pass

        escolas_setores.extend([(f.record[1],l[0],calcula_dados(area),vincenty(pol.centroid.coords, (l[2],l[1])).km) for l in escolas[['CO_ENTIDADE','LAT','LONG','MENOR_DIST']].values if vincenty(pol.centroid.coords, (l[2],l[1])).km < max([2.5,l[3]/2])])
    lpd = []
    for a,b,c,d in escolas_setores:
        c['CO_SETOR_CENSITARIO'] = a
        c['CO_ENTIDADE'] = b
        c['DISTANCIA_SETOR_ENTIDADE'] = d
        lpd.append(c)
    return pd.DataFrame(lpd)
