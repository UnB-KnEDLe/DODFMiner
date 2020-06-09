# Guia de Contribuição  

## Como contribuir?

Para contribuir com o projeto é muito fácil e cada pouquinho conta! Basta seguir os seguintes passos:

* *Fork* do repositório (apenas para usuários externos)
* Criar [*branchs*](CONTRIBUTING.md#política-de-branches)
* Seguir a política de [*commits*](CONTRIBUTING.md#política-de-commits)
* Submeter [*Pull Request*](CONTRIBUTING.md#política-de-merges-e-pull-requests)


### Política de Branches  

#### *master*

A branch *master* é a branch de produção, onde ficará a versão estável do projeto. Ela estará bloqueada para commits e para pushs.
Veja a política de merges no tópico [Merges para *master*](CONTRIBUTING.md#merges-para-master).

#### *development*

A branch *development* é a branch de desenvolvimento, onde o trabalho das outras branchs será unificado e onde será criada uma versão estável para mesclar com a *master*.
Assim como a *master* ela está bloqueada para commits e pushs.
Veja a política de merges no tópico [Merges para development](CONTRIBUTING.md#merges-para-development)
merges para *development*</a>.

#### Nome das Branches  

As branchs de desenvolvimento de features serão criadas a partir da branch *development* com a nomenclatura padrão `x_nome_da_issue`, onde o `x` representa o código de rastreio da issue.

### Política de Commits

Os commits devem ser feitos usando o parâmetro `-s` para indicar sua assinatura no commit.

```
git commit -s
```
A issue em questão deve ser citada no commit, para isso, basta adicionar `#<numero_da_issue>`.

```
 #5 Fazendo guia de contribuição
```

** \*\*Por padrão, o caracter `#` define uma linha de comentário no arquivo da mensagem do commit. Para resolver este problema, use o commando:**
```
git config --local core.commentChar '!'
```

Igualmente, para commits em dupla deve ser usado o comando `-s` , e deve ser adicionado a assinatura da sua dupla.

```
git commit -s
```
Comentário do commit:
```
Making contribution guide

Signed-off-by: Isaque Alves <isaquealvesdl@gmail.com>
Signed-off-by: Felipe Campos <fepas.unb@gmail.com>
```

Para que ambos envolvidos no commit sejam incluidos como contribuintes no gráfico de commits do GitHub, basta incluir a instrução `Co-authored-by:` na mensagem:

```
Making contribution guide

Signed-off-by: Isaque Alves <isaquealvesdl@gmail.com>
Signed-off-by: Felipe Campos <fepas.unb@gmail.com>

Co-authored-by: Isaque Alves <isaquealvesdl@gmail.com>
Co-authored-by: Felipe Campos <fepas.unb@gmail.com>

```


Para commits que encerram a resolução de uma issue, deve-se iniciar a mensagem do commit com `Fix #<numero_da_issue> <mensagem>`, para que a issue seja [encerrada automaticamente](https://help.github.com/articles/closing-issues-using-keywords/) quando mesclada na `master`.

Exemplo de comentário do commit:
```
Fix #5 Finalizando guia de contribuição do projeto
```

Para commits que incluem uma pequena mudança em uma issue que já teve sua resolução encerrada, deve-se iniciar a mensagem do commit com `HOTFIX #<numero_da_issue> <mensagem>`

Exemplo de comentário do commit:
```
HOTFIX #5 Atualizando guia de contribuição do projeto
```

### Política de Merges e Pull Requests

#### Pull Requests

Pull requests devem ser feitos para a branch *master* seguindo as regras e os passos do tópico [*Merges para master*](CONTRIBUTING.md#merges-para-master). No conteúdo do pull request deve haver uma descrição clara do que foi feito.

Deve ser seguido o [template Pull Request](docs/pull_request_template.md).

##### Work in Progress

Caso haja a necessidade de atualizar a branch *master* antes de concluir a issue, o nome do pull request deve conter WIP:<X_nome_da_branch> para que a branch não seja deletada.

#### Merges para *master*
Os merges para *master* deverão ser feitos quando a funcionalidade ou refatoração estiverem de acordo com os seguintes aspectos:  
- Funcionalidade ou refatoração concluída;
- *Build* do Travis passando;
- Progredir ou manter a porcentagem de cobertura de teste;
- Funcionalidade revisada por algum outro membro.

Para fazer um merge para *master* os passos a serem seguidos são:  
- `git checkout branch_de_trabalho`;
- `git pull --rebase origin master`;
- `git push origin branch_de_trabalho`;
- Abrir pull request via interface GitHub;
- Aguardar Code Review


##### Code Review
O code review deve ser feito por um ou mais membros da equipe que não participaram das modificações.
Após pelo menos uma aprovação de Code Review, Status Check (Travis, CodeClimate) o PullRequest poderá ser aceito;

Para aceitar o PullRequest, deve-se usar a opção *merge* no Github.

![Merge](/docs/assets/img/merges.png)

##### Cobertura de testes
A Cobertura de código é avaliada constantemente e o objetivo é que a mesma nunca diminua. "Código testado gera menos retrabalho e mais qualidade de vida".

OBS: linhas de `console.log()` costumam não ser contabilizadas na cobertura de código. E geralmente não devem. Para resolver este problema, você pode adicionar o seguinte comentário na linha anterior ao `console.log()`:

```
/* istanbul ignore next */
```

Exemplo:
```nodejs
/* istanbul ignore next */
console.log("Mensagem de Checkpoint");
```

#### Tag's

<!-- Explicar tag's -->
