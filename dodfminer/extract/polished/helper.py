""" Polished extraction helper functions.

Functions in this files can be used inside, or outside, the ActsExtractor
class. Their purpose is to make some tasks easier for the user,
like creating txts, searching through files, and print dataframes.

Usage Example::

    from ddodfminer.extract.polished import helper
    helper.print_dataframe(df)

Functions
=========

"""

import os
import tqdm
import pandas as pd

from dodfminer.extract.polished.core import ActsExtractor
from dodfminer.extract.polished.core import _acts_ids
from dodfminer.extract.pure.core import ContentExtractor

def xml_multiple(path, backend):
    files = []
    if os.path.isfile(path):
<<<<<<< HEAD
        files = [path]
    else:
        files = get_files_path(path, 'pdf')

    print(files)
=======
        files = [].append(path)
    else:
        files = get_files_path(path, 'pdf')

>>>>>>> 8408f7280c1243329517e678ede62d376f08457e
    print("[XMLFy] Make yourself a coffee! This may take a while")
    bar = tqdm.tqdm(total=len(files), desc="[XMLFy] Progress")
    i = 1
    for file in files:
        xml = ActsExtractor.get_xml(file, backend, i)
        xml.save_to_disc(path)
        i += 1
        bar.update(1)

def extract_multiple_acts(path, types, backend):
    """Extract multple Acts from Multiple DODFs to act named CSVs.

    Args:
        path (str): Folder where the Dodfs are.
        types ([str]): Types of the act, see the core class to view
                    avaiables types.
        backend (str): what backend will be used to extract Acts {regex, ner}

    Returns:
        None
    """
    print(types)
    if len(types) == 0:
        types = _acts_ids.keys()

    if os.path.isfile(path):
        ContentExtractor.extract_text(path, single=True)
        for type in types:
            df = extract_single(path.replace('.pdf', '.txt'), type, backend=backend)
            df.to_csv(os.path.join(os.path.dirname(path), type+'.csv'))
    else:
        ContentExtractor.extract_to_txt(path)
        files = get_files_path(path, 'txt')
        for type in types:
            df = extract_multiple(files, type, backend)
            df.to_csv(os.path.join(path, type+".csv"))


def extract_multiple(files, type, backend, txt_out=False, txt_path="./results"):
    """Extract Act from Multiple DODF to a single DataFrame.

    Note:
        This function might save data to disc in text format,
        if txt_out is True.

    Args:
        files ([str]): List of dodfs files path.
        type (str): Type of the act, see the core class to view
                    avaiables types.
        backend (str): what backend will be used to extract Acts {regex, ner}
        txt_out (bool): Boolean indicating if acts should be saved on
                        text files.
        txt_path (str): Path to save the text files.

    Returns:
        A dataframe containing all instances of the desired
        act in the files set.

    """
    res = []
    for file in files:
        res_obj = ActsExtractor.get_act_obj(type, file, backend)
        res_df = res_obj.data_frame
        res_txt = res_obj.acts_str
        if not res_df.empty:
            res.append(res_df)
            if txt_out:
                build_act_txt(res_txt, type, txt_path)

    if len(res) == 0:
        res_final = pd.DataFrame()
    else:
        res_final = pd.concat([pd.DataFrame(df) for df in res],
                              ignore_index=True)
    return res_final


def extract_single(file, type, backend):
    """Extract Act from a single DODF to a single DataFrame.

    Note:
        This function might save data to disc in text format,
        if txt_out is True.

    Args:
        files (str): Dodf file path.
        type (str): Type of the act, see the core class to view
                    avaiables types.
        backend (str): what backend will be used to extract Acts {regex, ner}

    Returns:
        A dataframe containing all instances of the desired act
        including the texts found.

    """
    res_obj = ActsExtractor.get_act_obj(type, file, backend)
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
                .set_table_styles([dict(selector='th',
                                        props=[('text-align', 'left')])]))
    return style_df


def get_files_path(path, type):
    """Get all files path inside a folder.

    Works with nested folders.

    Args:
        path: Folder to look into for files

    Returns:A dataframe containing all instances of the desired
        act in the files set.
        A list of strings with the file path.

    """
    files_path = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith("."+type):
                files_path.append(os.path.join(root, file))
    return files_path
