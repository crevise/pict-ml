import pandas
from time import time
from sklearn.preprocessing import MinMaxScaler
from sklearn.cross_validation import train_test_split
import numpy as np
from sklearn import svm

#
# Learning set created using the normal rows like so:
#       head -n 200000 kdd_cup.data_corrected | grep 'normal.' > kddcup.data_cv
# Random test set created as:
#       shuf -n 100000 kdd_cup.data_corrected > kddcup.data_test
#


def loadDataFile(filename):
    col_names = ["duration","protocol_type","service","flag","src_bytes",
        "dst_bytes","land","wrong_fragment","urgent","hot","num_failed_logins",
        "logged_in","num_compromised","root_shell","su_attempted","num_root",
        "num_file_creations","num_shells","num_access_files","num_outbound_cmds",
        "is_host_login","is_guest_login","count","srv_count","serror_rate",
        "srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate",
        "diff_srv_rate","srv_diff_host_rate","dst_host_count","dst_host_srv_count",
        "dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate",
        "dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate",
        "dst_host_rerror_rate","dst_host_srv_rerror_rate","label"]
    kdd_data_10percent = pandas.read_csv(filename, header=None, names = col_names)
    # kdd_data_10percent.describe()
    # kdd_data_10percent['label'].value_counts()
    num_features = [
        "duration","src_bytes",
        "dst_bytes","land","wrong_fragment","urgent","hot","num_failed_logins",
        "logged_in","num_compromised","root_shell","su_attempted","num_root",
        "num_file_creations","num_shells","num_access_files","num_outbound_cmds",
        "is_host_login","is_guest_login","count","srv_count","serror_rate",
        "srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate",
        "diff_srv_rate","srv_diff_host_rate","dst_host_count","dst_host_srv_count",
        "dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate",
        "dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate",
        "dst_host_rerror_rate","dst_host_srv_rerror_rate"
    ]
    kdd_data_10percent['label'][kdd_data_10percent['label']!='normal.'] = 'attack.'
    features = kdd_data_10percent[num_features].astype(float)
    features_train, features_test, labels_train, labels_test = train_test_split(features[num_features], kdd_data_10percent['label'], test_size=0.1, random_state=42)
    features_train.apply(lambda x: MinMaxScaler().fit_transform(x))
    features_test.apply(lambda x: MinMaxScaler().fit_transform(x))
    labels = kdd_data_10percent['label'].copy()
    lables_train = labels[:len(features_train)]
    labels_test = labels[len(features_train):]
    return features_train, features_test, labels_train, labels_test

if __name__=='__main__':
    X, Xtest, Y, Ytest = loadDataFile("kddcup.data_cv")
    # Tune these arguments for tweaking the result
    clf = svm.OneClassSVM(nu=0.5, kernel="poly", degree=2, gamma=0.1)
    clf.fit(X)
    y_pred_train = clf.predict(X)
    y_pred_test = clf.predict(Xtest)
    correct = 0
    wrong = 0

    for (i,), value in np.ndenumerate(Ytest):
        if y_pred_test[i] == 1.0 and value == 'normal.':
            correct += 1
        elif y_pred_test[i] == -1.0 and value == 'attack.':
            correct += 1
        else:
            wrong += 1
    print 'Train set correct:', correct, 'wrong:', wrong
    
    correct = 0
    false_positive = 0
    true_negative = 0
    X, Xtest, Y, Ytest = loadDataFile("kddcup.data_test")
    y_pred_train = clf.predict(X)
    for (i,), value in np.ndenumerate(Y):
        if y_pred_train[i] == 1.0 and value == 'normal.':
            correct += 1
        elif y_pred_train[i] == -1.0 and value == 'attack.':
            correct += 1
        elif y_pred_train[i] == -1.0 and value == 'normal.':
            false_positive += 1
        else:
            true_negative += 1
    print 'Test set correct:', correct, 'false postive: ', false_positive, 'true negative: ', true_negative
    

