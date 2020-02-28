import math
from typing import Dict, List

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import wordpunct_tokenize


class NLProcessor:
    stemmer = PorterStemmer()
    stopwords = set(stopwords.words('english'))
    stopwords.update(['.', ',', '.,', '-', '–', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}'])
    stopwords.update(['$', '%', '#', '/', '‘', '’', '“', '”', '·', '`'])

    @staticmethod
    def split_sentence(sentence: str):
        return wordpunct_tokenize(sentence)

    @staticmethod
    def norm_word(word: str):
        word = word.lower()
        if word in NLProcessor.stopwords:
            return None

        return NLProcessor.stemmer.stem(word)


class NaiveBayesClassifier:
    def __init__(self, alpha=.01, classes_n=3, labels_str: List[str] = None):
        self.alpha = alpha

        self.labels_n = classes_n
        self.labels_total = [0 for _ in range(self.labels_n)]
        self.labels_words = [0 for _ in range(self.labels_n)]
        self.labels_prior = [0. for _ in range(self.labels_n)]

        if labels_str is None:
            labels_str = ['good', 'maybe', 'never']

        labels_str.sort()
        self.labels_definition: Dict[str, int] = dict([(labels_str[i], i) for i in range(classes_n)])

        self.word_frequency: Dict[str, List[int]] = {}
        self.word_likelihood: Dict[str, List[float]] = {}

    def fit(self, X: List[str], y: List[str]):
        """ Fit Naive Bayes classifier according to X, y. """

        for i in range(len(X)):
            word_label = self.labels_definition[y[i]]
            self.labels_total[word_label] += 1

            for word in NLProcessor.split_sentence(X[i]):
                word = NLProcessor.norm_word(word)
                if word is None:
                    continue

                if word not in self.word_frequency:
                    self.word_frequency[word] = [0 for _ in range(self.labels_n)]
                    self.labels_words[word_label] += 1

                self.word_frequency[word][word_label] += 1

        sum_classes = sum(self.labels_total)
        sum_words = len(self.word_frequency)

        for word, freq in self.word_frequency.items():
            self.word_likelihood[word] = [0 for _ in range(self.labels_n)]
            for i in range(self.labels_n):
                self.word_likelihood[word][i] = (freq[i] + self.alpha) / (self.labels_words[i] + self.alpha * sum_words) * 1000

        for i in range(self.labels_n):
            self.labels_prior[i] = math.log(self.labels_total[i] / sum(self.labels_total))

    def predict(self, X):
        """ Perform classification on an array of test vectors X. """
        predicts = []

        for i in range(len(X)):
            probabilities = self.labels_prior.copy()

            for word in NLProcessor.split_sentence(X[i]):
                word = NLProcessor.norm_word(word)

                if word in self.word_likelihood:
                    for i in range(self.labels_n):
                        probabilities[i] += math.log(self.word_likelihood[word][i])

            decision = probabilities.index(max(probabilities))
            for label, label_index in self.labels_definition.items():
                if decision == label_index:
                    predicts.append(label)

        return predicts

    def score(self, X_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        prediction = self.predict(X_test)
        corrects = sum([1 for i in range(len(prediction)) if prediction[i] == y_test[i]])
        return corrects / len(y_test)
