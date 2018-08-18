import pandas as pd
import shapefile
from shapely.geometry import shape
from shapely.geometry import Point, Polygon
import numpy as np
from glob import glob
from tqdm import tqdm



class SetorCensitario:
    indice_uf = -1

    def __init__(self,PATH_CENSO):
        self.PATH_CENSO = PATH_CENSO
        self.indice_uf = -1

    def checa_ponto(coord,lat,lng):
        try:
            return  Polygon(coord).contains(Point((lat,lng)))
        except Exception as e:
            for c in coord:
                return SetorCensitario.checa_ponto(c,lat,lng)
            pass
    def codigo_uf_ponto(self,feat,lat,lng,rec=1):
        if SetorCensitario.checa_ponto(feat.shape.__geo_interface__['coordinates'],lat,lng):
            return int(feat.record[rec])
        return -1


    def monta_array(arq,colunas,setor):
        df = pd.read_csv(f'{arq}',sep=';',usecols=colunas,encoding='latin1')
        df = df.loc[df.Cod_setor == int(setor)].values
        return None if len(df) == 0 else df[0]

    def obtem_dado_uf(self,uf,lat,lng):
        for f in shapefile.Reader(glob('%s/*.shp' %(self.PATH_CENSO))[0]).shapeRecords():
            if self.codigo_uf_ponto(f,lat,lng) != -1: return f
        return None

    def dados_setor_censitario(self,lat,lng):
        if lat > 0 or lng > 0: return None
        uf_cli = 'DF'
        path_csv = ('%s/dados/' %self.PATH_CENSO)
        fus = self.obtem_dado_uf(uf_cli,lat,lng)
        area = shape(fus.shape).area

        cols_dom01 = ['Cod_setor', 'Situacao_setor','V002', 'V006','V007','V008','V009','V010','V011']
        df_dm1 = SetorCensitario.monta_array(('%sDomicilio01_%s.csv'%(path_csv,uf_cli)),cols_dom01,fus.record[1])

        cols_pss12 = ['Cod_setor','V019']+[ 'V' + str(i).zfill(3) for i in range(1,4)]
        df_pss12 = SetorCensitario.monta_array(('%sPessoa12_%s.csv'%(path_csv,uf_cli)),cols_pss12,fus.record[1])

        cols_pss13 = ['Cod_setor']+[ 'V' + str(i).zfill(3) for i in range(22,135)]
        df_pss13 = SetorCensitario.monta_array(('%sPessoa13_%s.csv'%(path_csv,uf_cli)),cols_pss13,fus.record[1])

        cols_dr1 = ['Cod_setor','V002']+[ 'V' + str(i).zfill(3) for i in range(5,15)]
        df_dr1 = SetorCensitario.monta_array(('%sDomicilioRenda_%s.csv'%(path_csv,uf_cli)),cols_dr1,fus.record[1])

        cols_ent1 = ['Cod_setor', 'V001']
        df_ent1 = SetorCensitario.monta_array(('%sEntorno01_%s.csv'%(path_csv,uf_cli)),cols_ent1,fus.record[1])

        cols_ent2 = ['Cod_setor']+[ 'V' + str(i).zfill(3) for i in range(262,274)]
        df_ent2 = SetorCensitario.monta_array(('%sEntorno02_%s.csv'%(path_csv,uf_cli)),cols_ent2,fus.record[1])

        cols_ent3 = ['Cod_setor','V422']
        df_ent3 = SetorCensitario.monta_array(('%sEntorno03_%s.csv'%(path_csv,uf_cli)),cols_ent3,fus.record[1])


        pop_ttl = sum([int(df_pss13[i]) for i,c in enumerate(cols_pss13) if c.startswith('V')])  if not df_pss13 is None else np.nan
        return {
            'latitude' : lat,
            'longitude' : lng,
            'co_entidade' : uf_cli,
            'cd_setor' : fus.record[1],
            'sit_setor' : df_dm1[cols_dom01.index('Situacao_setor')] if not df_dm1 is None else np.nan,
            'densidade_demografica' : area/pop_ttl,
            'area_media_domicilio' : area/df_dm1[cols_dom01.index('V002')]  if not df_dm1 is None else np.nan,
            'qtd_domicilios' : int(df_dm1[cols_dom01.index('V002')])  if not df_dm1 is None else np.nan,
            'qtd_quitados' : int(df_dm1[cols_dom01.index('V006')])  if not df_dm1 is None else np.nan,
            'qtd_em_aquisicao' : int(df_dm1[cols_dom01.index('V007')])  if not df_dm1 is None else np.nan,
            'qtd_alugados' : int(df_dm1[cols_dom01.index('V008')])  if not df_dm1 is None else np.nan,
            'qtd_cedidos' : int(df_dm1[cols_dom01.index('V009')]) + int(df_dm1[cols_dom01.index('V010')])  if not df_dm1 is None else np.nan,
            'renda_media_dom' : int(df_dr1[cols_dr1.index('V002')])/int(df_dm1[cols_dom01.index('V002')]) if not df_dm1 is None else np.nan,
            'qtd_dom_renda_per_cap_abx_1sm' : np.sum([int(df_dr1[cols_dr1.index('V'+str(i).zfill(3))]) for i in range(5,9)])  if not df_dr1 is None else np.nan,
            'qtd_dom_renda_max_per_mais_5sm' : np.sum([int(df_dr1[cols_dr1.index('V'+str(i).zfill(3))]) for i in range(12,14)])  if not df_dr1 is None else np.nan,
            'qtd_dom_renda_per_cap_abx_1sm_vizinhos' : np.sum([int(df_ent2[cols_ent2.index('V'+str(i).zfill(3))]) for i in range(262,268)]) if not df_ent2 is None else np.nan,
            'qtd_pessoas' : pop_ttl,
            'qtd_pessoas_vizinhos' : int(df_ent3[cols_ent3.index('V422')]) if not df_ent3 is None else np.nan,
            'qtd_dom_vizinhos' : int(df_ent1[cols_ent1.index('V001')]) if not df_ent1 is None else np.nan,
            'qtd_mulheres_resp' : int(df_pss12[cols_pss12.index('V003')])  if not df_pss12 is None else np.nan,
            'qtd_mulheres' : int(df_pss12[cols_pss12.index('V001')])  if not df_pss12 is None else np.nan,
            'qtd_pss_abx_12' : np.sum([int(df_pss13[cols_pss13.index('V'+str(i).zfill(3))]) for i in range(22,46)])  if not df_pss13 is None else np.nan,
            'qtd_pss_acima_65' : np.sum([int(df_pss13[cols_pss13.index('V'+str(i).zfill(3))]) for i in range(99,135)])   if not df_pss13 is None else np.nan,
            'qtd_pss_acima_90' : np.sum([int(df_pss13[cols_pss13.index('V'+str(i).zfill(3))]) for i in range(124,135)])   if not df_pss13 is None else np.nan

        }
