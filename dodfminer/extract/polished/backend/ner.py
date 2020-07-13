class ActNER:

    def __init__(self):
        super(ActNER, self).__init__()
        self._model = self._load_model()

    def _load_model(self):
        if self._backend == 'ner':
            print("This Act does not have an model: FALLING BACK TO REGEX")
            self._backend = 'regex'

    def _get_features(self, act):
        sent_features = []
        for i in range(len(act)):
            word_feat = {
                'word': act[i].lower(),
                'capital_letter': act[i][0].isupper(),
                'all_capital': act[i].isupper(),
                'isdigit': act[i].isdigit(),
                'word_before': act[i].lower() if i == 0 else act[i-1].lower(),
                'word_after:': act[i].lower() if i+1 >= len(act) else act[i+1].lower(),
                'BOS': i == 0,
                'EOS': i == len(act)-1
            }
            sent_features.append(word_feat)
        return sent_features

    def _prediction(self, act):
        act = self._preprocess(act)
        if isinstance(act[0], list):
            feats = []
            for i in range(len(act)):
                feats.append(self._get_features(act[i]))
            predictions = self._model.predict(feats)
            return predictions
        else:
            feats = self._get_features(act)
            predictions = self._model.predict_single(feats)
            return self.dataFramefy(act, predictions)

    def _preprocess(self, sentence):
        sentence = sentence.replace(',', ' , ').replace(';', ' ; '). \
                   replace(':', ' : ').replace('. ', ' . ').replace('\n', ' ')
        if sentence[len(sentence)-2:] == '. ':
            sentence = sentence[:len(sentence)-2] + " ."
        return sentence.split()

    # TODO create dataframe with identified entities
    def dataFramefy(self, sentence, prediction):
        # Create dictionary of tags to save predicted entities
        tags = self._model.classes_
        tags.remove('O')
        tags.sort(reverse=True)
        while(tags[0][0] == 'I'):
            del tags[0]
        for i in range(len(tags)):
            tags[i] = tags[i][2:]
        dict = {}
        for i in tags:
            dict[i] = []

        last_tag = 'O'
        temp_entity = []
        for i in range(len(prediction)):
            if prediction[i] != last_tag and last_tag != 'O':
                dict[last_tag[2:]].append(temp_entity)
                temp_entity = []
            if prediction[i] == 'O':
                last_tag = 'O'
                continue
            else:
                temp_entity.append(sentence[i])
                last_tag = "I" + prediction[i][1:]

        if temp_entity:
            tags[last_tag[2:]].append(temp_entity)

        return dict
