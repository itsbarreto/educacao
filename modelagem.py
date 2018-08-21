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


def processa_tudo(model_vars,grid_search=False):
    X_train, X_test, y_train, y_test = gera_datasets(model_vars)
    if grid_search:
        clf = modela_gs_cv(X_test,y_test,RandomForestClassifier(random_state=123))
    else:
        clf = modela(X_train,y_train)
    return avalia(X_test,y_test,X_train,y_train, clf,model_vars.drop('target',axis=1).columns)



def gera_datasets(model_vars,balanceia = True):
    if balanceia:
        md = model_vars.loc[model_vars.target == 0].sample(sum(model_vars.target.values),random_state=42).append(model_vars.loc[model_vars.target == 1])
    else:
        md = model_vars.copy()
    X = md.drop('target',axis=1).values
    y = md.target.values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

    scaler = MinMaxScaler()
    scaler.fit(X_train)
    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)
    return X_train, X_test, y_train, y_test

def modela(X_train,y_train):
    clf = RandomForestClassifier(random_state=0)
    clf.fit(X_train,y_train)
    return clf

def avalia(X_test,y_test,X_train,y_train, clf,cols):
    y_pred = clf.predict(X_test)
    display(confusion_matrix(y_test, y_pred))
    print('Base de TREINO')
    print(classification_report(y_train, clf.predict(X_train)))
    print('Base de TESTE')
    print(classification_report(y_test, y_pred))
    try:
        y_pred_proba = clf.predict_proba(X_test)[::,1]
        fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred_proba)
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
        std = np.std([tree.feature_importances_ for tree in clf.estimators_],
                     axis=0)
        indices = np.argsort(importances)[::-1]
        for f in range(X_test.shape[1]):
            fi.append(cols[indices[f]])
            print("%d. feature %s (%f)" % (f + 1, cols[indices[f]], importances[indices[f]]))

        # Plot the feature importances of the forest
        plt.figure()
        plt.title("Feature importances")
        plt.bar(range(X_test.shape[1]), importances[indices],
               color="r", yerr=std[indices], align="center")
        plt.xticks(range(X_test.shape[1]), indices)
        plt.xlim([-1, X_test.shape[1]])
        plt.show()
    except:
        print('Nao foi possivel mostrar o feature importance.')
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
            print("")



def modela_gs_cv(X_test,y_test,clf):

    # specify parameters and distributions to sample from
    param_dist = {"max_depth": [3, None],
                  "max_features": sp_randint(1, 11),
                  "min_samples_split": sp_randint(2, 11),
                  "min_samples_leaf": sp_randint(1, 11),
                  "bootstrap": [True, False],
                  "criterion": ["gini", "entropy"]}

    # run randomized search
    n_iter_search = 20
    random_search = RandomizedSearchCV(clf, param_distributions=param_dist,
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
                  "min_samples_leaf": [1, 3, 10],
                  "bootstrap": [True, False],
                  "criterion": ["gini", "entropy"]}

    # run grid search
    grid_search = GridSearchCV(clf, param_grid=param_grid)
    start = time()
    grid_search.fit(X_test, y_test)
    print("GridSearchCV took %.2f seconds for %d candidate parameter settings."
          % (time() - start, len(grid_search.cv_results_['params'])))
    report(grid_search.cv_results_)
    return grid_search
