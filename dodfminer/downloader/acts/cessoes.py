"""Files to download for Cessões act model."""

from dodfminer.downloader.acts.base import Atos

class Cessoes(Atos):
    '''
    Class for Cessões act.
    '''

    def __init__(self, path, model_type):
        super().__init__(path, model_type)

    def _act_name(self):
        return "Cessoes"
    
    def _get_files(self):
        if self._model_type == 'prop':
            return ['cessao.pkl']
        elif self._model_type == 'seg':
            return ['cessao.pkl']

    def _get_dataset_path(self):
        if self._model_type == 'prop':
            return 'http://164.41.76.30/models/atos_pessoal/models/v1/'
        elif self._model_type == 'seg':
            return 'http://164.41.76.30/models/atos_pessoal/seg_models/v1/'