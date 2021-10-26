import nltk
import numpy as np
import joblib

#from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer

class Committee:
    def __init__(self):
        self.pipe = make_pipeline(FunctionTransformer(self.remove_not_words),
                             FunctionTransformer(self.embedding),
                             FunctionTransformer(self.predict),
                             FunctionTransformer(self.get_new_labels))
        
        nltk.download('punkt', quiet = True)
        nltk.download('rslp', quiet = True)
        nltk.download('stopwords', quiet = True)
        
        self.stopwords = nltk.corpus.stopwords.words('portuguese')
        self.stemmer = nltk.stem.RSLPStemmer()

    def load_models(self, path):
        with open(path, 'rb') as file:
            self.clfs = joblib.load(file)
            self.vectorizer = joblib.load(file)
            self.vectorizer.tokenizer = self.tokenize
        
    def transform(self, X, y):
        self.y = y
        
        return self.pipe.transform(X)
    
    def tokenize(self, text):
        tokens = [word.lower() for word in nltk.word_tokenize(text) if len(word) > 1]
        return [self.stemmer.stem(item) for item in tokens if item not in self.stopwords]

    def remove_not_words(self, text):
        return text.str.replace(r'\w*\d\w*|\W', ' ', regex = True).str.lower()

    def embedding(self, text):
        return self.vectorizer.transform(text)

    def predict(self, text):
        results = []
        for clf in self.clfs:
            predicted = clf.predict(text)
            results.append(predicted)

        return np.array(results).T
        
    def get_new_labels(self, results):
        new_types = []
        for i in range(0, len(results)):
            d = dict(zip(*np.unique(results[i], return_counts=True)))
            r = max(d, key = d.get)
            if d[r] >= 0.5 and r != self.y[i]:
                new_types.append(r)
            else:
                new_types.append(self.y[i])
        return new_types