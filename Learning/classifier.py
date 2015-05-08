from __future__ import print_function

try:
    import unicodecsv as csv
except ImportError:
    import warnings

    warnings.warn("can't import `unicodecsv` encoding errors may occur")
    import csv

from collections import namedtuple
from sklearn import datasets
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn import cross_validation
import numpy as np
import os
# from sklearn.datasets import fetch_20newsgroups

fields = ("video_id", "author", "comment", "helpfulness", "length_of_text")

CLASS1 = 'relevant'
CLASS2 = 'non_relevant'


# See https://districtdatalabs.silvrback.com/simple-csv-data-wrangling-with-python
class CommentRecord(namedtuple('CommentRecord_', fields)):
    @classmethod
    def parse(cls, row):
        row = list(row)  # Make row mutable
        row[4] = int(row[4])
        row[3] = int(row[3])
        return cls(*row)

    def __str__(self):
        return "{1} with comment {2}".format(self.author, self.comment)


def read_comment_data(path):
    with open(path, 'rU') as data:
        data.readline()  # Skip the header
        reader = csv.reader(data, delimiter='|')  # Create a regular tuple reader
        for row in map(CommentRecord.parse, reader):
            yield row


def run_test(clf, rel_train, rel_test):
    train_data = rel_train.data

    if clf == '1':
        print("Predicting using Multinomial Naive Bayes!\n")
        text_clf = Pipeline([('vect', TfidfVectorizer()), ('tfidf', TfidfTransformer()), ('clf', MultinomialNB())])
        clf_descr = "MultinomialNB"
    elif clf == '2':
        print("Predicting using SVM with stochastic gradient descent!\n")
        text_clf = Pipeline([('vect', TfidfVectorizer()), ('tfidf', TfidfTransformer()), ('clf', SGDClassifier())])
        clf_descr = "SDGClassifier"

    else:
        print("That is not a classifier!\n")
        exit(1)

    scores = cross_validation.cross_val_score(text_clf, train_data, rel_train.target, cv=5)
    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
    text_clf = text_clf.fit(train_data, rel_train.target)

    test_data = rel_test.data
    predicted = text_clf.predict(test_data)

    mean = np.mean(predicted == rel_test.target)
    print("The mean is : {0}".format(mean))

    print(metrics.classification_report(rel_test.target, predicted, target_names=rel_test.target_names))
    print(metrics.confusion_matrix(rel_test.target, predicted))

    return clf_descr, mean


if __name__ == "__main__":
    train = os.path.realpath('./train_data')
    test = os.path.realpath('./test_data')
    rel_train = datasets.load_files(train)
    rel_test = datasets.load_files(test)
    results = []

    results.append(run_test('1', rel_train, rel_test))
    results.append(run_test('2', rel_train, rel_test))
    # results.append(run_test('1', twenty_train, twenty_test))
    # results.append(run_test('2', twenty_train, twenty_test))


    # length_of_review_texts = []
    # helpfulness = []
    # for row in read_comment_data("jblow888_rel.csv"):
    #
    # length_of_review_texts.append(row[4])
    #     helpfulness.append(row[3])
    #
    # # Used to calculate pearson correlation
    # pearson = numpy.corrcoef(length_of_review_texts, helpfulness)[0, 1]
    # print(pearson)
    #
    # # Histogram of length of comments
    # plt.hist(length_of_review_texts, 200)
    # plt.title("Length of Comment")
    # plt.xlabel("Number of characters in comment")
    # plt.ylabel("Number of Commenters")
    # plt.show()
    #
    # # Scatterplot of length of review text vs. helpfulness
    # plt.scatter(helpfulness, length_of_review_texts)
    # plt.title("Length of Review Text vs. Helpfulness")
    # plt.xlabel("Helpfulness")
    # plt.ylabel("Length of Review Text")
    # plt.show()
