import urllib.request
import os
import patoolib
import zipfile
from glob import glob
import shutil
from tqdm import tqdm
CSV_PATH = '/home/itsbarreto/csv/educacao/'
ARQ_PATH = CSV_PATH + 'dsc/'
PATH_DF_CSV = CSV_PATH + 'mod/'

url_inep = lambda arq,ano: f'http://download.inep.gov.br/microdados/{arq}_{ano}.zip'
baixa_inep = lambda arq, anos: map(lambda ano: urllib.request.urlretrieve(url_inep(arq,ano), CSV_PATH + f'{arq}_{ano}.zip'), anos)


#destino do arquivo csv
def dst_csv_docente(ano,arq):
    return ano + '/' + arq.split('/')[-1]

def extrai_arq(arq):
    dst_ano = lambda arq_zip: ARQ_PATH + arq_zip[-8:-4]

    TMP_PATH = '/'.join(arq.split('/')[:-1]) + '/TMP/'
    shutil.rmtree(TMP_PATH,ignore_errors=True)
    os.mkdir(TMP_PATH)
    patoolib.extract_archive(arq, outdir=TMP_PATH)
    try:
        os.mkdir(dst_ano(arq))
    except:
        pass
    list(map(lambda f: patoolib.extract_archive(f, outdir=dst_ano(arq)), [f for f in glob(f'{TMP_PATH}*/DADOS/*') if (('DOCENTE' in f or 'MATRICULA' in f) and '_CO' in f) or 'ESCOLAS' in f or 'TURMA' in f]))
    shutil.rmtree(TMP_PATH,ignore_errors=True)



baixa_img = lambda url, nm: urllib.request.urlretrieve(url, 'img/%s'%nm)
#baixa_img('https://i.gifer.com/Gckv.gif','exploracao.gif')
