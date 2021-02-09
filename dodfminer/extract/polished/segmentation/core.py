import torch
import os
from torch import nn
import numpy as np
import torch
import nltk
from nltk.tokenize import sent_tokenize
from torch.nn.utils.rnn import pad_sequence 
import unicodedata
import joblib
import gdown

model_cover_list = ['Aposentadoria']


class word_cnn(nn.Module):
    """single layer CNN with: filters=50, kernel_size=3, dropout=0.5"""
    def __init__(self, embedding_dim, embedding_size=None, pretrained_word_emb=None, pad_idx = 929606):
        super(word_cnn, self).__init__()
        assert (embedding_size or pretrained_word_emb), 'Undefined embedding for the word level CNN'

        if pretrained_word_emb:
            self.embedding = nn.Embedding.from_pretrained(torch.FloatTensor(pretrained_word_emb.vectors))
            self.embedding.padding_idx = pad_idx
        else:
            self.embedding = nn.Embedding(num_embeddings=embedding_size, embedding_dim=embedding_dim, padding_idx=pad_idx)

        self.conv = nn.Conv1d(in_channels=embedding_dim, out_channels=200, kernel_size=3, stride=1, padding=2)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.5)

    def forward(self, x):
        x = self.embedding(x)
        shape = x.shape
        x = self.conv(x.view([shape[0]*shape[1], shape[2], shape[3]]).permute(0, 2, 1))
        x = self.dropout(self.relu(x))
        x = torch.nn.functional.max_pool1d(x, kernel_size=x.shape[2]).squeeze()
        return x.view([shape[0], shape[1], -1])

class sentence_cnn(nn.Module):
    """two-layer CNN, filter=800, kernel=5"""
    def __init__(self, in_channels=200):
        super(sentence_cnn, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=in_channels, out_channels=800, kernel_size=5, padding=2)
        self.conv2 = nn.Conv1d(in_channels=800, out_channels=800, kernel_size=5, padding=2)
        self.relu  = nn.ReLU()
        self.dropout = nn.Dropout(p=0.5)

    def forward(self, x):
        w = x.clone()
        # Go through 2 conv layers
        x = self.conv1(x.permute(0, 2, 1))
        x = self.dropout(self.relu(x))
        x = self.conv2(x)
        x = self.relu(x)
        x = x.permute(0, 2, 1)
        return torch.cat((x, w), dim=2)

class decoder(nn.Module):
    def __init__(self, feature_size, num_classes, device):
        super(decoder, self).__init__()
        self.device = device
        self.num_classes = num_classes
        self.lstm = torch.nn.LSTM(feature_size+num_classes, 256)
        self.linear = torch.nn.Linear(256, num_classes)
        self.dropout = torch.nn.Dropout(p=0.5)
        self.loss_fn = torch.nn.CrossEntropyLoss(ignore_index = -1, reduction='sum')
    
    def forward_step(self, x, prev_tag, prev_lstm_state):
        prev_tag_onehot = torch.nn.functional.one_hot(prev_tag, num_classes=self.num_classes).to(self.device)
        lstm_input = torch.cat((x, prev_tag_onehot), dim=1).unsqueeze(dim=0)
        lstm_output, lstm_state = self.lstm(lstm_input, prev_lstm_state)
        linear_output = self.linear(lstm_output.squeeze(dim=0))
        prediction = torch.argmax(linear_output, dim=1)
        return linear_output, prediction, lstm_state
    
    def forward(self, x, tag):
        batch_size, seq_len, _ = x.size()
        x = x.permute(1, 0, 2)
        tag = tag.permute(1, 0)
        pred = torch.LongTensor([0 for i in range(batch_size)])
        lstm_state = None
        loss = 0.0
        # 50% chance word mask (dropout) to improve generalization
        x = self.dropout(x)
        for i in range(seq_len):
            output, pred, lstm_state = self.forward_step(x=x[i], prev_tag=pred, prev_lstm_state=lstm_state)
            loss += self.loss_fn(output, tag[i])
        return loss

    def decode(self, x):
        batch_size, seq_len, _ = x.size()
        x = x.permute(1, 0, 2)
        pred = torch.LongTensor([0 for i in range(batch_size)])
        lstm_state = None
        full_predictions = torch.LongTensor().to(self.device)
        full_output = torch.Tensor().to(self.device)
        for i in range(seq_len):
            output, pred, lstm_state = self.forward_step(x=x[i], prev_tag=pred, prev_lstm_state=lstm_state)
            full_predictions = torch.cat((full_predictions, pred.unsqueeze(dim=0)), dim=0)
            full_output = torch.cat((full_output, output.unsqueeze(dim=0)), dim=0)
        return full_predictions.permute(1, 0), full_output.permute(1, 0, 2)


