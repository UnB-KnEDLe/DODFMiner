"""Files to download for Aditamento act model."""

from dodfminer.downloader.acts.base import Atos

class Aditamentos(Atos):
    '''
    Class for Aditamento act.
    '''

    def __init__(self, path, model_type):
        super().__init__(path, model_type)

    def _act_name(self):
        return "Aditamento"
    
    def _get_files(self):
        if self._model_type == 'prop':
            return ['aditamento-cnn_bilstm_crf.pkl', 'aditamento-tag2idx.pkl', 'aditamento-word2idx.pkl', 'aditamento-char2idx.pkl']
        elif self._model_type == 'seg':
            raise NotImplementedError

    def _get_dataset_path(self):
        if self._model_type == 'prop':
            return 'http://164.41.76.30/models/contratos/v1/aditamento/'
        elif self._model_type == 'seg':
            raise NotImplementedError