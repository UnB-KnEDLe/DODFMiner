# JSON acts extraction tutorial 

This tutorial is meant to help in the process of extracting acts from the section 3 of the DODF JSON files manually. These are the types of acts extracted from the section 3:

- Contrato / Convênio
- Aditamento
- Licitação
- Anulação / Revogação
- Suspensão

*Requirements: in this tutorial, it is assumed that you have already installed the [DODFMiner requirements](./../../../../requirements.txt)*

The first step to do is importing the DODFMiner `ActsExtractor` class in order to extract the acts from a JSON file:

```Python
from dodfminer.extract.polished.core import ActsExtractor
```

Each of the 5 types of acts have their own class that manages the whole process of extraction from the JSON file. There are two ways to do so: extract all acts from a specific type or extract all of them at once. 

## Extracting a specific type of act

[text]

## Extracting all acts

In order to extract all acts at once, you have to use the `get_all_obj` method.

```Python
ActsExtractor.get_all_obj(file="PATH/TO/JSON/FILE.json")
```

- Parameters:
    - **file** (string) - Path to JSON file.

- Returns:
    - Dictionary containing the class objects correspondent to each type of act found.

## Returned object details

Within each class object in the returned dictionary, there's a pandas dataframe attribute (`df`) containing all the entities from that act type.

You can access them by the following keys:

- `aditamento`
- `licitacao`
- `suspensao`
- `anulacao_revogacao`
- `contrato_convenio`

Here's an example accessing the dataframe of `contrato_convenio` 

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
|       233       |      I TERMO ADITIVO AO CONTRATO BRB 011/2022     | I TERMO ADITIVO AO CONTRATO BRB 011/2022 Contr... |  I TERMO ADITIVO | [BRB, BRB, BRB] |        prorrogação 12 meses até 19/01/2024        |  1.096/2021  |       NaN      |        NaN       |
|       233       | EXTRATO DO 1º TERMO ADITIVO AO CONTRATO Nº 19/... | EXTRATO DO 1º TERMO ADITIVO AO CONTRATO Nº 19/... | 1º TERMO ADITIVO |  [SEEDF, SEEDF] | a ) Alterar a razão social da Contratada , de ... |      NaN     |     19/2022    |    14/12/2022    |

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

| **numero_dodf** |           **titulo**           |                      **text**                     | MODALIDADE_LICITACAO |            NUM_LICITACAO           |         ORGAO_LICITANTE         |                   OBJ_LICITACAO                   | VALOR_ESTIMADO |                  SISTEMA_COMPRAS                  | PROCESSO         | DATA_ABERTURA | CODIGO_SISTEMA_COMPRAS |
|:---------------:|:------------------------------:|:-------------------------------------------------:|:--------------------:|:----------------------------------:|:-------------------------------:|:-------------------------------------------------:|:--------------:|:-------------------------------------------------:|------------------|---------------|------------------------|
|       233       | AVISO DE ABERTURA DE LICITAÇÃO | AVISO DE ABERTURA DE LICITAÇÃO PREGÃO ELETRÔNI... |   PREGÃO ELETRÔNICO  |               26/2022              | Fundação Hemocentro de Brasília | aquisição de Materiais Médico-Hospitalares par... |       6.686,20 |                 www.gov.br/compras                |              NaN | NaN           | NaN                    |
|       233       |       AVISO DE LICITAÇÃO       |  AVISO DE LICITAÇÃO PREGÃO ELETRÔNICO PE Nº 274.. |    PREGÃO ELETRÔNICO | [274/2022, 00092-00055194.2022-84] |              Caesb              | Aquisição de materiais de ferro fundido para r... |       NaN      | [https : //www.gov.br/compras/pt-br, https : /... | 21.205.100.020-2 |    04/01/2023 | 974200                 |

### Suspensão

These are the entities captured in `suspensao` acts:

- numero_dodf
- titulo
- text
- PROCESSO
- DATA_ESCRITO
- OBJ_ADITIVO

Here's an example of the acts in a dataframe:

| **numero_dodf** |                     **titulo**                    |                      **text**                     |      **PROCESSO**      |                  **OBJ_ADITIVO**                  |                  **CONTRATANTE**                  | **NUM_AJUSTE** | **NUM_ADITIVO** | **DATA_ESCRITO** |
|:---------------:|:-------------------------------------------------:|:-------------------------------------------------:|:----------------------:|:-------------------------------------------------:|:-------------------------------------------------:|:--------------:|:---------------:|:----------------:|
|       215       |                 AVISO DE SUSPENSÃO                | AVISO DE SUSPENSÃO PREGÃO ELETRÔNICO POR SRP N... | 00055-00045741/2020-54 | a suspensão da licitação supracitada , a qual ... | Secretaria de Estado de Saúde do Distrito Federal |       NaN      |       NaN       |        NaN       |
|       118       | AVISO DE SUSPENSÃO DO PREGÃO ELETRÔNICO Nº 49/... | AVISO DE SUSPENSÃO DO PREGÃO ELETRÔNICO Nº 49/... |           NaN          |    a suspensão de realização do PE nº 049/2022    |                        BRB                        |       NaN      |       NaN       |        NaN       |

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

| **numero_dodf** |             **titulo**             |                      **text**                     |      **PROCESSO**      | **NUM_AJUSTE** |           **CONTRATANTE_ou_CONCEDENTE**           | **CONTRATADA_ou_CONVENENTE** | **CNPJ_CONTRATADA_ou_CONVENENTE** |                   **OBJ_AJUSTE**                  |        **VALOR**       | **CODIGO_UO** | **FONTE_RECURSO** | **NATUREZA_DESPESA** | **NOTA_EMPENHO** |                    **VIGENCIA**                   | **DATA_ASSINATURA** | **PROGRAMA_TRABALHO** | **NOME_RESPONSAVEL** | **CNPJ_CONTRATANTE_ou_CONCEDENTE** |
|:---------------:|:----------------------------------:|:-------------------------------------------------:|:----------------------:|:--------------:|:-------------------------------------------------:|:----------------------------:|:---------------------------------:|:-------------------------------------------------:|:----------------------:|:-------------:|:-----------------:|:--------------------:|:----------------:|:-------------------------------------------------:|:-------------------:|:---------------------:|:--------------------:|:----------------------------------:|
|        38       |         EXTRATO DE CONTRATO        | EXTRATO DE CONTRATO Contrato nº 9441. Assinatu... |           NaN          |       NaN      |                       CAESB                       |              NaN             |                NaN                | Fornecimento de acesso à sistema informatizado... | [23.722,14, 23.722,14] |     22.202    |  11.101.000.000-3 |          NaN         |        NaN       | 12 ( doze ) e 12 ( doze ) mês ( es ) , respect... |      21/02/2022     |          NaN          |          NaN         |                 NaN                |
|        38       | EXTRATO DE CONTRATO Nº 045723/2022 | EXTRATO DE CONTRATO Nº 045723/2022 Processo: 0... | 00366-00000136/2022-11 |   045723/2022  | ADMINISTRAÇÃO REGIONAL DE VICENTE PIRES/RA-VP ... |           OURO GÁS           |                NaN                | Aquisição de gás liquefeito de petróleo , boti... |        1.991,20        |     09133     |        100        |        339030        |    2022NE00016   | O contrato terá vigência do contrato será a pa... |      21/02/2022     | 04.122.6001.8517.0095 |          NaN         |                 NaN                |