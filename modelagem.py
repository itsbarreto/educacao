'''


Criado em 21.08.2018, por Ítalo Barreto.

Utilizado para "limpar" o .ipynb das funções de criação de modelo.

'''

import pandas as  pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.preprocessing import MinMaxScaler
from time import time
from scipy.stats import randint as sp_randint
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import classification_report
import seaborn as sns
from sklearn.cluster import DBSCAN
from sklearn.cluster import MiniBatchKMeans

def processa_tudo(model_vars : pd.DataFrame,grid_search=False,tg='target',vai_escalar=True,clf=None):
    """
        Função que executa e avalia um classificador padrão
        (com grid_search ou não).

        Arguments
        ---------
        model_vars: pandas.DataFrame
            A tabela com os dados para modelagem, a variável target deve ser uma
            das colunas desse DataFrame.
        grid_search: bool
            Se a modelagem incluirá o grid de parâmetros.
        tg: str
            Nome da coluna que será a target do modelo.
        vai_escalar: bool
            Se os dados passarão por um MinMaxScaler.
        clf:
            Algum classificador que possua método fit, em caso de ser None o
            classificador será um sklearn.ensemble.RandomForestClassifier

        Returns
        -------
        tuple
            Em que o primeiro é uma lista com o feature importance (caso haja) e
            o segundo é o classificador.
    """
    X_train, X_test, y_train, y_test = gera_datasets(model_vars,False,tg=tg,vai_escalar=True)
    if grid_search:
        clf = modela_gs_cv(X_test,y_test,RandomForestClassifier(random_state=123))
    else:
        clf = modela(X_train,y_train,clf)
    return avalia(X_test,y_test,X_train,y_train, clf,model_vars.drop(tg,axis=1).columns),clf


def gera_datasets(model_vars,balanceia = True,tg='target',vai_escalar=True):
    md = model_vars.copy()
    if balanceia:
        md = model_vars.loc[model_vars[tg] == 0].sample(sum(model_vars[tg].values),random_state=42).append(model_vars.loc[model_vars[tg] == 1])
    X = md.drop(tg,axis=1).values
    y = np.array(md[tg].values)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)
    if vai_escalar:
        scaler = MinMaxScaler()
        scaler.fit(X_train)
        X_train = scaler.transform(X_train)
        X_test = scaler.transform(X_test)
    return X_train, X_test, y_train, y_test


def modela(X_train,y_train,clf=None):
    if clf is None:
        clf = RandomForestClassifier(random_state=0)
    clf.fit(X_train,y_train)
    return clf


def avalia(X_test,y_test,X_train,y_train, clf,cols,y_pred=None):
    if not y_pred:
        y_pred = clf.predict(X_test)
    print('Base de TREINO')
    print(classification_report(y_train, clf.predict(X_train)))
    print('Base de TESTE')
    print(classification_report(y_test, y_pred))
    print_confusion_matrix(confusion_matrix(y_test, y_pred),sorted(set(y_train)))
    plt.show()
    try:
        y_pred_proba = clf.predict_proba(X_test)[::,1]
        fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred_proba   )
        auc = metrics.roc_auc_score(y_test, y_pred_proba)

        plt.plot(fpr,tpr,label="Base de teste, auc="+str(auc))
        plt.legend(loc=4)
        plt.show()
    except:
        print('Nao foi possivel mostrar a ROC.')
        pass
    if type(clf) == GridSearchCV:
        clf = clf.best_estimator_
    # Print the feature ranking
    print("Feature ranking:")
    fi = []
    try:
        importances = clf.feature_importances_
        std = None
        try:
            std = np.std([tree.feature_importances_ for tree in clf.estimators_],
                         axis=0)
        except Exception as e:
            pass
        indices = np.argsort(importances)[::-1]
        for f in range(X_test.shape[1]):
            fi.append(cols[indices[f]])
            print("%d. feature %s (%f)" % (f + 1, cols[indices[f]], importances[indices[f]]))
        plt.figure()
        plt.title("Feature importances")
        if std:
            plt.bar(range(X_test.shape[1]), importances[indices],
                   color="r", yerr=std[indices], align="center")
        else:
            plt.bar(range(X_test.shape[1]), importances[indices],
                   color="r", align="center")
        plt.xticks(range(X_test.shape[1]), indices)
        plt.xlim([-1, X_test.shape[1]])
        plt.show()

    except Exception as e:
        print('Nao foi possivel plotar o feature importance.')
        print(e)
        pass
    return fi


