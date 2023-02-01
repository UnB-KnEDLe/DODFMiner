# JSON Acts Extraction Tutorial

This tutorial is meant to help in the process of extracting acts from the section 3 of the DODF JSON files manually. These are the types of acts extracted from the section 3:

- Contrato / Convênio
- Aditamento
- Licitação
- Anulação / Revogação
- Suspensão

*Requirements: in this tutorial, it is assumed that you have already installed the [DODFMiner requirements](./../../../../requirements.txt) and that you have got DODF JSON files, in case you don't, [this is where you can find them](#obtaining-json-files).*

The first step to do is importing the DODFMiner `ActsExtractor` class in order to extract the acts from a JSON file:

```Python
from dodfminer.extract.polished.core import ActsExtractor
```

Each of the 5 types of acts have their own class that manages the whole process of extraction from the JSON file.

There are two ways to do so: extracting all acts of a specific type or extracting all acts at once. The default model of extraction used is CRF, but you may [use your own trained model](#using-a-specific-model-with-scikit-learn-pipeline).

## Extracting a Specific Type of Act

The `get_act_obj` method will be used to extract one type of act from the JSON file.

```Python
ActsExtractor.get_act_obj(ato_id="ID", file="PATH/TO/JSON/FILE.json")
```

- Parameteres:
  - **ato_id** (string) - Act ID restricted to the following keys:
    - `aditamento`
    - `licitacao`
    - `suspensao`
    - `anulacao_revogacao`
    - `contrato_convenio`
  - **file** (string): Path of the JSON file.
  - **pipeline** (object): Scikit-learn pipeline object (optional).

- Returns:
  - An object of the desired act, already with extracted information.

## Using a Specific Model with Scikit-learn Pipeline

If you're not familiar with Scikit-learn Pipeline, you can <a href="https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html" target="_blank">learn more</a>.

If you want to use a different model you can do so by passing a scikit-learn pipeline object as a parameter of the `get_act_obj` method. There are a few things you have to do:

- Specify the pipeline parameter when calling the method. Ex: `get_act_obj(pipeline=pipeline_obj)`.
- Set an element in your pipeline with key `pre-processing` wich will be responsable for pre-processing and tokenization. This process has to be called by the method `Pipeline['pre-processing'].transform(X)` where `X` is a list with the input data.
- The model that extends the `BaseEstimator` class must return its output in IOB tag format.

In case of not following these requirements, the generated dataframe will not be correct.

Here's an example step-by-step:

```Python
# 1. Creating pipeline as required.

pipeline_obj = Pipeline([('pre-processing', Processing()), ('feature-extraction', FeatureExtractor()), ('model', Model())])

# 2. Pre-processing and tokenizing input data.

pipeline_obj['pre-processing'].transform(X)

# 3. Training model.

pipeline_obj.fit(X, y)

# 4. Calling method.

result = get_act_obj("aditamento", "PATH/TO/JSON/FILE.json", pipeline=pipeline_obj)

# 5. Accessing data extracted.

dataframe = result.df
```

## Extracting All Acts

In order to extract all acts at once, you have to use the `get_all_obj` method.

```Python
ActsExtractor.get_all_obj(file="PATH/TO/JSON/FILE.json")
```

- Parameters:
  - **file** (string) - Path to JSON file.

- Returns:
  - Dictionary containing the class objects correspondent to each type of act found.

## Returned object details

If you extract all acts at once, the returned object will be a dictionary with a key to each type of act. The value of each key is the respective act object.

You can access them by the following keys:

- `aditamento`
- `licitacao`
- `suspensao`
- `anulacao_revogacao`
- `contrato_convenio`

In case you extract only one type of act, the respective act object will be returned. The act objects have a pandas dataframe attribute `df` containing all acts extracted and their entities.

Here's an example of accessing the dataframe of `contrato_convenio`:

```Python
df = d['contrato_convenio'].df
```

### Aditamento

These are the entities captured in `aditamento` acts:

- numero_dodf
- titulo
- text
- NUM_ADITIVO
- CONTRATANTE
- OBJ_ADITIVO
- PROCESSO
- NUM_AJUSTE
- DATA_ESCRITO

Here's an example of the acts within the dataframe:

| **numero_dodf** |                     **titulo**                    |                      **text**                     |  **NUM_ADITIVO** | **CONTRATANTE** |                  **OBJ_ADITIVO**                  | **PROCESSO** | **NUM_AJUSTE** | **DATA_ESCRITO** |
|:---------------:|:-------------------------------------------------:|:-------------------------------------------------:|:----------------:|:---------------:|:-------------------------------------------------:|:------------:|:--------------:|:----------------:|
|       233       |      I TERMO ADITIVO AO CONTRATO BRB 011/2022     | I TERMO ADITIVO AO CONTRATO BRB 011/2022 Contr... |  I TERMO ADITIVO | [BRB, BRB, BRB] |        prorrogação 12 meses até 19/01/2024        |  1.096/2021  |    06/2021     |    19/12/2022    |
|       233       | EXTRATO DO 1º TERMO ADITIVO AO CONTRATO Nº 19/... | EXTRATO DO 1º TERMO ADITIVO AO CONTRATO Nº 19/... | 1º TERMO ADITIVO |  [SEEDF, SEEDF] | a ) Alterar a razão social da Contratada , de ... |      19/2022 |     19/2022    |    14/12/2022    |

### Licitação

These are the entities captured in `licitacao` acts:

- numero_dodf
- titulo
- text
- MODALIDADE_LICITACAO
- NUM_LICITACAO
- ORGAO_LICITANTE
- OBJ_LICITACAO
- VALOR_ESTIMADO
- SISTEMA_COMPRAS
- PROCESSO
- DATA_ABERTURA
- CODIGO_SISTEMA_COMPRAS

| **numero_dodf** |           **titulo**           |                      **text**                     | MODALIDADE_LICITACAO |            NUM_LICITACAO           |         ORGAO_LICITANTE         |                   OBJ_LICITACAO                   | VALOR_ESTIMADO |                  SISTEMA_COMPRAS                  |     PROCESSO     | DATA_ABERTURA  | CODIGO_SISTEMA_COMPRAS |
|:---------------:|:------------------------------:|:-------------------------------------------------:|:--------------------:|:----------------------------------:|:-------------------------------:|:-------------------------------------------------:|:--------------:|:-------------------------------------------------:|------------------|----------------|------------------------|
|       233       | AVISO DE ABERTURA DE LICITAÇÃO | AVISO DE ABERTURA DE LICITAÇÃO PREGÃO ELETRÔNI... |   PREGÃO ELETRÔNICO  |               26/2022              | Fundação Hemocentro de Brasília | aquisição de Materiais Médico-Hospitalares par... |   6.686,20     |                 www.gov.br/compras                |     35/2022      |   22/12/2022   |         925008         |
|       233       |       AVISO DE LICITAÇÃO       |  AVISO DE LICITAÇÃO PREGÃO ELETRÔNICO PE Nº 274.. |    PREGÃO ELETRÔNICO | [274/2022, 00092-00055194.2022-84] |              Caesb              | Aquisição de materiais de ferro fundido para r... |  3.835.600,90  | [https:/www.gov.br/compras/pt-br, https:/...      | 21.205.100.020-2 |   04/01/2023   |         974200         |

### Suspensão

These are the entities captured in `suspensao` acts:

- numero_dodf
- titulo
- text
- PROCESSO
- DATA_ESCRITO
- OBJ_ADITIVO

Here's an example of the acts in a dataframe:

| **numero_dodf** |                     **titulo**                    |                      **text**                     |      **PROCESSO**      |                  **OBJ_ADITIVO**                  |                  **CONTRATANTE**                  | **NUM_AJUSTE** | **NUM_ADITIVO** |     **DATA_ESCRITO**    |
|:---------------:|:-------------------------------------------------:|:-------------------------------------------------:|:----------------------:|:-------------------------------------------------:|:-------------------------------------------------:|:--------------:|:---------------:|:-----------------------:|
|       215       |                 AVISO DE SUSPENSÃO                | AVISO DE SUSPENSÃO PREGÃO ELETRÔNICO POR SRP N... | 00055-00045741/2020-54 | a suspensão da licitação supracitada , a qual ... | Secretaria de Estado de Saúde do Distrito Federal |    14/2021     |     03/2021     | 11 de novembro de 2021  |
|       118       | AVISO DE SUSPENSÃO DO PREGÃO ELETRÔNICO Nº 49/... | AVISO DE SUSPENSÃO DO PREGÃO ELETRÔNICO Nº 49/... | 00050-00002711/2021-75 |    a suspensão de realização do PE nº 049/2022    |                        BRB                        |    21/2022     |     58/2021     |       07/10/2021        |

### Anulação e Revogação

These are the entities captured in `anulacao_revogacao` acts:

- numero_dodf
- titulo
- text
- IDENTIFICACAO_OCORRENCIA
- MODALIDADE_LICITACAO

Here's an example of the acts in a dataframe:

| **numero_dodf** |            **titulo**           |                      **text**                     | IDENTIFICACAO_OCORRENCIA | MODALIDADE_LICITACAO |
|:---------------:|:-------------------------------:|:-------------------------------------------------:|:------------------------:|:--------------------:|
|       160       | AVISO DE REVOGAÇÃO DE LICITAÇÃO | AVISO DE REVOGAÇÃO DE LICITAÇÃO O Presidente d... |                REVOGAÇÃO |         Concorrência |
| 38              | AVISO DE REVOGAÇÃO DE LICITAÇÃO | AVISO DE REVOGAÇÃO DE LICITAÇÃO A Caesb torna ... | Caesb                    | Licitação Fechada    |

### Contrato/Convênio

These are the entities captured in `contrato_convenio` acts:

- numero_dodf
- titulo
- text
- PROCESSO
- NUM_AJUSTE
- CONTRATANTE_ou_CONCEDENTE
- CONTRATADA_ou_CONVENENTE
- CNPJ_CONTRATADA_ou_CONVENENTE
- OBJ_AJUSTE
- VALOR
- CODIGO_UO
- FONTE_RECURSO
- NATUREZA_DESPESA
- NOTA_EMPENHO
- VIGENCIA
- DATA_ASSINATURA
- PROGRAMA_TRABALHO
- NOME_RESPONSAVEL
- CNPJ_CONTRATANTE_ou_CONCEDENTE

Here's an example of the acts in a dataframe:

| **numero_dodf** |             **titulo**             |                      **text**                     |      **PROCESSO**        | **NUM_AJUSTE**  |           **CONTRATANTE_ou_CONCEDENTE**           | **CONTRATADA_ou_CONVENENTE** | **CNPJ_CONTRATADA_ou_CONVENENTE** |                   **OBJ_AJUSTE**                  |        **VALOR**       | **CODIGO_UO** | **FONTE_RECURSO** | **NATUREZA_DESPESA** | **NOTA_EMPENHO** |                    **VIGENCIA**                   | **DATA_ASSINATURA** | **PROGRAMA_TRABALHO** |   **NOME_RESPONSAVEL**   | **CNPJ_CONTRATANTE_ou_CONCEDENTE** |
|:---------------:|:----------------------------------:|:-------------------------------------------------:|:------------------------:|:---------------:|:-------------------------------------------------:|:----------------------------:|:---------------------------------:|:-------------------------------------------------:|:----------------------:|:-------------:|:-----------------:|:--------------------:|:----------------:|:-------------------------------------------------:|:-------------------:|:---------------------:|:------------------------:|:----------------------------------:|
|        38       |         EXTRATO DE CONTRATO        | EXTRATO DE CONTRATO Contrato nº 9441. Assinatu... | 00146-0000000457/2021-01 |   37/2021       |                       CAESB                       |       L2A UNIAO LTDA         |        90.180.605/0001-02         | Fornecimento de acesso à sistema informatizado... | [23.722,14, 23.722,14] |     22.202    |  11.101.000.000-3 |       4.4.90.51      |    2021NE00764   | 12 ( doze ) e 12 ( doze ) mês ( es ) , respect... |      21/02/2022     | 28.845.0903.00NR.0053 |     Bruno Costa Nunes    |          23.791.169/0001-02        |
|        38       | EXTRATO DE CONTRATO Nº 045723/2022 | EXTRATO DE CONTRATO Nº 045723/2022 Processo: 0... |  00366-00000136/2022-11  |   045723/2022   | ADMINISTRAÇÃO REGIONAL DE VICENTE PIRES/RA-VP ... |           OURO GÁS           |        27.983.951/0001-84         | Aquisição de gás liquefeito de petróleo , boti... |        1.991,20        |     09133     |        100        |        339030        |    2022NE00016   | O contrato terá vigência do contrato será a pa... |      21/02/2022     | 04.122.6001.8517.0095 |  THIAGO H. M. DOS SANTOS |          16.615.705/0001-53        |

## Obtaining JSON Files

If you do not have any JSON file to extract data from, you can find them in <a href="https://www.dodf.df.gov.br/index/jornal-json" target="_blank">this page</a>. In your web browser, just right click on the page, click on "save as" and select json file.

The page is updated everyday with the DODF of the day. Unfortunatelly there's not a database available of previous DODFs.
