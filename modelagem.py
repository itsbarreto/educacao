import pandas as  pd
import numpy as np
from matplotlib import pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score


def processa_tudo(model_vars):
    X_train, X_test, y_train, y_test = gera_datasets(model_vars)
    clf = modela(X_train,y_train)
    return avalia(X_test,y_test, clf,model_vars.drop('target',axis=1).columns)

def gera_datasets(model_vars):
    X = model_vars.drop('target',axis=1).values
    y = model_vars.target.values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=42)

    return X_train, X_test, y_train, y_test

def modela(X_train,y_train):
    clf = RandomForestClassifier(random_state=0)
    clf.fit(X_train,y_train)
    return clf

def avalia(X_test,y_test, clf,cols):
    y_pred = clf.predict(X_test)
    display(confusion_matrix(y_test, y_pred))
    importances = clf.feature_importances_
    std = np.std([tree.feature_importances_ for tree in clf.estimators_],
                 axis=0)
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    print("Feature ranking:")
    fi = []
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
    display(precision_score(y_test, y_pred, average='macro')  )

    display(precision_score(y_test, y_pred, average='micro')  )

    display(precision_score(y_test, y_pred, average='weighted'))


    display(precision_score(y_test, y_pred, average=None)  )

    return fi
