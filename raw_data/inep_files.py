# -*- coding: utf-8 -*-
"""Arquivos do Inep

Esse modulo faz o download e a descompactação dos arquivos necessários para
análise das saídas dos professores das escolas.


"""
import urllib.request
import os
import patoolib
import zipfile
from glob import glob
import shutil
from tqdm import tqdm

from constantes import ANOS_PESQUISA, ARQ_PATH, CSV_PATH

def url_inep(arq : str, ano : str) -> str:
    #monta string com a url do arquivo
    return ('http://download.inep.gov.br/microdados/%s_%s.zip' %(arq,ano))


def baixa_inep (arq : str, anos : list):
    #baixa os arquivos dos anos informados
    map(
            lambda ano: urllib.request.urlretrieve(
                        url_inep(arq,str(ano)),
                                ('%s%s_%s.zip' %(CSV_PATH,arq,ano))),
                        anos
                        )

def baixa_micro_censo_escolar (anos : list):
    #baixa os dados do micro censo escolar
    baixa_inep('micro_censo_escolar_',anos)

def dst_csv_docente(ano,arq : str) -> str:
    #destino do arquivo csv
    return ano + '/' + arq.split('/')[-1]

def extrai_arq(arq):
    #descompacta os arquivos para uma pasta temporaria
    dst_ano = lambda arq_zip: ARQ_PATH + arq_zip[-8:-4]
    TMP_PATH = '/'.join(arq.split('/')[:-1]) + '/TMP/'
    shutil.rmtree(TMP_PATH,ignore_errors=True)
    os.mkdir(TMP_PATH)
    patoolib.extract_archive(arq, outdir=TMP_PATH)
    try:
        os.mkdir(dst_ano(arq))
    except:
        pass
    list(map(lambda f:
                patoolib.extract_archive(f, outdir=dst_ano(arq)),
                                        [f for f in glob(f'{TMP_PATH}*/DADOS/*')
                                            if (
                                                ('DOCENTE' in f or 'MATRICULA' in f)
                                                and '_CO' in f)
                                            or 'ESCOLAS' in f or 'TURMA' in f
                                        ]
            ))
    shutil.rmtree(TMP_PATH,ignore_errors=True)

def extrai_todos_arquivos(dir_ogm,dir_dst):
    #descompacta para a pasta de destino
    shutil.rmtree(dir_ogm,ignore_errors=True)
    os.mkdir(dir_ogm)
    list(map(extrai_arq,glob(dir_dst + '*.zip')))

if __name__ == '__main__':
    #baixa arquivos do site inepdata
    baixa_micro_censo_escolar(ANOS_PESQUISA)
    #extracao dos arquivos de interesse
    extrai_todos_arquivos(ARQ_PATH,CSV_PATH)
