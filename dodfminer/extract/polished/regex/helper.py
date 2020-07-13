""" Regex helper functions.

Functions in this files can be used inside, or outside, the Regex class.
Their purpose is to make some tasks easier for the user, like creating txts,
searching through files, and print dataframes.

Usage Example::

    from dodfminer.extract.regex import helper
    helper.print_dataframe(df)

Functions
=========

"""

import os
import pandas as pd
from os.path import isfile, join

from dodfminer.extract.polished.regex.core import ActRegex


def extract_multiple(files, type, txt_out=False, txt_path="./results"):
    """Extract Act from Multiple DODF to a single DataFrame.

    Note:
        This function might save data to disc in text format, if txt_out is True.

    Args:
        files ([str]): List of dodfs files path.
        type (str): Type of the act, see the core class to view avaiables types.
        txt_out (bool): Boolean indicating if acts should be saved on text files.
        txt_path (str): Path to save the text files.
    
    Returns:
        A dataframe containing all instances of the desired act in the files set.

    """
    res = []
    for file in files:
        res_obj = Regex.get_act_obj(type, file)
        res_df = res_obj.data_frame
        res_txt = res_obj.acts_str
        if not res_df.empty:
            res.append(res_df)
            if txt_out:
                build_act_txt(res_txt, type, txt_path)

    res_final = pd.concat([pd.DataFrame(df) for df in res],
                            ignore_index=True)
    return res_final

def extract_single(file, type):
    """Extract Act from a single DODF to a single DataFrame.

    Note:
        This function might save data to disc in text format, if txt_out is True.

    Args:
        files ([str]): List of dodfs files path.
        type (str): Type of the act, see the core class to view avaiables types.
    
    Returns:
        A dataframe containing all instances of the desired act including the texts found.

    """
    res_obj = Regex.get_act_obj(type, file)
    res_df = res_obj.data_frame
    res_txt = res_obj.acts_str
    res_df['text'] = res_txt
    
    return res_df

def build_act_txt(acts, name, save_path="./results/"):
    """Create a text file in disc for a act type.

    Note:
        This function might save data to disc in text format.

    Args:
        acts ([str]): List of all acts to save in the text file.
        name (str): Name of the output file.
        save_path (str): Path to save the text file.

    """
    if len(acts) > 0:
        file = open(f"{save_path}{name}.txt", "a") 
        for act in acts:
            file.write(act)
            file.write("\n\n\n")
        file.close

def print_dataframe(df):
    """Style a Dataframe.

    Args:
        The dataframe to be styled.

    Returns:
        The styled dataframe

    """
    style_df = (df.style.set_properties(**{'text-align': 'left'})
                                        .set_table_styles([ dict(selector='th',
                                                                 props=[('text-align','left')])])
                )
    return style_df

def get_files_path(path):
    """Get all files path inside a folder.

    Works with nested folders.

    Args:
        path: Folder to look into for files

    Returns:
        A list of strings with the file path.

    """
    files_path = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".txt"):
                files_path.append(os.path.join(root, file))
    return files_path