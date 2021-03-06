
# Projeto de conclusão de curso de _nanodegree_

### Ítalo Barreto


### Objetivo:
Esse projeto visa investigar as causas que levaram professores da rede pública do DF a sair da escola que estavam lotados no ano de 2015. Para avaliar a rotatividade comparei com a base de 2017.

### Ferramental:

#### Enviroment:
- OS: Ubuntu 16.04
- Python 3.6.4 | Anaconda custom (64-bit)


#### Bibliotecas utilizadas:

* pandas: 0.23.0
* numpy: 1.14.3
* matplotlib: 2.2.2
* seaborn: 0.8.1
* tqdm: 4.23.4
* scipy: 1.1.0
* sklearn: 0.19.1
* IPython: 6.4.0
* folium: 0.5.0
* xgboost: 0.80
* tabulate: 0.8.2

Para visualização correta favor abrir no jupyter notebook pois o visualizador do Github não exibe corretamente as saídas html.


### Organização do projeto:

#### Por ordem de execução

01. Download dos arquivos do site do Inep Data (raw_data/inep_files.py).
02. Descompactação dos arquivos de interesse (raw_data/inep_files.py).
03. Construção da base de estudo (MontagemDasBases.ipynb).
04. Investigação da base construída (EDA_Professores.ipynb)

Os arquivos não mencionados aqui servem para suporte dos referidos programas.

#### Atalho:
É possível executar diretamente o arquivo EDA_Professores.ipynb desde que:
- o arquivo model_vars exista (pode ser baixado nesse [link](https://www.dropbox.com/s/igdnw2gu6tybq2z/model_vars.csv?dl=0)).
- editar a estrutura de diretórios nas variáveis CSV_PATH e PATH_DF_CSV que estão declaradas no arquivo raw_data/constantes.py.
