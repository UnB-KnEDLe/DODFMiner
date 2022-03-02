# Propriedades

## Abono (Modelo ner)

- Nome
- Matricula
- Cargo_efetivo
- Classe
- Padrao
- Quadro
- Fundamento_legal
- Orgao
- Processo_sei
- Vigencia
- Matricula_siape
- Cargo
- Lotacao

## Aposentadoria (Modelo ner)

- Ato
- Processo
- Nome_ato
- Cod_matricula_ato
- Cargo
- Classe
- Padrao
- Quadro
- Fund_legal
- Empresa_ato

## Retificação de aposentadoria (Regex)

- Tipo do Ato,
- Tipo de Documento
- Número do documento
- Data do documento 
- Número do DODF
- Data do DODF
- Página do DODF
- Nome do Servidor
- Matrícula
- Cargo
- Classe
- Padrao
- Matricula SIAPE
- Informação Errada
- Informação Corrigida

## Cessões (Regex)

- nome
- matricula
- cargo_efetivo
- classe
- padrao
- orgao_cedente
- orgao_cessionario
- onus
- fundamento legal
- processo_SEI
- vigencia
- matricula_SIAPE
- cargo_orgao_cessionario
- simbolo
- hierarquia_lotaca

## Exoneração (Modelos NER)

- Nome
- Matricula
- Simbolo
- Cargo_comissionado
- Hierarquia_lotacao
- Orgao
- Vigencia
- Carreir
- Fundamento_legal
- A_pedido_ou_nao
- Cargo_efetivo
- Matricula_siape
- Motivo

## Exoneração Efetivos (Modelos NER)

- Nome
- Matricula
- Cargo_efetivo
- Classe
- Padrao
- Carreira
- Quadro
- Processo_sei
- Vigencia
- A_pedido_ou_nao
- Motivo
- Fundamento_legal
- Orgao
- Simbolo
- Hierarquia_lotacao
- Cargo_comissionado

## Nomeração Efetivos (Modelo NER)

- Edital_normativo
- Data_edital_normativo
- Numero_dodf_edital_normativo
- Data_dodf_edital_normativo
- Edital_resultado_final
- Data_edital_resultado_final
- Numero_dodf_resultado_final
- Data_dodf_resultado_final
- Cargo
- Especialidade
- Carreira
- Orgao
- Candidato
- Classe
- Quadro
- Candidato_pne
- Padrao

## Nomeração Comissionado (Modelo NER)

- Edital_normativo
- Data_edital_normativo
- Numero_dodf_edital_normativo
- Data_dodf_edital_normativo
- Edital_resultado_final
- Data_edital_resultado_final
- Numero_dodf_resultado_final
- Data_dodf_resultado_final
- Cargo
- Especialidade
- Carreira
- Orgao
- Candidato
- Classe
- Quadro
- Candidato_pne
- Padrao

## Reversoes (Modelo NER)

- Processo_sei
- Nome
- Matricula
- Cargo_efetivo
- Classe
- Padrao
- Quadro
- Fundamento_legal
- Orgao
- Vigencia

## Sem efeito aposentadoria (Modelo NER)

- tipo_documento
- numero_documento
- data_documento
- numero_dodf
- data_dodf
- pagina_dodf
- nome
- matricula
- matricula_SIAPE
- cargo_efetivo
- classe
- padrao
- quadro
- orgao
- processo_SE

## Substituição

- Nome_substituto
- Cargo_substituto
- Matricula_substituto
- Nome_substituido
- Matricula_substituido
- Simbolo_substitut
- Cargo_objeto_substituicao
- Simbolo_objeto_substituicao
- Hierarquia_lotacao
- Orgao
- Data_inicial
- Data_final
- Matricula_siape
- Motivo

# Problemas nos modelos

### Abono:
- 'cargo' e 'cargo_efetivo'

### Nomeação:
- Dois campos 'Matricula_siape'
- 3 campos de cargo: 'Cargo_efetivo', 'Cargo_comissionado', 'Cargo'