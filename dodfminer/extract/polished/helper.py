""" Polished extraction helper functions.

Functions in this files can be used inside, or outside, the ActsExtractor
class. Their purpose is to make some tasks easier for the user,
like creating txts, searching through files, and print dataframes.

Usage Example::

    from dodfminer.extract.polished import helper
    helper.print_dataframe(df)

Functions
=========

"""

from typing import List, Tuple
import multiprocessing
import os
import re
import tqdm
import pandas as pd

from dodfminer.extract.polished.core import ActsExtractor
from dodfminer.extract.polished.core import _acts_ids
from dodfminer.extract.pure.core import ContentExtractor

from dodfminer.extract.polished.acts.type_classification.committee import Committee

def xml_multiple(path, backend):
    files = []
    if os.path.isfile(path):
        files = [path]
        path_ = './'
    else:
        if ".pdf" in path :
            rgx = r".*/"
            path_ = re.findall(rgx, path)[0]
            arq = re.sub(rgx,"", path)
            files = [arq]
        else:
            path_ = path
            files = get_files_path(path_, 'pdf')


    print(files)
    print("[XMLFy] Make yourself a coffee! This may take a while")
    progress_bar = tqdm.tqdm(total=len(files), desc="[XMLFy] Progress")
    i = 1
    for file in files:
        xml = ActsExtractor.get_xml(file, backend, i)
        xml.save_to_disc(path_)
        i += 1
        progress_bar.update(1)

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
        for act_type in types:
            data_frame, _= extract_single(path.replace('.pdf', '.txt'), act_type, backend=backend)
            data_frame.to_csv(os.path.join(os.path.dirname(path), act_type+'.csv'))
    else:
        ContentExtractor.extract_to_txt(path)
        files = get_files_path(path, 'txt')
        for act_type in types:
            data_frame = extract_multiple(files, act_type, backend)
            data_frame.to_csv(os.path.join(path, act_type + ".csv"))


def extract_multiple_acts_parallel(path: str, types: List[str], backend: str, processes = 4):
    """Extract multple Acts from Multiple DODFs to act named CSVs in parallel.

    Args:
        path (str): Folder where the Dodfs are.
        types ([str]): Types of the act, see the core class to view
                    avaiables types.
        backend (str): what backend will be used to extract Acts {regex, ner}

    Returns:
        None
    """
    if len(types) == 0:
        types = _acts_ids.keys()

    if os.path.isfile(path):
        ContentExtractor.extract_text(path, single=True)
        extraction_arguments = []
        for act_type in types:
            extraction_arguments.append((path.replace('.pdf', '.txt'), act_type, backend))

        with multiprocessing.Pool(processes=processes) as pool:
            result = pool.starmap(run_extract_simple_wrap, extraction_arguments)

        for act_type, (data_frame, _) in result:
            data_frame.to_csv(os.path.join(os.path.dirname(path), act_type+'.csv'))
    else:
        ContentExtractor.extract_to_txt(path)
        files = get_files_path(path, 'txt')
        extraction_arguments = []

        for act_type in types:
            extraction_arguments.append((files, act_type, backend))

        with multiprocessing.Pool(processes=processes) as pool:
            result = pool.starmap(run_thread_wrap_multiple, extraction_arguments)

            for item in result:
                item[1].to_csv(os.path.join(path, item[0] + ".csv"))


def run_extract_simple_wrap(file: str, act_type: str, backend: str) -> Tuple[str, pd.DataFrame]:
    '''
    Run one extractions
    '''
    result = extract_single(file, act_type, backend)
    return (act_type, result)


def run_thread_wrap_multiple(files: list, act_type: str, backend: str) -> Tuple[str, pd.DataFrame]:
    '''
    Run multiple extractions
    '''
    dataframe = extract_multiple(files, act_type, backend)
    return (act_type, dataframe)


