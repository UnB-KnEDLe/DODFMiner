# Todos os imports necessários para testar o nosso módulo de segmentação.

# A classe ContentExtractor é responsável por extrair o texto puro dos Pdfs.
from dodfminer.extract.pure.core import ContentExtractor

# Essa é a nossa classe principal do core de Segmentação. Ela é o nosso foco de teste.
from dodfminer.extract.polished.segmentation.core import Segmentation
import os

# Os arquivos necessários para fazer os testes sempre estarão dentro da pasta "tests/support".
# Coloquei um DODF na pasta support que tenho certeza que o modelo encontra segmentos de aposentadoria nele.  
file_not_empty = ""+os.path.dirname(__file__)+"/support/DODF 195 14-10-2020 INTEGRA.pdf"


# O modelo n encontra modelos de aposentadoria neste DODF.
file_empty = ""+os.path.dirname(__file__)+"/support/DODF 001 01-01-2019 EDICAO ESPECIAL.pdf"

""" 
Começaremos os testes agora.....

Toda função de teste deve começar com prefixo "test_". Isso que indica para
a biblioteca que essa função testa alguma coisa no nosso código.

Outro padrão é o nome auto explicativo, ou seja, vcs irão descrever brevemente no
nome da função o que ela testa. Dessa maneira, caso ocorra algum erro, o pytest
apresenta o nome da função que falhou. Assim se torna mais fácil identificar
onde esta o erro.

Inicialmente testaremos somente a classe Segmentation. Ela possui somente
uma função "extract_segments" e é a classe que utiliza todo o código contido no core. 
Se garantirmos que ela funciona podemos ter uma maior confiança no resto 
do código do módulo. Portanto, testaremos todas as declarações que 
existem dentro dela, ou seja, todos os possíveis caminhos que são tomados dentro dela.

Antes de testar qualquer função é importante entender as entradas e as saídas dela.
A função "Segmentation.extract_segments", recebe um texto e um argumento act_name como entrada,
ambos tipo string. Tal função esta localizada no core do módulo segmentation. O caminho
até o módulo se apresenta na parte dos imports.

O argumento "text" é o texto que o módulo usará para extrair os segmentos. E "act_name" é o nome
do ato q está sendo extraido. A função usa isso pra checar se o modelo atual
tem treinamento para extrair o ato desejado. Essa informação é passada para o código manualmente
na variável "model_cover_list" definida no início do código do módulo. ATUALMENTE SÓ TEMOS
O MODELO TREINADO COM OS ATOS DE APOSENTADORIA.

Caso o modelo atual n tenha treinamento do ato solicitado a função avisa o usuário
e retorna o texto originalmente passado como argumento.
"""


"""
Nota Geral: Vcs podem checar as mensagens que foram apresentadas no terminal utilizando:

captured = capsys.readouterr()

E passando como argumento da função de teste a variável "capsys". "def teste(capsys)"
"""



"""
Como exemplo, fiz o teste da funcionalidade mais básica da função. Aqui eu suponho que 
a função funcionara da maneira correta com todos os parâmetros corretos.
Para isso utilizo o arquivo "file_not_empty" na qual sei que existem segmentos nele. 

Eu sei q a saída dessa função quando é correta se apresenta como uma lista de strings.
Então como um teste básico, basta eu checar se o tamanho da lista de retorno é maior que 0.
"""
def test_segmentation_extract_segments_act_in_cover_list():
    # Perceba que a função extract_segments não extrai o texto dos pdfs, quem faz isso
    # é um outra classe do DODFMiner o ContentExtractor. E pode ser usada como na linha abaixo. 
    text = ContentExtractor.extract_text(file_not_empty)
    # Retirado o texto do PDF agora podemos passar para a função a ser testada.
    segments = Segmentation.extract_segments(text, 'Aposentadoria')
    # A linha assert dirá para o pytest se o teste foi bem sucedido.
    assert len(segments) > 0

# THAIS
def test_segmentation_extract_segments_act_not_in_cover_list(capsys):
    """
    Nesse teste faremos o teste do primeiro if da função fazendo a pergunta:
    E se o modelo n tiver sido treindo com o ato passado?
    Tecnicamente, e se act_name n estiver em model_cover_list?
    Se checarmos o resultado vemos que ela deve retornar um texto logo depois de uma mensagem.
    Então nossos "asserts" devem checar tanto se a mensagem foi apresentada quanto se o texto esta
    presente no retorno.
    """
    text = ContentExtractor.extract_text(file_not_empty)
    segments = Segmentation.extract_segments(text, 'reversoes')
    captured = capsys.readouterr()
    assert '[Segmentation] The current model is not trained with this act yet. Changing to pure text' in captured.out
    assert segments == text

# DANIEL
def test_segmentation_extract_segments_none_act_found():
    """
    Nesse teste checaremos se ao colocar um DODF em que ele n encontra nenhum segmento, ele
    retorna corretamente uma mensagem e o texto original no DODF. Igual ao teste de cima
    somente muda a mensagem que mostra para o usuário.
    """
    text = ContentExtractor.extract_text(file_empty)

    segmentation = Segmentation.extract_segments(text, 'Aposentadoria')

    assert segmentation == text

# IAN
def test_segmentation_extract_segments_successful_correct_message(capsys):
    """
    Esse teste é um tanto simples, ele repete o que o primeiro teste faz, porém ao invés
    de checar se os segmentos foram extraidos, ele checará se as 3 mensagens para o usuário aparecem
    caso ele consiga extrair corretamente os segmentos.
    """
    text = ContentExtractor.extract_text(file_not_empty)
    segments = Segmentation.extract_segments(text, 'Aposentadoria')

    captured = capsys.readouterr()

    assert ('[Segmentation] Segmentation is being applied...' and '[Segmentation] Finished.') in captured.out

# GUILHERME
def test_segmentation_extract_segments_first_argument_not_text():
    """
    Nesse teste faremos o teste se o código realmente retorna alguma exceção caso
    não seja passado um texto como argumento primário.
    """
    assert True == True

# GUILHERME
def test_segmentation_extract_segments_if_model_is_not_present():
    """
    Essa função faz a extração de segmentos utilizando um modelo de IA, portanto esse modelo
    precisa ser carregado de algum lugar já que não vem durante a instalação da biblioteca.
    Esse teste irá checar se a biblioteca realmente efetua o download do modelo caso ele n esteja presente
    nos arquivos da biblioteca. Como solução proponho excluir o modelo existente 
    (Ver na função qual o caminho para o modelo) e executá-la para extrair normalmente. 
    Se ao final vc obtiver os segmentos dentro de file_not_empty o assert é correto. 
    """
    assert True == True

