"""Files to download for Contrato act model."""

from dodfminer.downloader.acts.base import Atos

class Contratos(Atos):
    '''
    Class for Contrato act.
    '''

    def __init__(self, path, model_type):
        super().__init__(path, model_type)

    def _act_name(self):
        return "Contrato"
    
    def _get_files(self):
        if self._model_type == 'prop':
            return ['gold_extratos_contrato-cnn_cnn_lstm.pkl', 'tag2idx.pkl', 'word2idx.pkl', 'char2idx.pkl']
        elif self._model_type == 'seg':
            return ['contrato.pkl']

    def _get_dataset_path(self):
        if self._model_type == 'prop':
            return 'http://164.41.76.30/models/contratos/v1/extrato/'
        elif self._model_type == 'seg':
            return 'http://164.41.76.30/models/atos_pessoal/seg_models/v1/'