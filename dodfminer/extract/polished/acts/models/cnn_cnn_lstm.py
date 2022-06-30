import torch
import math
from math import sqrt
from random import sample
from torch import nn

class char_cnn(nn.Module):
    """
    Character-level word embedding neural network as implemented in Ma and Hovy (https://arxiv.org/abs/1603.01354)
    """
    def __init__(self, embedding_size, embedding_dim, out_channels):
        super(char_cnn, self).__init__()
        self.embedding = nn.Embedding(num_embeddings=embedding_size, embedding_dim=embedding_dim, padding_idx=0)
        self.conv = nn.Conv1d(in_channels=embedding_dim, out_channels=out_channels, kernel_size=3, stride=1, padding=1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.5)
        # self.dropout = CustomDropout(p=0.5)
        self.init_weight()

    def init_weight(self):
        """
        Initialize weights for the character embeddings as done in Ma and Hovy (https://arxiv.org/abs/1603.01354)
        """
        bias = sqrt(3.0/self.embedding.embedding_dim)
        nn.init.uniform_(self.embedding.weight, -bias, bias)

    def forward(self, x):
        x = self.dropout(self.embedding(x))
        shape = x.shape
        x = self.conv(x.reshape([shape[0]*shape[1], shape[2], shape[3]]).permute(0, 2, 1))
        x = torch.nn.functional.max_pool1d(x, kernel_size=x.shape[2]).squeeze(2)
        x = self.relu(x)
        return x.reshape([shape[0], shape[1], -1])

class word_cnn(nn.Module):
    """
    Word-level CNN for word level encoding of a token with its surrounding context as designed by Shen et al (https://arxiv.org/abs/1707.05928)
    """
    def __init__(self, pretrained_word_emb, word2idx, full_embedding_size, conv_layers, out_channels):
        super(word_cnn, self).__init__()
        self.word2idx = word2idx
        self.embedding = nn.Embedding.from_pretrained(torch.FloatTensor(pretrained_word_emb.vectors), freeze=True)
        self.dropout = nn.Dropout(p=0.5)
        # self.dropout = CustomDropout(p=0.5)
        convnet = []
        for i in range(conv_layers):
            if i == 0:
                convnet.append(nn.Conv1d(in_channels=full_embedding_size, out_channels=out_channels, kernel_size = 5, padding = 2))
                convnet.append(nn.ReLU())
                convnet.append(nn.Dropout(p=0.5))
            else:
                convnet.append(nn.Conv1d(in_channels=out_channels, out_channels=out_channels, kernel_size = 5, padding = 2))
                convnet.append(nn.ReLU())
                convnet.append(nn.Dropout(p=0.5))
        self.convnet = nn.Sequential(*convnet)
        self.init_weight()

    def init_weight(self):
        """
        Initialization of weights for the word-level CNN, created for tests only as it was not specified in previous works
        """
        pass

    def forward(self, x, char_embeddings, mask=None):
        # 50% chance word dropout to improve generalization (avoid replacing special tokens - <BOS> <EOS> <PAD>)
        # if self.training and mask != None:
        #     mask_ = mask.clone()
        #     for i in range(mask_.shape[0]):
        #         for j in range(mask.shape[1]-1):
        #             if mask_[i, j] == 0 and mask[i, j+1] == 1:
        #                 mask[i, j] = 1
        #     WD_mask = torch.distributions.Bernoulli(probs=(1-0.5)).sample(x.size()).to(x.device)
        #     WD_mask[:, 0] = 1
        #     mask_ *= WD_mask
        #     x[~mask_.bool()] = self.word2idx['<UNK>']
        # word2vec embedding
        x = self.embedding(x)
        # concat word and char embedding
        x = torch.cat((x, char_embeddings), dim=2)
        x = self.dropout(x)
        w = x.clone()
        x = x.permute(0, 2, 1)
        x = self.convnet(x)
        x = x.permute(0, 2, 1)
        # Return Concat w_full (word representation - combination of word and char embeddings) and h_enc (output of conv layers)
        return torch.cat((x, w), dim=2)

