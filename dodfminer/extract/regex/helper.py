import os
from os.path import isfile, join

# def print_database_dfs(files_path, ato):
#     res_dfs = []
#     for txt in files_path:
#         txt_str = open(txt, "r").read()
#         ret = Retirements(txt_str)
#         if not ret.data_frame.empty:
#             res_dfs.append(ret.data_frame)

#     rets_final = pd.concat([pd.DataFrame(df) for df in res_dfs],
#                             ignore_index=True)
#     print_dataframe(rets_final)


def _build_act_txt(acts, name, save_path="./results/"):
    if len(acts) > 0:
        file = open(f"{save_path}{name}.txt", "w") 
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

def get_txts(path):
    txt_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))
    return txt_files