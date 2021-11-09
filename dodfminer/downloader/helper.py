import json
import requests


LISTAR_URL = 'https://dodf.df.gov.br/listar?'
DOWNLOAD_URL = 'https://dodf.df.gov.br/index/visualizar-arquivo/?pasta='


# req1 returns list with available months for the given year
def req1(year):
    url1 = LISTAR_URL+f'dir={str(year)}'
    return url1


# req2 returns list with available DODFs for the given month
def req2(url1, month):
    if "_" in month:
        url2 = url1 + '/' + month
        request2 = requests.get(url2)
        content2 = json.loads(request2.content)
        dodfs = list(content2['data'].items())
        return(url2, dodfs)

    raise ValueError("month parameter format is wrong")


# req3 returns all pdfs from the selected DODF
def req3(url2, dodf):
    url3 = url2+"/"+dodf.replace(" ", "%20")
    request3 = requests.get(url3)
    content3 = json.loads(request3.content)
    pdfs = content3['data']
    return(url3, pdfs)


# Check for DODFs on the selected date
def check_date(year, month):
    if "_" in month:
        url1 = LISTAR_URL+f'dir={year}/{month}'
        print(url1)
        req = requests.get(url1)
        content = json.loads(req.content)
        if 'data' in content.keys():
            return len(content["data"]) > 0
        return False

    raise ValueError("month parameter format is wrong")

# Generates download url


def get_downloads(year, month):
    if "_" in month:
        url2, dodfs = req2(req1(year), month)
        _links = {}

        # Lista de DODFS:
        for dodf in dodfs:
            url3, pdfs = req3(url2, dodf[1])
            dodf_name = dodf[1]
            _pdfs = []
            for pdf in pdfs:
                dir_ = (url3[url3.find(year):]).replace("/", "|")+'|'+'&arquivo='
                index2 = pdf.rfind("/")
                arq_ = pdf[index2+1:].replace(" ", "%20")
                link_download = DOWNLOAD_URL+dir_+arq_
                _pdfs.append(link_download)
                _links[dodf_name] = _pdfs

        return _links

    raise ValueError("month parameter format is wrong")
