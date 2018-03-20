
# coding: utf-8

# In[1]:

# k_fold_cross_validation


# In[3]:

from __future__ import print_function

import datetime

import pandas as pd
import sklearn

from sklearn import cross_validation
from sklearn.metrics import confusion_matrix
from sklearn.svm import SVC

from QuantModels.forecaster import create_lagged_series


# In[4]:

if __name__ == "__main__":
    # Create a lagged series of the S&P500 US stock market index
    snpret = create_lagged_series("^GSPC", datetime.datetime(2001,1,10), datetime.datetime(2005,12,31), lags=5)
    
    # Use the prior two days of returns as predictor values, with direction as the response
    X = snpret[["Lag1", "Lag2"]]
    y = snpret["Direction"]
    
    # Create a k-fold cross-validation object
    kf = cross_validation.KFold(len(snpret), n_folds=10, indices=False, shuffle=True, random_state=42)
    
    # Use the kf object to create index arrays that state which elements have been retained
    # for training and which elements have been retained for testing, for each k-element iteration
    for train_index, test_index in kf:
        
        X_train = X.ix[X.index[train_index]]
        X_test = X.ix[X.index[test_index]]
        y_train = y.ix[y.index[train_index]]
        y_test = y.ix[y.index[test_index]]
        
        # In this instance, only use the Radial Support Vector Machine (SVM)
        print("Hit Rates/Confusion Matrices:")
        model = SVC(C=1000000.0, cache_size=200, class_weight=None, coef0=0.0, degree=3,
                    gamma=0.0001, kernel='rbf', max_iter=-1, probability=False, randome_state=None,
                    shrinking=True, tol=0.001, verbose=False)
        
#         models = [("LR", LogisticRegression()),
#                   ("LDA", LDA()),
#                   ("QDA", QDA()),
#                   ("LinearSVC", LinearSVC()),
#                   ("RSVM", SVC(
#                       C=1000000.0, cache_size=200, class_weight=None, coef0=0.0, degree=3,
#                       gamma=0.0001, kernel='rbf', max_iter=-1, probability=False, randome_state=None,
#                       shrinking=True, tol=0.001, verbose=False)),
#                   ("RF", RandomForestClassifier(
#                       n_estimators=1000, criterion='gini', max_depth=None, min_samples_split=2,
#                       min_samples_leaf=1, max_features='auto', bootstrap=True, oob_score=False,
#                       n_jobs=1, random_state=None, verbose=0)
#                   )
#                  ]
    
#     # Iterate through the models
#     for m in models:
        
        # Train each of the models on the training set
        model.fit(X_train, y_train)
        
        # Make an array of predictions on the test set
        pred = m.predict(X_test)
        
        # Output the hit-rate and the confusion matrix
        print("%0.3f" % model.score(X_test, y_test))
        print("%s\n" % confusion_matrix(pred, y_test))


# In[ ]:



