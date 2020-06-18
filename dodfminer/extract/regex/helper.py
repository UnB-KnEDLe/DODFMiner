import os
import pandas as pd
from core import Regex
from os.path import isfile, join

def extract_multiple(files, type, txt_out=False, txt_path="./results"):
    res = []
    for file in files:
        res_obj = Regex.get_act_obj(type, file)
        res_df = res_obj.data_frame
        res_txt = res_obj.acts_str
        if not res_df.empty:
            res.append(res_df)
            if txt_out:
                _build_act_txt(res_txt, type, txt_path)

    res_final = pd.concat([pd.DataFrame(df) for df in res],
                            ignore_index=True)
    return res_final

def _build_act_txt(acts, name, save_path="./results/"):
    if len(acts) > 0:
        file = open(f"{save_path}{name}.txt", "a") 
        for act in acts:
            file.write(act)
            file.write("\n\n\n")
        file.close

def print_dataframe(df):
    style_df = (df.style.set_properties(**{'text-align': 'left'})
                                        .set_table_styles([ dict(selector='th',
                                                                 props=[('text-align','left')])])
                )
    return style_df

def get_files_path(path):
    files_path = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".txt"):
                files_path.append(os.path.join(root, file))
    return files_path