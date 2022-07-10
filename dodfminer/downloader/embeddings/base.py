"""Base class for a Pre-Trained Embedding.

This module contains the Embeddings class, which have all that is necessary to
download files of an available pre-trained embedding.
"""

import os
import requests

_embeddings_ids = {
    "Word2Vec CBOW 100 dim": "emb_cbow_s100.pkl"
}

class Embeddings:  # pylint: disable=too-many-instance-attributes
    """Base class for extracting an act and its proprieties to a dataframe.

    Note:
        You should not use this class alone,
        use its childs on the regex module.

    Args:
        file (str): The dodf file path.
        backend (str): The mechanism to use in extraction.
                       Can be either regex or ner.
                       Defaults to regex.

    Attributes:
        _file_name (str): The dodf file path.
        _text (str): The dodf content in string format.
        _acts_str (str): List of raw text acts.
        _name (str): Name of the act.
        _columns (str): List of the proprieties names from the act.
        _raw_acts (list): List of raw text acts .
        _acts (list): List of acts with propreties extracted.
        _data_frame (dataframe): The resulting dataframe from the
                                 extraction process.

    """

    def __init__(self, path, embedding_id):
        super().__init__()
        self._embedding_path = path
        self._base_url = "http://164.41.76.30/models/contratos/v1/extrato/"
        self._download_embedding(embedding_id)

    def get_ids():
        """IDs of the available embeddings.

        Returns:
            List of all available embeddings IDs.

        """

        return list(_embeddings_ids.keys())
    
    def get_filename(embedding_id):
        """Get the embedding file name
        
        Returns:
            Pre-trained embedding file name.

        """

        return _embeddings_ids[embedding_id]

    def _download_embedding(self, embedding_id):
        """Download selected embedding"""

        embedding_path = _embeddings_ids[embedding_id]
        url = self._base_url + embedding_path
        r = requests.get(url)
        open(os.path.join(self._embedding_path, embedding_path), 'wb').write(r.content)

    def _download_data(self):
        """Download and save the embedding files"""

        for file in self._files:
            url = self._dataset_path + file
            r = requests.get(url)
            open(os.path.join(self._model_path, file), 'wb').write(r.content)

    def _get_path(self):
        return self._model_path