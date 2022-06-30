import re
import pickle


def load_pkl(file_name):
    with open(file_name, 'rb') as file:
        loaded_file = pickle.load(file)
    file.close()
    return loaded_file

def clean_numbers(text):
    text = re.sub('[0-9]{5,}', '#####', text)
    text = re.sub('[0-9]{4}', '####', text)
    text = re.sub('[0-9]{3}', '###', text)
    text = re.sub('[0-9]{2}', '##', text)
    
    return text

def get_word2idx(sentence, word2idx_dic):
    sentence_temp = sentence.copy()
    
    for i in range(len(sentence_temp)):
        word = clean_numbers(sentence_temp[i])
        
        if word in word2idx_dic:
            sentence_temp[i] = word2idx_dic[word]
        elif word.lower() in word2idx_dic:
            sentence_temp[i] = word2idx_dic[word.lower()]
        else:
            sentence_temp[i] = word2idx_dic['<UNK>']
    
    return sentence_temp

def get_char2idx(words, char2idx_dic):
    words_temp = words.copy()
    words_temp = [[char2idx_dic['<UNK>'] if char not in char2idx_dic else char2idx_dic[char] for char in word] for word in words_temp]
    
    return words_temp

def IOBES_tags(predictions, tag2idx):
    """
    Transform tags from indices to class name strings
    """
    idx2tag = {}
    for tag in tag2idx:
        idx2tag[tag2idx[tag]] = tag
    
    IOBES_tags = predictions.copy()
    for i in range(len(IOBES_tags)):
        for j in range(len(IOBES_tags[i])):
            IOBES_tags[i][j] = idx2tag[IOBES_tags[i][j]]
    return IOBES_tags