class decoder(nn.Module):
    """
    LSTM decoder (greedy decoding) as proposed by Shen et al (https://arxiv.org/abs/1707.05928)
    """
    def __init__(self, feature_size, num_classes, hidden_size, decoder_layers, device):
        super(decoder, self).__init__()
        self.device = device
        self.num_classes = num_classes
        self.lstm = torch.nn.LSTM(input_size=feature_size+num_classes, hidden_size=hidden_size, num_layers=decoder_layers)
        self.linear = torch.nn.Linear(hidden_size, num_classes)
        self.dropout = nn.Dropout(p=0.5)
        # self.dropout = CustomDropout(p=0.5)
        self.loss_fn = torch.nn.CrossEntropyLoss(ignore_index = 0, reduction='sum')
        self.init_weight()

    def init_weight(self):
        """
        Initialization of weights for the greedy LSTM decoder, initialization procedure done as implemented in Ma and Hovy (https://arxiv.org/abs/1603.01354)
        """
        # Initialize linear layer
        bias = sqrt(6.0/(self.linear.weight.shape[0]+self.linear.weight.shape[1]))
        nn.init.uniform_(self.linear.weight, -bias, bias)
        nn.init.constant_(self.linear.bias, 0.0)
        # Initialize LSTM layer
        for name, params in self.lstm.named_parameters():
            if 'bias' in name:
                nn.init.constant_(params, 0.0)
                nn.init.constant_(params[self.lstm.hidden_size:2*self.lstm.hidden_size], 1.0)
            else:
                bias = sqrt(6.0/(params.shape[0]+params.shape[1]))
                nn.init.uniform_(params, -bias, bias)

    def forward_step(self, x, prev_tag, prev_lstm_state):
        prev_tag_onehot = torch.nn.functional.one_hot(prev_tag, num_classes=self.num_classes).to(self.device)
        lstm_input = torch.cat((x, prev_tag_onehot), dim=1).unsqueeze(dim=0)
        lstm_output, lstm_state = self.lstm(lstm_input, prev_lstm_state)
        lstm_output = self.dropout(lstm_output)
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
    """
    CNN-CNN-LSTM model with greedy decoding, as proposeb by Shen et al (https://arxiv.org/abs/1707.05928)
    """
    def __init__(self, char_vocab_size, word2idx, pretrained_word_emb, num_classes, device, char_embedding_dim=30, char_out_channels=50, word_out_channels=800, word_conv_layers=2, decoder_layers=1, decoder_hidden_size=256):
        super(CNN_CNN_LSTM, self).__init__()
        self.num_classes = num_classes
        self.char_encoder = char_cnn(embedding_size=char_vocab_size, embedding_dim=char_embedding_dim, out_channels=char_out_channels)
        self.word_encoder = word_cnn(pretrained_word_emb=pretrained_word_emb, word2idx=word2idx, conv_layers = word_conv_layers, full_embedding_size=pretrained_word_emb.vector_size+char_out_channels, out_channels=word_out_channels)
        self.decoder      = decoder(num_classes=num_classes, feature_size=pretrained_word_emb.vector_size+char_out_channels+word_out_channels, hidden_size=decoder_hidden_size, decoder_layers=decoder_layers, device=device)

    def forward(self, sentence, word, tag, mask):
        x = self.char_encoder(word)
        x = self.word_encoder(sentence, x, mask)
        x = self.decoder(x, tag)
        return x
    
    def encode(self, sentence, word, mask):
        x = self.char_encoder(word)
        x = self.word_encoder(sentence, mask)
        return x

    def decode(self, sentence, word, mask, return_token_log_probabilities=False):
        x = self.char_encoder(word)
        x = self.word_encoder(sentence, x, mask)
        predictions, output = self.decoder.decode(x)
        if return_token_log_probabilities == True:
            return predictions, torch.nn.functional.log_softmax(output, dim=2)
        else:
            probability = torch.nn.functional.softmax(output, dim=2).max(dim=2).values
            probability[mask==False] = 1.0
            probability = probability.prod(dim = 1)
            return predictions, probability