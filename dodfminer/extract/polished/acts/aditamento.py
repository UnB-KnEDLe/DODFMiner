import pandas as pd
import json
import joblib
import re
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')

from dodfminer.extract.polished.acts.base import Atos

class Aditamento(Atos):

    def __init__(self, file, backend):
        self.file = file
        self.backend = backend
        self.model = None
        self.df = {'texto': [], 'IOB': []}
        self.flow()


    def flow(self):
        self.load()
        self.pre_process()
        self.ner_extraction()
        self.post_process()
        return self.df
    
    
    def load(self):
        self.model = joblib.load('./models/aditamento.pkl')
        if self.file[-5:] == '.json':
            with open(self.file, 'r') as f:
                self.file = json.load(f)
            self.file = self.segment(self.file)
        else:
            pass
        return


    def segment(self, file):
        atos_aditamento = []

        try:
            section_3 = file['json']['INFO']['Seção III']

            for orgao in section_3:
                for documento in section_3[orgao]:
                    for ato in section_3[orgao][documento]:
                        if "aditamento" in section_3[orgao][documento][ato]['titulo'].lower():
                            atos_aditamento.append(re.sub(r'<[^>]*>', '', section_3[orgao][documento][ato]['texto']))

        except KeyError:
            print("Chave 'Seção III' não encontrada")
            print(f"Chaves existentes: {file['json']['INFO'].keys()}")

        return atos_aditamento


    def pre_process(self):
        self.df['texto'] = self.file
        self.file = [word_tokenize(x) for x in self.file]
        self.file = [self.get_features(x) for x in self.file]
        return
        

    def get_features(self, sentence):
        
        sent_features = []
        for i in range(len(sentence)):
            # print(sentence[i])
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


    def ner_extration(self):
        for t in self.file:
            self.df['IOB'].append(self.model.predict(t))


    def post_process(self):
        self.df = pd.DataFrame(self.df)
