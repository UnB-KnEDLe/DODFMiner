from bs4 import BeautifulSoup
import os  # formataçao para OS em caminhos de arquivos
import requests


def download(url, endereco):
    resposta = requests.get(url)  # retorna binarios que compoe o arq

    try:
        with open(endereco, 'wb') as novo_arquivo:  # wb: escrita e binario
            novo_arquivo.write(resposta.content)
        print('Download salvo em {}'.format(endereco))
    except:
        print('Ocorreu um Erro')


MONTHS_STRING = ["", "01_Janeiro", "02_Fevereiro", "03_Mar%E7o", "04_Abril",
                 "05_Maio", "06_Junho", "07_Julho", "08_Agosto",
                 "09_Setembro", "10_Outubro", "11_Novembro", "12_Dezembro"]

ano = int(input('Escolha um ano:'))
mes = int(input('Escolha um mes:'))
mes_format = ""

for y in range(0, 13):
    if(mes == y):
        mes_format = MONTHS_STRING[y]


# Base URL
url_ = "http://www.buriti.df.gov.br/ftp/novo_portal_gdf/novo_dodf.asp?Ano={}&Mes={}&dir=".format(
    ano, mes_format)


r = requests.get(url_)
soup = BeautifulSoup(r.content, 'html.parser')

# Find options
select = soup.find('select', attrs={
    'class': 'chzn-select', 'data-placeholder': 'Selecione o Diário...'})
options = select.find_all('option')


# DODF choice
for c in range(1, len(options)):
    print('Opção {} : {}'.format(c, options[c].text))
opcao = int(input('Escolha uma opção:'))
txt = options[opcao].text
txt_cadeia = txt.split()

# Complete url formation
for d in range(0, len(txt_cadeia)):
    if(d == len(txt_cadeia)-1):
        url_ = url_+txt_cadeia[d]
    else:
        url_ = url_+txt_cadeia[d]+'+'
url_link = url_

rr = requests.get(url_link)
soup2 = BeautifulSoup(rr.content, 'html.parser')

find_links = soup2.find_all('a')
links = []

base = "http://www.buriti.df.gov.br/ftp"
for link in find_links:
    links.append(base+link.get('href')[2:].replace(' ', '%20'))
    print(link.get('href'))

count = 0
for url in links:
    output = os.path.join('files/', 'file{}.pdf'.format(count))
    download(url, output)
    count += 1