class CNN_CNN_LSTM(nn.Module):
    def __init__(self, embedding_dim, decoder_feature_size, num_classes, device, embedding_size=None, pretrained_word_emb=None):
        super(CNN_CNN_LSTM, self).__init__()
        assert embedding_size or pretrained_word_emb, 'Undefined word embedding :('
        self.num_classes = num_classes
        if pretrained_word_emb:
            self.word_encoder = word_cnn(pretrained_word_emb=pretrained_word_emb, embedding_dim=embedding_dim)
        else:
            self.word_encoder = word_cnn(embedding_dim=embedding_dim, embedding_size=embedding_size)
        self.sent_encoder = sentence_cnn()
        self.decoder      = decoder(num_classes=num_classes, feature_size=decoder_feature_size, device=device)

    def forward(self, x, y):
        x = self.word_encoder(x)
        x = self.sent_encoder(x)
        x = self.decoder(x, y)
        return x

    def decode(self, x):
        x = self.word_encoder(x)
        x = self.sent_encoder(x)
        predictions, output = self.decoder.decode(x)
        return predictions, output

### Metrics

def relaxed_f1_score(model, dataloader, device):
    TP = [0 for _ in range(len(model.num_classes))]
    FP = [0 for _ in range(len(model.num_classes))]
    FN = [0 for _ in range(len(model.num_classes))]

    # for sent, tag, word, mask in dataloader:
        # sent = sent.to(device)
        # tag = tag.to(device)
        # word = word.to(device)
        # pred, _ = model.eval().decode(sent, word)
    print("Still ongoing development!")

