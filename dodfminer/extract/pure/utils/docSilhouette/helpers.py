import pytesseract as pt
from operator import itemgetter
import pandas as pd

def image2df(page, lang='eng', sort=True, skipColumns=False, minConf=-1, minTop=1, filterBlank=False):
    ds = pt.image_to_data(page, lang, nice=0, output_type='data.frame')
    if sort:
        ds = ds.sort_values(by=['top', 'left'], ascending=True) 
    if skipColumns:
        ds.drop(columns=['level','page_num', 'block_num', 'par_num', 'line_num', 'word_num']) 
    if filterBlank:
        ds = ds[~ds.text.str.match(r'^\s*$', na=False)]
        
    ds = ds[(ds.conf > minConf) & (ds.top>=minTop)].reset_index(drop=True)

    df_grouped_by_block = ds.groupby('block_num')
    groups = {}
    for group_name, df_group in df_grouped_by_block:
        groups[group_name] = wordsInLine(df_group)
    # if VERBOSE:
    #     print(f'GROUPS MAPPED AND TEXT FLOW FOR PAGE {idx} CREATED')   
    data = {}
    index = 0
    for key, value in groups.items():
        for key2, value2 in value.items():
            value2['group'] = key
            data[index] = value2
            index+=1

    # if VERBOSE:
    #     print(f'DATA FOR ALL LINES WITH GROUPS AND WORDS FOR PAGE {idx} CREATED')

    return pd.DataFrame.from_dict(data, orient='index')

def wordsInLine(ds, verbose=False):
    n = len(ds)
    minHeight = ds.height.min()
    lines = {}
    lineIndex = -1
    wordIndex = 0
    
    while wordIndex < n:
        lineIndex += 1
        row = ds.iloc[wordIndex]
        word = str(row['text'])
        top, botton = row.top, row.top + .5*row.height
        row_botton = row.top + row.height
        lines[lineIndex] = {'top': top, 
                            'botton': row_botton, 
                            'left': row.left, 
                            'right': row.left + row.width, 
                            'height': row.height,
                            'width': row.width,
                            'wordsIds': [wordIndex],
                            'wordsAndPos': [(row.left, word)]
                           }
        
        if verbose:
            print(f'{lineIndex:2}|{word:>21}|{row_botton: >#06.1f}|{row.top:4}|{row.left:4}|{row.width:3}|{row.height:3}')

        wordIndex += 1
        if (wordIndex < n):
            row = ds.iloc[wordIndex]
            while wordIndex < n and row.top < botton:
                word = str(row['text'])
                row_top = lines[lineIndex]['top'] if lines[lineIndex]['top'] < row.top else row.top 
                row_botton = lines[lineIndex]['botton'] if lines[lineIndex]['botton'] > lines[lineIndex]['top'] + row.height else row.top + row.height
                row_left = lines[lineIndex]['left'] if lines[lineIndex]['left'] < row.left else row.left 
                row_right = lines[lineIndex]['right'] if lines[lineIndex]['right'] > row.left + row.width else row.left + row.width            
                row_height = lines[lineIndex]['height'] if (lines[lineIndex]['height'] > row.height or ';' in word) else row.height            
                
                row_width = lines[lineIndex]['width'] + row.width                            

                words = lines[lineIndex]['wordsIds']
                wordsAndPos = lines[lineIndex]['wordsAndPos']
                wordsAndPos.append((row.left, word))
                words.append(wordIndex)
                lines[lineIndex] = {'top': row_top, 
                                    'botton': row_botton, 
                                    'left': row_left,
                                    'right': row_right, 
                                    'height':row_height,
                                    'width':row_width,                                    
                                    'wordsIds': words,
                                    'wordsAndPos': wordsAndPos
                                   }

                if verbose:
                    print(f'{lineIndex:2}|{word:>21}|{row_botton: >#06.1f}|{row.top:4}|{row.left:4}|{row.width:3}|{row_height:3}')

                wordIndex += 1
                if (wordIndex < n):
                    row = ds.iloc[wordIndex]
                
        wordsAndPos = lines[lineIndex]['wordsAndPos']
        wordsAndPos.sort(key=itemgetter(0))
        lines[lineIndex]['text'] = ' '.join([''.join(w[1]) for w in wordsAndPos])

    return lines

def setColumnGroup(row, columns_by_groups):
    group = row['group']
    row['column'] = columns_by_groups[group]
    return row

def count_groups_by_column(df):
    columns_dict = df.groupby('column', as_index=True).agg({"left": "min", "right": "max"}).to_dict('index')
    columns_samples = df['column'].value_counts().to_dict()
    for key, value in columns_samples.items():
        columns_dict[key]['samples'] = value
    return columns_dict


def setCentered(row, columns_dict, page_width, ratio = 0.01):
    column_index = row['column']
    samples = columns_dict[column_index]['samples']
    text = row['text']
    text_with_pipe = '|' in text
    left = row['left']
    right = row['right']
    row['centered'] = False
    if samples <= 1:
        return row
    
    column_left = columns_dict[column_index]['left']
    column_right = columns_dict[column_index]['right']
    delta_left = left - column_left
    delta_right = column_right - right
    tolerance = ratio * page_width
    diff = abs(delta_left - delta_right)
    
    if diff < tolerance + text_with_pipe * 220 and (delta_left > tolerance or delta_right > tolerance ):
        row['centered'] = True
    return row  