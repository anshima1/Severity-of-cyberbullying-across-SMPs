import pickle, numpy as np
import preprocessor as p
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.utils import shuffle
from sklearn.svm import SVC, LinearSVC
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split, KFold
from sklearn.metrics import classification_report, f1_score, accuracy_score, confusion_matrix, make_scorer, recall_score, precision_score, classification_report, precision_recall_fscore_support
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble  import GradientBoostingClassifier, RandomForestClassifier
HASH_REMOVE = None
NO_OF_FOLDS = 10
WORD = False
N_CLASS = 4
def load_data(filename):
    data = pickle.load(open(filename, 'rb'))
    x_text = []
    labels = []
    for i in range(len(data)):
        if(HASH_REMOVE):
            x_text.append(p.tokenize((data[i][1]).encode('utf-8')))
        else:
            x_text.append(data[i][1])
        labels.append(data[i][2])
    return x_text,labels

def get_model(m_type):
    if m_type == 'lr':
        logreg = LogisticRegression(class_weight="balanced")
    elif m_type == 'naive':
        logreg =  MultinomialNB()
    elif m_type == "random_forest":
        logreg = RandomForestClassifier(n_estimators=100, n_jobs=-1)
    elif m_type == "svm":
        logreg = LinearSVC(class_weight="balanced")
    else:
        print ("ERROR: Please specify a correst model")
        return None
    return logreg

def train(x_text, labels, MODEL_TYPE):

    if(WORD):
        print("Using word based features")
        bow_transformer = CountVectorizer(analyzer="word",max_features = 10000,stop_words='english').fit(x_text)
        comments_bow = bow_transformer.transform(x_text)
        tfidf_transformer = TfidfTransformer(norm = 'l2').fit(comments_bow)
        comments_tfidf = tfidf_transformer.transform(comments_bow)
        features = comments_tfidf
        #print(features)
    else:
        print("Using char n-grams based features")
        bow_transformer = CountVectorizer(max_features = 10000, ngram_range = (1,2)).fit(x_text)
        comments_bow = bow_transformer.transform(x_text)
        tfidf_transformer = TfidfTransformer(norm = 'l2').fit(comments_bow)
        comments_tfidf = tfidf_transformer.transform(comments_bow)
        features = comments_tfidf
        #print(features)

        dict1 = {'L':0,'M':1,'H':2,'none':3}
        labels = np.array([dict1[b] for b in labels])
        print (labels)
    from collections import Counter
    print(Counter(labels))
    classification_model(features, labels, model_type)
    #
    # if(MODEL_TYPE != "all"):
    #     classification_model(features, labels, MODEL_TYPE)
    # else:
    #     for model_type in models:
    #         classification_model(features, labels, model_type)


def get_scores(y_true, y_pred):
#     if(data=="wiki"):
#         auc = roc_auc_score(y_true,y_pred)
#         print('Test ROC AUC: %.3f' %auc)
#     print(":: Confusion Matrix")
#     print(confusion_matrix(y_true, y_pred))
#     print(":: Classification Report")
#     print(classification_report(y_true, y_pred))
    return np.array([
            precision_score(y_true, y_pred, average=None),
            recall_score(y_true, y_pred,  average=None),
            f1_score(y_true, y_pred, average=None)])

def print_scores(scores):
    for i in range(N_CLASS):
        if(i!=0):
            print ("Precision Class %d (avg): %0.3f (+/- %0.3f)" % (i,scores[:, i].mean(), scores[:, i].std() * 2))
            print ("Recall Class %d (avg): %0.3f (+/- %0.3f)" % (i,scores[:,  N_CLASS+i].mean(), scores[:,N_CLASS+i].std() * 2))
            print ("F1_score Class %d (avg): %0.3f (+/- %0.3f)" % (i,scores[:, N_CLASS*2+i].mean(), scores[:,  N_CLASS*2+i].std() * 2))

def classification_model(X, Y, model_type):
    X, Y = shuffle(X, Y, random_state=42)
    print ("Model Type:", model_type)
    kf = KFold(n_splits=NO_OF_FOLDS)
    scores = []
    for train_index, test_index in kf.split(X):
        Y = np.asarray(Y)
        model = get_model(model_type)
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = Y[train_index], Y[test_index]
        model.fit(X_train,y_train)
        y_pred = model.predict(X_test)
        curr_scores = get_scores(y_test, y_pred)
        scores.append(np.hstack(curr_scores))
    print_scores(np.array(scores))


x = "C:/Users/kavita/Desktop/BTP_Downloads/twitterp.pkl"
x_text,labels = load_data(x)
model_type='random_forest'
train(x_text, labels, "all")