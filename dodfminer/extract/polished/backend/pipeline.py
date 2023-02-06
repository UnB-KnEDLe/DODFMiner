#pipeline imports
from sklearn.base import TransformerMixin, BaseEstimator
from nltk.tokenize import word_tokenize

class feature_extractor(TransformerMixin):
  def __init__(self):
    # print(">>>> init() Transformer called.\n")
    pass

  def get_features(self, sentence):
    sent_features = []
    for i in range(len(sentence)):
      word_feat = {
        # Palavra atual
        'word': sentence[i].lower(),
        'capital_letter': sentence[i][0].isupper(),
        'all_capital': sentence[i].isupper(),
        'isdigit': sentence[i].isdigit(),
        # Uma palavra antes
        'word_before': '' if i == 0 else sentence[i-1].lower(),
        'word_before_isdigit': '' if i == 0 else sentence[i-1].isdigit(),
        'word_before_isupper': '' if i == 0 else sentence[i-1].isupper(),
        'word_before_istitle': '' if i == 0 else sentence[i-1].istitle(),
        # Uma palavra depois
        'word_after': '' if i+1 >= len(sentence) else sentence[i+1].lower(),
        'word_after_isdigit': '' if i+1 >= len(sentence) else sentence[i+1].isdigit(),
        'word_after_isupper': '' if i+1 >= len(sentence) else sentence[i+1].isupper(),
        'word_after_istitle': '' if i+1 >= len(sentence) else sentence[i+1].istitle(),

        'BOS': i == 0,
        'EOS': i == len(sentence)-1
      }
      sent_features.append(word_feat)
    return sent_features

  def tokenize(self, sentence):
    text = word_tokenize(sentence)
    return text

  def fit(self, X, y = None):
    # print(">>>> fit() Transformer called.\n")
    return self

  def transform(self, X, y = None):
    # print(">>>> transform() Transformer called.\n")
    transformed = []
    for x in X:
      tokens = self.tokenize(x)
      features = self.get_features(tokens)
      transformed.append(features)
    return transformed

class PipelineCRF(BaseEstimator):

    def __init__(self, model):
        # print(">>>> init() Estimator called.\n")
        self.crf = model

    # This method will not be used in the default pipeline
    def fit(self, X, y):
        # print(">>>> fit() Estimator called.\n")
        # print("Training...\n")
        self.crf.fit(X, y)
        # print("Done!\n")
        return self

    def predict(self, x):
        # print(">>>> predict() Estimator called.\n")
        pred = self.crf.predict(x)
        return pred