def extract_multiple(files, act_type, backend, txt_out=False, txt_path="./results"):
    """Extract Act from Multiple DODF to a single DataFrame.

    Note:
        This function might save data to disc in text format,
        if txt_out is True.

    Args:
        files ([str]): List of dodfs files path.
        act_type (str): Type of the act, see the core class to view
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
        res_obj = ActsExtractor.get_act_obj(act_type, file, backend)
        # print(res_obj._backend)
        res_df = res_obj.data_frame
        res_txt = res_obj.acts_str
        res_df['text'] = res_txt
        if not res_df.empty:
            res.append(res_df)
            if txt_out:
                build_act_txt(res_txt, act_type, txt_path)

    if len(res) == 0:
        res_final = pd.DataFrame()
    else:
        res_final = pd.concat([pd.DataFrame(df) for df in res],
                              ignore_index=True)
    return res_final

def extract_multiple_acts_with_committee(path, types, backend):
    """Extract multple Acts from Multiple DODFs to act named CSVs.
    Uses committee_classification to find act types.

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

    all_acts = []

    if os.path.isfile(path):
        ContentExtractor.extract_text(path, single=True)
        for act_type in types:
            dataframe, _= extract_single(path.replace('.pdf', '.txt'), act_type, backend=backend)
            dataframe['type'] = act_type
            all_acts.append(dataframe.filter(['text', 'type'], axis = 1))
    else:
        ContentExtractor.extract_to_txt(path)
        files = get_files_path(path, 'txt')
        process_ref = []
        output = multiprocessing.Queue(len(types))
        for act_type in types:
            process = multiprocessing.Process(target = run_thread_wrap, args = (files, act_type, backend, output))
            process_ref.append(process)

        for thread in process_ref:
            thread.start()

        all_acts = [output.get() for _ in process_ref]

        for thread in process_ref:
            thread.join()

    dataframe = pd.concat(all_acts, ignore_index = True)

    if len(dataframe) == 0:
        dataframe = pd.DataFrame(columns = ['text', 'type'])

    committee_classification(dataframe, path, types, backend)

def run_thread_wrap(files: list, act_type: str, backend: str, all_acts: multiprocessing.Queue) -> None:
    '''
    Run multiple extractions
    '''
    dataframe = extract_multiple(files, act_type, backend)
    dataframe['type'] = act_type
    all_acts.put(dataframe.filter(['text', 'type'], axis = 1))

def committee_classification(all_acts, path, types, backend):
    """Uses committee classification to find act types.

    Args:
        all_acts (DataFrame): Dataframe with acts text and regex type.
        path (str): Folder where the Dodfs are.
        types ([str]): Types of the act, see the core class to view
                    avaiables types.
        backend (str): what backend will be used to extract Acts {regex, ner}
    Returns:
        None
    """

    classification_folder = os.path.dirname(__file__) + '/acts/type_classification/'
    models_path = classification_folder + 'models/models.pkl'

    committee = Committee(models_path)

    new_types = committee.transform(all_acts['text'], all_acts['type'])

    all_acts['type']  = new_types

    for act_type in types:
        df_act = all_acts.loc[all_acts.type == act_type]['text']
        all_strings = ""
        for act in df_act:
            all_strings += act + ".\n"

        data_frame, _ = extract_single(all_strings, act_type, backend=backend)

        if os.path.isfile(path):
            data_frame.to_csv(os.path.join(os.path.dirname(path), act_type+'.csv'))
        else:
            data_frame.to_csv(os.path.join(path, act_type+".csv"))

def extract_single(file, act_type, backend):
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
        A tuple containing, respectively: a dataframe containing all instances of the desired act
        including the texts found, and a list of the segmented text blocks, and .

    """
    res_obj = ActsExtractor.get_act_obj(act_type, file, backend)
    res_df = res_obj.data_frame
    res_txt = res_obj.acts_str
    res_df['text'] = res_txt

    return res_df, res_txt


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
        with open(f"{save_path}{name}.txt", "a", encoding='utf-8') as file:
            for act in acts:
                file.write(act)
                file.write("\n\n\n")


def print_dataframe(data_frame):
    """Style a Dataframe.

    Args:
        The dataframe to be styled.

    Returns:
        The styled dataframe

    """
    style_df = (data_frame.style.set_properties(**{'text-align': 'left'})
                .set_table_styles([dict(selector='th',
                                        props=[('text-align', 'left')])]))
    return style_df


def get_files_path(path, file_type):
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
        # sort file names to avoid unpredictable results
        files.sort()
        for file in files:
            if file.endswith("."+file_type):
                files_path.append(os.path.join(root, file))
    return files_path