# Utility function to report best scores
def report(results, n_top=3):
    for i in range(1, n_top + 1):
        candidates = np.flatnonzero(results['rank_test_score'] == i)
        for candidate in candidates:
            print("Model with rank: {0}".format(i))
            print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
                  results['mean_test_score'][candidate],
                  results['std_test_score'][candidate]))
            print("Parameters: {0}".format(results['params'][candidate]))
            earch = 20
            pass
            random_sprint("")

def modela_gs_cv(X_test,y_test,clf):
    # specify parameters and distributions to sample from
    param_dist = {"max_depth": [3, None],
                  "max_features": sp_randint(1, 11),
                  "min_samples_split": sp_randint(2, 11),
                  "min_samples_leaf": sp_randint(1, 11),
                  "bootstrap": [True, False],
                  "criterion": ["gini", "entropy"]}
    # run randomized search
    n_iter_search = RandomizedSearchCV(clf, param_distributions=param_dist,
                                       n_iter=n_iter_search)
    start = time()
    random_search.fit(X_test, y_test)
    print("RandomizedSearchCV took %.2f seconds for %d candidates"
          " parameter settings." % ((time() - start), n_iter_search))
    report(random_search.cv_results_)
    # use a full grid over all parameters
    param_grid = {"max_depth": [3, None],
                  "max_features": [1, 3, 10],
                  "min_samples_split": [2, 3, 10],
                  "bootstrap": [True, False],
                  "min_samples_leaf": [1, 3, 10],
                  "criterion": ["gini", "entropy"]}

    # run grid search
    grid_search = GridSearchCV(clf, param_grid=param_grid)
    start = time()
    grid_search.fit(X_test, y_test)
    print("GridSearchCV took %.2f seconds for %d candidate parameter settings."
          % (time() - start, len(grid_search.cv_results_['params'])))
    report(grid_search.cv_results_)
    return grid_search

from sklearn.cluster import KMeans
import numpy as np
def kmeans_professores(df,ncl,rs=0):
    scaler = MinMaxScaler()
    data = df.values
    scaler.fit(data)
    X = scaler.transform(data)

    kmeans = KMeans(n_clusters=ncl, random_state=rs).fit(X)
    return kmeans




def print_confusion_matrix(confusion_matrix, class_names, figsize = (10,7), fontsize=14):
    """Prints a confusion matrix, as returned by sklearn.metrics.confusion_matrix, as a heatmap.

    Arguments
    ---------
    confusion_matrix: numpy.ndarray
        The numpy.ndarray object returned from a call to sklearn.metrics.confusion_matrix.
        Similarly constructed ndarrays can also be used.
    class_names: list
        An ordered list of class names, in the order they index the given confusion matrix.
    figsize: tuple
        A 2-long tuple, the first value determining the horizontal size of the ouputted figure,
        the second determining the vertical size. Defaults to (10,7).
    fontsize: int
        Font size for axes labels. Defaults to 14.

    Returns
    -------
    matplotlib.figure.Figure
        The resulting confusion matrix figure
    """
    df_cm = pd.DataFrame(
        confusion_matrix, index=class_names, columns=class_names,
    )
    fig = plt.figure(figsize=figsize)
    try:
        heatmap = sns.heatmap(df_cm, annot=True, fmt="d")
    except ValueError:
        raise ValueError("Confusion matrix values must be integers.")
    heatmap.yaxis.set_ticklabels(heatmap.yaxis.get_ticklabels(), rotation=0, ha='right', fontsize=fontsize)
    heatmap.xaxis.set_ticklabels(heatmap.xaxis.get_ticklabels(), rotation=45, ha='right', fontsize=fontsize)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    return fig


from scipy.cluster.hierarchy import dendrogram, linkage
from matplotlib import pyplot as plt

def hirarquical_cluster(df,classes):
    linked = linkage(df.values, 'single')

    labelList = classes

    plt.figure(figsize=(10, 7))
    dendrogram(linked,
                orientation='top',
                labels=labelList,
                distance_sort='descending',
                show_leaf_counts=True)
    plt.show()




def za_km_minibatch(nc,df):
    km = MiniBatchKMeans(n_clusters=nc, random_state=25 ).fit(df)
    return km


def clusteriza_dbscan(df):
    X = MinMaxScaler().fit_transform(df.values)

    # #############################################################################
    # Compute DBSCAN
    db = DBSCAN(eps=0.3, min_samples=10).fit(X)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    print('Estimated number of clusters: %d' % n_clusters_)
    print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
    print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
    print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
    print("Adjusted Rand Index: %0.3f"
          % metrics.adjusted_rand_score(labels_true, labels))
    print("Adjusted Mutual Information: %0.3f"
          % metrics.adjusted_mutual_info_score(labels_true, labels))
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(X, labels))
    return labels
