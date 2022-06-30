"""Files to download for Reversões act model."""

from dodfminer.downloader.acts.base import Atos

class Revertions(Atos):
    '''
    Class for Reversões act.
    '''

    def __init__(self, path, model_type):
        super().__init__(path, model_type)

    def _act_name(self):
        return "Reversoes"
    
    def _get_files(self):
        if self._model_type == 'prop':
            return ['reversao.pkl']
        elif self._model_type == 'seg':
            return ['reversao.pkl']

    def _get_dataset_path(self):
        if self._model_type == 'prop':
            return 'http://164.41.76.30/models/atos_pessoal/models/v1/'
        elif self._model_type == 'seg':
            return 'http://164.41.76.30/models/atos_pessoal/seg_models/v1/'