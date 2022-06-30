"""Base class for an Act model.

This module contains the Atos class, which have all that is necessary to
download files from a specialized act.
"""

import os
import requests

class Atos:  # pylint: disable=too-many-instance-attributes
    """Base class to download model files from a specific act.

    Note:
        You should not use this class alone,
        use its childs on the regex module.

    Args:
        path (str): The model path.
        model_type (str): The type of the model to download.
                          Can be either prop (catch entities) or seg (segmentation).
                          Defaults to prop.

    Attributes:
        _name (str): Name of the type of the act whose model must be downloaded.
        _model_type (str): Type of the model to download.
        _model_path (str): Path where the files will be stored.
        _files (list): List of file names of the model.
        _dataset_path (str): The dataset URL where the file is hosted.

    """

    def __init__(self, path, model_type):
        self._name = self._act_name()
        self._model_type = model_type
        super().__init__()

        self._model_path = path
        self._files = self._get_files()
        self._dataset_path = self._get_dataset_path()

        self._download_data()

    @property
    def name(self):
        """str: Name of the act."""
        return self._name

    def _get_files(self):
        """Name of the act.

        Must return a list of all the files to download

        Raises:
            NotImplementedError: Child class needs to overwrite this method.

        """
        raise NotImplementedError

    def _get_dataset(self):
        """The dataset URL from which files will be downloaded.

        Must return a single string with the URL

        Raises:
            NotImplementedError: Child class needs to overwrite this method.

        """
        raise NotImplementedError

    def _act_name(self):
        """Name of the act.

        Must return a single string representing the act name

        Raises:
            NotImplementedError: Child class needs to overwrite this method.

        """
        raise NotImplementedError

    def _download_data(self):
        """Download and write the data of the model."""

        for file in self._files:
            url = self._dataset_path + file
            r = requests.get(url)
            open(os.path.join(self._model_path, file), 'wb').write(r.content)

    def _get_path(self):
        """Return the path where the files will be stored.
        
        Returns:
            The path where the files will be stored.

        """

        return self._model_path