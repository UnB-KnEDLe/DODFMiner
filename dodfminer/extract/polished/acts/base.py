"""Base class for an Act model.

This module contains the Atos class, which have all that is necessary to
extract information from a specialized act.
"""

import re
import json
import pandas as pd

from dodfminer.extract.polished.backend.regex import ActRegex
from dodfminer.extract.polished.backend.ner import ActNER
from dodfminer.extract.polished.backend.seg import ActSeg


class Atos(ActRegex, ActNER, ActSeg):  # pylint: disable=too-many-instance-attributes
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

    def __init__(self, file_name, backend='regex'):
        self._backend = backend
        self._name = self._act_name()
        super().__init__()

        if file_name[-5:] == '.json':
            self.read_json(file_name)
        else:
            self.read_txt(file_name)

        self._acts_str = []
        self._columns = self._props_names() + self._standard_props_names()

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

    @classmethod
    def _section(cls):
        """Section of the act.

        Must return a single string representing the act section

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

    #pylint: disable=no-self-use
    def _standard_props_names(self, capitalize=False):
        props = ['DODF_Fonte_Arquivo', 'DODF_Fonte_Data', 'DODF_Fonte_Numero']

        if capitalize:
            props = [name.capitalize() for name in props]

        return props

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
                data_frame.columns = [x.capitalize()
                                      for x in data_frame.columns]
            self._check_cols(data_frame.columns)
            return data_frame
        return pd.DataFrame()

    def _standard_props(self):
        act = {}

        file = self._file_name.split('/')[-1] if self._file_name else None
        match = re.search(r'(\d+\-\d+\-\d+)',file) if file else None
        file_split = file.split() if file else None

        act['DODF_Fonte_Arquivo'] = file.replace('.txt', '.pdf') if file else None
        act['DODF_Fonte_Data'] = match.group(1).replace('-', '/') if match else None
        act['DODF_Fonte_Numero'] = file_split[1] if file_split and len(file_split)>=2 else None

        return act

    def get_expected_colunms(self) -> list:
        '''
        Get the expected columns for the dataframe
        Raises:
            NotImplementedError: Child class needs to overwrite this method.
        '''
        raise NotImplementedError

    def _check_cols(self, columns: list) -> None:
        '''
            Check if dataframe columns are the expected ones
            Raises:
                NotImplementedError: Child class needs to overwrite this method.

        '''
        for col in self.get_expected_colunms():
            if col not in columns:
                raise KeyError(f'Key not present in dataframe -> {col}')

    def add_standard_props(self, act, capitalize=False):
        standard_props = self._standard_props()

        if capitalize:
            standard_props = {(key.capitalize()):val for key, val in standard_props.items()}

        act = {**act, **(standard_props)}
        return act

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
            # Merge act props with standard props
            acts.append(self.add_standard_props(act))

        return acts

    def read_json(self, file_name):
        """Reads a .json file of a DODF.

        A single string with all the relevant text from the act section is extracted.
        """
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                self._json = json.load(file)
                self._file_name = file_name

            section = self._json['json']['INFO'][self._section()]

            all_txt = []
            for agency in section:
                for document in section[agency]:
                    for subdoc in section[agency][document]:
                        txt = section[agency][document][subdoc]['texto']
                        txt = re.sub('<[^<]+?>', ' ', txt).replace('&nbsp', ' ')
                        all_txt.append(txt)
            self._text = ''.join(all_txt)

        except IOError:
            self._text = file_name
            self._file_name = None

    def read_txt(self, file_name):
        """Reads a .txt file of a DODF.

        A single string with all the text of the file is extracted.
        """

        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                self._text = file.read()
                self._file_name = file_name
        except IOError:
            self._text = file_name
            self._file_name = None
