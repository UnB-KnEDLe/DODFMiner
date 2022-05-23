import pdf2image
from dodfminer.extract.pure.utils.docSilhouette.helpers import *
import pandas as pd
import logging
logging.basicConfig(filename = 'logging.log', format = '%(message)s', filemode = 'a', level = logging.DEBUG)
import tqdm

class docSilhouette:
    '''
    A class responsible for transforming pdf into text enriched with 
    special characters denoting aesthetics features, like page and document
    position for each text block.
    
    The transformation begins with OCRing document pagens with tesseract, 
    engine, whose dataframe output is the base for obtaining the 
    visual information surrouding the texto block itself.
    
    parameters
    ----------
        file_path: the pdf file full path
        lang: pytessere language, default eng
        page_width: page width in pixels, default 1654
        page_height: page height in pixels, default 2340
        DPI: DPI of the pdf, default 200        
    '''
    
    BEGIN_OF_BLOCK = 'xxbob'
    END_OF_BLOCK ='xxeob' 

    BEGIN_OF_CENTERED_TEXT = 'xxbcet'
    END_OF_CENTERED_TEXT = 'xxecet'
    
    def __init__(self, file_path, lang='eng', page_width=1654, page_height=2340, DPI = 200 ):
        self.file_path = file_path
        self.df_pages = None
        self.lang = lang
        self.ready = False
        self.DPI = DPI
        self.page_width = page_width
        self.page_height = page_height
        
    def __str__(self):
        return f'{self.__class__.__name__} object'
            
    def setup(self):
        '''
        Takes pdf and transform its pages into a single dataframe from tesseract
        '''
        try:
            pages = pdf2image.convert_from_path(pdf_path=self.file_path, dpi=self.DPI, size=(self.page_width,self.page_height))
            prog_bar_pages = tqdm.tqdm(total=len(pages))
            for ix, page in enumerate(pages):
                df = image2df(page)
                df['page'] = ix + 1
                if ix == 0:
                    self.df_pages = df.copy()
                else:
                    self.df_pages = pd.concat([self.df_pages, df.copy()], ignore_index=True)
                del df
                prog_bar_pages.update(1)
            del pages
            if len(self.df_pages) > 0:
                self.ready = True
        except Exception as error:
            print(f'Error: {error}')
            logging.error(f'Error to convert pdf pages to image! {error}')  
    def __len__(self):
        if self.ready:
            return self.df_pages['page'].max()
        logging.error('You must run setup method before using docSilhouete!')
        
    def get_text(self, echo_page = True, echo_quad = True, n_lines = 6, n_cols = 4, echo_centralized = True, page=None):
        '''
        
        parameters
        ----------
            echo_page: echoes the number of page in the text. Default: True
            echo_quads: echoes the block position start quadrant and the end quadrant. Default: True
            n_lines: amount of rows to be considered when defining page quadrants
            n_cols: amount of columns to be considered when defining page quadrants
            echo_centralized: echoes when the block is centralized, having the reference the column of text. Default: True
            page: page number to be processed. Default: None            
        '''
        
        text = ''
        if page:
            text += self.get_text_from_page(page, echo_quad, n_lines, n_cols, echo_centralized)  
        else:
            for page in range(self.__len__()):
                text += self.get_text_from_page(page+1, echo_page, echo_quad, n_lines, n_cols, echo_centralized)         
        return text
            
    def get_text_from_page(self, page, echo_page, echo_quad, n_lines, n_cols, echo_centralized):
        dfs = self.df_pages[self.df_pages['page']==page]
        
        h_dist = int(((1000 * self.page_height)/n_lines)/1000)
        v_dist = int(((1000 * self.page_width)/n_cols)/1000)
        
        logging.debug(f'LINE BOUNDING BOXES EXTRACTED FOR PAGE')
        _text = ''       
        #pages_drawn = []
        
        blocks_df = self.extract_group_bounding_boxes(dfs)

        logging.debug(f'GROUP BOUNDING BOXES EXTRACTED FOR PAGE')                    

        # if DRAW:
        #     pages_drawn.append(draw_blocks_into_page(blocks_df, page, (H_QUAD, V_QUAD), (self.page_width, HEIGHT)))
        #     logging.debug(f'GROUP BOUNDING BOXES DRAWN FOR PAGE')                       

        columns_by_groups = self.TriageGroupsByColumns(blocks_df)
        logging.debug(f'GROUP TRIAGED BY COLUMNS FOR PAGE')                       

        dfs = dfs.apply(setColumnGroup, columns_by_groups=columns_by_groups, axis=1)

        logging.debug(f'GROUP COLUMN SET FOR PAGE')                       

        columns_dict = count_groups_by_column(dfs)

        groups_dict = dfs.groupby('group', as_index=True).agg({"left": "min", "right": "max", "top":"min", "botton":"max"}).to_dict('index')

        dfs = dfs.apply(setCentered, page_width= self.page_width, columns_dict=columns_dict, axis=1)
        logging.debug(f'CENTER ALINGMENT SET FOR PAGE')

        last_group = None
        for row in dfs.sort_values(by=['group', 'top']).itertuples():
            group = row.group
            if last_group != group:
                if last_group != None:
                    if echo_quad:
                        right = groups_dict[last_group]['right']
                        botton = groups_dict[last_group]['botton']
                        q_H_end = (int(botton))//h_dist
                        q_V_end = (int(right))//v_dist    
                        _text += f'{self.END_OF_BLOCK} '
                        _text += f'xxQ{q_H_end:02}_{q_V_end:02}\n'

                        left = groups_dict[group]['left']
                        top = groups_dict[group]['top']
                        q_H_begin = (int(top))//h_dist
                        q_V_begin = (int(left))//v_dist        
                        _text += f'\nxxP{page:03}' if echo_page else '' 
                        _text += f'\nxxQ{q_H_begin:02}_{q_V_begin:02}'
                        _text += f' {self.BEGIN_OF_BLOCK} '
                    else:
                        _text += f'{self.END_OF_BLOCK}\n'
                        _text += f'\n{self.BEGIN_OF_BLOCK}\n'                                    
                else:
                    if echo_quad:
                        left = groups_dict[group]['left']
                        top = groups_dict[group]['top']
                        q_H_begin = (int(top))//h_dist
                        q_V_begin = (int(left))//v_dist
                        _text += f'\nxxP{page:03}' if echo_page else ''                 
                        _text += f'\nxxQ{q_H_begin:02}_{q_V_begin:02}'
                        _text += f' {self.BEGIN_OF_BLOCK} '
                    else:                         
                        _text += f'\nxxP{page:03}' if echo_page else ''      
                        _text += f'\n\n{self.BEGIN_OF_BLOCK}\n'

                last_group = group

            if row.centered:
                _text += f'{self.BEGIN_OF_CENTERED_TEXT} '
                _text += row.text + ' '
                _text += f'{self.END_OF_CENTERED_TEXT}\n' 
            else:
                _text += row.text + '\n'

        if last_group != None and group != None:
            if echo_quad:
                right = groups_dict[group]['right']
                botton = groups_dict[group]['botton']
                q_H_end = (int(botton))//h_dist
                q_V_end = (int(right))//v_dist    
                _text += f'{self.END_OF_BLOCK} '
                _text += f'xxQ{q_H_end:02}_{q_V_end:02}\n'
            else:
                _text += f'{self.END_OF_BLOCK}\n' 
        return _text
        
    def extract_line_bounding_boxes(page, VERBOSE=False):
        '''
        Extract text as dataframe from img page with tesseract. 
        Sort words by line and build a new dataframe with bounding box per line, with group column
        
        input:
            * page: PIL object
            * verbose: boolean
        outbut:
            * pandas dataframe
        '''

        df = image2df(page, skipColumns=False)

        if VERBOSE:
            print(f'DATAFRAME WITH OCR DATA PAGE LOADED')

        df_grouped_by_block = df.groupby('block_num')
        groups = {}
        for group_name, df_group in df_grouped_by_block:
            groups[group_name] = wordsInLine(df_group, verbose=VERBOSE)
        if VERBOSE:
            print(f'GROUPS MAPPED AND TEXT FLOW FOR PAGE CREATED')   
        data = {}
        index = 0
        for key, value in groups.items():
            for key2, value2 in value.items():
                value2['group'] = key
                data[index] = value2
                index+=1
        if VERBOSE:
            print(f'DATA FOR ALL LINES WITH GROUPS AND WORDS FOR PAGE CREATED')

        return pd.DataFrame.from_dict(data, orient='index')

    def extract_group_bounding_boxes(self,df):
        blocks_df = df.groupby('group', as_index=False).agg({"left": "min", "right": "max","top":"min","botton":"max", "text": '\n'.join}); 
        blocks_df['size'] = blocks_df['right'] - blocks_df['left']
        blocks_df['middle'] = blocks_df['left'] + (blocks_df['size'])/2
        return blocks_df

    def count_groups_by_column(self, df):
        columns_dict = df.groupby('column', as_index=True).agg({"left": "min", "right": "max"}).to_dict('index')
        columns_samples = df['column'].value_counts().to_dict()
        for key, value in columns_samples.items():
            columns_dict[key]['samples'] = value
        return columns_dict
    
    def TriageGroupsByColumns(self, ds,  tolerance=.10, verbose=False):
        '''
        It traverses a pandas dataframe and samples groups that share almost the same 
        center position, which means a distance of self.page_width mutiplied by tolerance.
        
        inputs:
                ds: pandas dataframe with at least the columns group (group ID) 
                    and middle (page position of the center of the group)
        
        self.page_width: it relates to the width of page that serves as a size reference
        
        tolerance: it refers to the acceptable tolerable distance of center
        
            verbose: print detailed information for each loop
            
        output:
        a dict whose key is the column and values an array of group ids
        
        {0: [1],
            1: [8, 5, 11, 7, 13, 10, 14, 15, 12, 6, 9],
            2: [2],
            3: [22, 21, 18, 16, 20, 24, 19, 23, 17],
            4: [3]}

        '''
        ds = ds.sort_values(by=['middle'], ascending=True) 
        n = len(ds)
        columns = {}
        columnIndex = 0
        groupIndex = 0
        
        while groupIndex < n:

            row = ds.iloc[groupIndex]
            
            middle = row['middle']
            group = row['group']
            text = row['text'][:30].replace('\n', ' ')
            
            left, right = middle, middle + self.page_width * tolerance
            columns[columnIndex] = [group]
            if verbose:
                print(f'column: {columnIndex} | group: {group:2d} | middle: {middle: >#06.1f} | {text:>21}')
            groupIndex += 1
            if (groupIndex < n):
                row = ds.iloc[groupIndex]
                middle = row['middle']
                while groupIndex < n and middle < right:
                    group = row['group']
                    text = row['text'][:30].replace('\n', ' ')
                    columns[columnIndex].append(group)
                    if verbose:
                        print(f'column: {columnIndex} | group: {group:2d} | middle: {middle: >#06.1f} | {text:>21}') 
                    groupIndex += 1
                    if (groupIndex < n):
                        row = ds.iloc[groupIndex]
                        middle = row['middle']
            columnIndex += 1
            
        columns_by_groups = {}
        for key, value in columns.items():
            for item in value:
                columns_by_groups[item] = key

        return columns_by_groups