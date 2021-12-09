"""Base class for an Act model.

This module contains the Atos class, which have all that is necessary to
extract information from a specialized act.
"""

import pandas as pd

from dodfminer.extract.polished.backend.regex import ActRegex
from dodfminer.extract.polished.backend.ner import ActNER
from dodfminer.extract.polished.backend.seg import ActSeg


class Atos(ActRegex, ActNER, ActSeg):
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

    def __init__(self, file, backend='regex'):
        self._backend = backend
        self._name = self._act_name()
        super().__init__()

        try:
            with open(file, "r", encoding='utf-8') as fp:
                self._text = fp.read()
                fp.close()
                self._file_name = file
        except IOError:
            self._text = file
            self._file_name = None

        self._acts_str = []
        self._columns = self._props_names()

        self._raw_acts = self._seg_function()
        self._acts = self._extract_props()
        self._data_frame = self._build_dataframe()

    @property
    def name(self):
        """str: Name of the act."""
        return self._name

    @property
    def data_frame(self):
        """:obj:`dataframe`: Act dataframe with proprieties extracted."""
        return self._data_frame

    @property
    def acts_str(self):
        """str: Vector of acts content as raw text."""
        return self._acts_str

    def _act_name(self):
        """Name of the act.

        Must return a single string representing the act name

        Raises:
            NotImplementedError: Child class needs to overwrite this method.

        """
        raise NotImplementedError

    def _props_names(self):
        """Name of all the proprieties for the dataframe column.

        Must return a vector of string representing the proprieties names

        Warning:
            The first name will be used for the type-of-act propriety.

        Raises:
            NotImplementedError: Child class needs to overwrite this method.

        """
        raise NotImplementedError

    def _build_dataframe(self):
        """Create a dataframe with the extracted proprieties.

        Returns:
            The dataframe created
        """
        if len(self._acts) > 0:
            data_frame = pd.DataFrame(self._acts)
            if self._backend == 'regex':
                data_frame.columns = self._columns
            else:
                data_frame.columns = [x.capitalize() for x in data_frame.columns]
            return data_frame
        return pd.DataFrame()

    def _extract_props(self):
        """Extract proprieties of all the acts.

        Returns:
            A vector of extracted acts dictionaries.
        """
        acts = []
        for value in self._raw_acts:
            act = {}
            if self._backend == 'regex':
                act = self._regex_props(value)
            elif self._backend == 'ner':
                act = self._prediction(value)
            else:
                raise NotImplementedError("Non-existent backend option")
            acts.append(act)
        return acts