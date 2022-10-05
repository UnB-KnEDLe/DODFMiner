import pandas as pd
import json
import joblib
import re
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')

class Licitacao():

    def __init__(self, file, backend):
        self.filename = file
        self.file = file
        self.backend = backend
        self.model = None
        self.texts = []
        self.preds = []
        self.df = []
        self.flow()


    def flow(self):
        self.load()
        self.pre_process()
        self.ner_extraction()
        self.post_process()
        return self.df
    
    
    def load(self):
        self.model = joblib.load('./models/licitacao.pkl')
        if self.file[-5:] == '.json':
            with open(self.file, 'r') as f:
                self.file = json.load(f)
            self.file = self.segment(self.file)
        else:
            pass


    def segment(self, file):
        atos_licitacao = []

        try:
            section_3 = file['json']['INFO']['Seção III']

            for orgao in section_3:
                for documento in section_3[orgao]:
                    for ato in section_3[orgao][documento]:
                        if "licitação" in section_3[orgao][documento][ato]['titulo'].lower():
                            atos_licitacao.append(re.sub(r'<[^>]*>', '', section_3[orgao][documento][ato]['texto']))

        except KeyError:
            print("Chave 'Seção III' não encontrada")
            print(f"Chaves existentes: {file['json']['INFO'].keys()}")

        return atos_licitacao


    def pre_process(self):
        self.texts = self.file
        self.file = [word_tokenize(x) for x in self.file]
        self.file = [self.get_features(x) for x in self.file]
        

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


    def ner_extraction(self):
        for t in self.file:
          pred = self.model.predict([t])
          pred = pred[0]
          self.preds.append(pred)


    def post_process(self):

        for IOB, text in zip(self.preds, self.texts):

            ent_dict = {
              'ato': '',
              'dodf': '',
              'treated_text': '', 
              'IOB': ''
            } 

            ent_dict['ato'] = 'LICITAÇÃO'
            ent_dict['dodf'] = self.filename
            ent_dict['treated_text'] = text
            ent_dict['IOB'] = IOB

            entities = []

            text_split = word_tokenize(text)

            ent_concat = ('', '')

            for ent, word in zip(IOB, text_split):
              if ent[0] == 'B':
                ent_concat = (ent[2:len(ent)], word)
              elif ent[0] == 'I':
                ent_concat = (ent_concat[0], ent_concat[1] + ' ' + word)
              elif ent[0] == 'O':
                if ent_concat[1] != '':
                  entities.append(ent_concat)
                  ent_concat = ('', '')

            for tup in entities:

              if tup[0] not in ent_dict:
                ent_dict[tup[0]] = tup[1]
              elif type(ent_dict[tup[0]]) != list:
                aux = []
                aux.append(ent_dict[tup[0]])
                aux.append(tup[1])
                ent_dict[tup[0]] = aux
              else:
                ent_dict[tup[0]].append(tup[1])

            self.df.append(ent_dict)

        self.df = pd.DataFrame(self.df)
        self.df.to_csv('result.csv',na_rep='NaN')