def exact_f1_score(model, dataloader, device):
    TP = np.array([0 for _ in range((model.num_classes-2)//2)])
    FP = np.array([0 for _ in range((model.num_classes-2)//2)])
    FN = np.array([0 for _ in range((model.num_classes-2)//2)])

    for x, y, mask in dataloader:
        x = x.to(device)
        y = y.to(device)
        pred, _ = model.eval().decode(x)

        batch_size = pred.shape[0]
        for i in range(batch_size):
            predicted_entities = find_entities(pred[i])
            real_entities = find_entities(y[i])
            for entity in predicted_entities:
                if entity in real_entities:
                    TP[(entity[2]//2)-1] += 1
                else:
                    FP[(entity[2]//2)-1] += 1
            for entity in real_entities:
                if entity not in predicted_entities:
                    FN[(entity[2]//2)-1] += 1

    precision = TP/(TP+FP+0.000001)
    recall = TP/(TP+FN+0.000001)
    f1 = 2*(precision*recall)/(precision+recall)

    occurrences = TP + FN
    return occurrences, f1

def find_entities(tag):
    entities = []
    prev_tag = 1
    begin_entity = -1

    for i in range(len(tag)):
        # Check if current tag is new entity by checking if it's 'B-' of any class
        if tag[i]%2==0 and tag[i]>=2:
            if prev_tag >=2:
                entities.append((begin_entity, i-1, prev_tag-1))
            begin_entity = i
            prev_tag = tag[i]+1
        # Check if current tag is new entity (by comparing to previous tag)
        elif tag[i] != prev_tag:
            if prev_tag >= 2:
                entities.append((begin_entity, i-1, prev_tag-1))
            begin_entity = i
            prev_tag = tag[i]
    # Check if entity continues to the end of tensor tag
    if prev_tag >=2:
        entities.append((begin_entity, len(tag)-1, prev_tag-1))
    return entities

### Interface

def load_model(word2idx_path, model_path):
    """
    Load the trained model and the dictionary to convert words into integers (to be fed to the neural model)
    """
    dic = joblib.load(word2idx_path)
    word2idx = dic['word2idx']
    embedding_size = dic['embedding_size']
    model = CNN_CNN_LSTM(embedding_dim=50, embedding_size=embedding_size, decoder_feature_size=1000, num_classes=4, device='cpu')
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    return model, word2idx

def preprocess_dodf(text, word2idx_dict):
    """
    Preprocess a dodf pure text, splitting sentences 

    input: pure dodf extracted using DODFMiner (text file path)
    output: dodf split at sentence level and normalized (using unicodedata)
    """
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    # Split text into sentences using NLTK sentence tokenizer
    sent_tokenizer=nltk.data.load('tokenizers/punkt/portuguese.pickle')
    sentences = sent_tokenizer.tokenize(text)
    processed_sentences = sentences.copy()
    processed_sentences = [[word.replace(',', '').replace(';', '').replace(':', '').lower() for word in sent.split()] for sent in processed_sentences]
    # processed_sentences = [sent.replace(',', '').replace(';', '').replace(':', '').split() for sent in processed_sentences]

    # Pad sentences to max_sentence_len
    max_sentence_len = -1
    for sent in processed_sentences:
        max_sentence_len = max(max_sentence_len, len(sent))
    for i in range(len(sentences)):
        processed_sentences[i] = ['<pad>' if k>=len(processed_sentences[i]) else processed_sentences[i][k] for k in range(max_sentence_len)]
    
    for i in range(len(processed_sentences)):
        for j in range(len(processed_sentences[i])):
            word = processed_sentences[i][j]
            if word in word2idx_dict:
                processed_sentences[i][j] = word2idx_dict[processed_sentences[i][j]]
            else:
                processed_sentences[i][j] = word2idx_dict["<unk>"]
    processed_sentences = torch.LongTensor(processed_sentences).unsqueeze(dim=0)
    return processed_sentences, sentences

def get_acts(predictions, sentences):
    """
    Extracts acts predicted by the text segmentation ML model

    input: predictions for each sentence, and the sentences that were given as input to the model (tuple indicating beginning, ending and type of an act)
    output: acts (one or more sentence per act) 
    """
    entities = find_entities(predictions)
    acts = []
    tags = []
    for prediction in entities:
        begin = prediction[0]
        end = prediction[1]
        tag = prediction[2]
        acts.append(' '.join(sentences[begin:end+1]))
        tags.append(tag)
    return acts, tags

#### Rotina

class Segmentation:
    @staticmethod
    def extract_segments(text, act_name):
        if act_name in model_cover_list:
            if not os.path.isfile(os.path.dirname(__file__) + '/model/cnn_cnn_lstm.pt'):
                print('[Segmentation] The model is not present in local files Downloding...')
                url = 'https://drive.google.com/uc?id=1keERcWl3M-ZMypqHWOtK3_TIntUI6I5s'
                output = os.path.dirname(__file__) + '/model/cnn_cnn_lstm.pt'
                gdown.download(url, output, quiet=False)
                print('[Segmentation] Download finished.')

            model, word2idx = load_model(word2idx_path=os.path.dirname(__file__) + '/model/word2idx_dictionary.pkl', 
                                         model_path=os.path.dirname(__file__) + '/model/cnn_cnn_lstm.pt')
            
            print('[Segmentation] Segmentation is being applied...')
            processed_sentences, sentences = preprocess_dodf(text=text, word2idx_dict=word2idx)
            predictions, _ = model.eval().decode(processed_sentences)
            atos, tags = get_acts(predictions.squeeze(dim=0), sentences)
            print('[Segmentation] Finished.')
            if len(atos) > 0:
                return atos[1]
            else:
                print('[Segmentation] No act found by segmentation returning the entire text')
                return text
        else:
            print('[Segmentation] The current model is not trained with this act yet. Changing to pure text')
            return text