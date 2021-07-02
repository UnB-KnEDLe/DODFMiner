import json
from _pytest.python_api import raises
import requests
import os


url_ = 'https://dodf.df.gov.br/listar?'
downl = 'https://dodf.df.gov.br/index/visualizar-arquivo/?pasta='


#req1 returns list with available months for the given year
def req1(year):
    url1 = url_+f'dir={str(year)}'
    return url1

#req2 returns list with available DODFs for the given month
def req2(url1, month):
    if("_" in month):
        url2 = url1 + '/' + month
        req2 = requests.get(url2)
        content2 = json.loads(req2.content)
        dodfs = list(content2['data'].items())
        return(url2, dodfs)
    else:
        raise ValueError("month parameter format is wrong")


#req3 returns all pdfs from the selected DODF 
def req3(url2, dodf):
    url3 = url2+"/"+dodf.replace(" ","%20")
    req3 = requests.get(url3)
    content3 = json.loads(req3.content)
    pdfs = content3['data']
    return(url3, pdfs)


#Check for DODFs on the selected date
def check_date(year, month):
    if("_" in month):
        url1 = url_+f'dir={year}/{month}'
        req = requests.get(url1)
        content = json.loads(req.content)
        if('data' in content.keys()):
            if(len(content["data"]) > 0):
                return True
            else:
                return False
        else:
            return False
    else:
        raise ValueError("month parameter format is wrong")
        
#Generates download url
def get_downloads(year, month):
    if("_" in month):
        url1 = req1(year)
        url2, dodfs = req2(url1,month)
        _links = {}

        #Lista de DODFS:
        for dodf in dodfs:
            url3, pdfs = req3(url2,dodf[1])
            dodf_name = dodf[1]
            _pdfs = []
            for pdf in pdfs:
                index1 = url3.find(year)
                dir_ = (url3[index1:]).replace("/","|")+'|'+'&arquivo='
                index2 = pdf.rfind("/")
                arq_ = pdf[index2+1:].replace(" ","%20")
                link_download = downl+dir_+arq_
                _pdfs.append(link_download)
                _links[dodf_name] = _pdfs

        return(_links)
    else:
        raise ValueError("month parameter format is wrong")



