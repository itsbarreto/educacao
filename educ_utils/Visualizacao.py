"""
    Arquivo com algumas funcoes gerais de visualizacao de dados

"""

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from IPython.core.display import display, HTML



def explora_df(df : pd.DataFrame,var_cor = None):
    #mostra alguns dados de todas as colunas de um DataFrame qualquer.
    qtd_ttl = df.shape[0]
    for i,c in enumerate(df.columns):
        display(HTML(f'<h2>{i+1}. {c}</h2>'))
        pc_nulos = df[c].isnull().sum() / qtd_ttl * 100
        display(f'{pc_nulos}% de registros nulos')
        try:
            display(f'Variância: {df[c].var()}')
        except:
            print('Não foi possível calcular a variância.')
            pass
        if var_cor:
            try:
                display(f'Correlacao:')
                for v in var_cor:
                    display(df[[c,v]].corr())
                    sns.violinplot(x=v,y=c,data=df)
                    plt.show()
            except:
                print('Não foi possível calcular a correlação.')
                pass
        if len(df[c].value_counts().values) > 10:
            display(df[c].describe())
        else:
            a = pd.DataFrame(df[c].value_counts())
            a.columns = ['qtd']
            a['pc'] = a['qtd']/qtd_ttl
            display(a)
        df[c].hist(bins=30)
        plt.show()
        display(HTML('<hr/>'))


def magnify():
    return [dict(selector="th",
                 props=[("font-size", "7pt")]),
            dict(selector="td",
                 props=[('padding', "0em 0em")]),
            dict(selector="th:hover",
                 props=[("font-size", "12pt")]),
            dict(selector="tr:hover td:hover",
                 props=[('max-width', '200px'),
                        ('font-size', '12pt')])
            ]


def plota_matriz_heatmap(df  : pd.DataFrame):
    cmap = cmap=sns.diverging_palette(5, 250, as_cmap=True)
    return df.style.background_gradient(cmap, axis=1)\
        .set_properties(**{'max-width': '80px', 'font-size': '10pt'})\
        .set_caption("Hover to magify")\
        .set_precision(2)\
        .set_table_styles(magnify())
