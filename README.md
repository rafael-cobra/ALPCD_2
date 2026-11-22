# fitcli ALPCD_2

Trabalho Prático 1 de ALPCD — Ciência de Dados, Universidade do Minho, 2026/2027.

A `fitcli` é uma aplicação de linha de comandos para consultar exercícios da API pública do wger. Permite pesquisar por músculo ou categoria, consultar detalhes e tipo de exercício, contar menções a equipamento e gerar planos de treino.

O projeto usa `Typer` para criar os comandos, `requests` para consultar a API e expressões regulares (`re`) para limpar e analisar texto.

## Requisitos

- Python 3.10 ou superior
- As dependências indicadas em `requirements.txt`

## Instalação

Clona o repositório e entra na pasta:

```bash
git clone https://github.com/rafael-cobra/ALPCD_2.git
cd ALPCD_2
```

Cria e ativa um ambiente virtual.

No Windows, usando PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

No Windows, usando a Linha de Comandos (CMD):

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

No Linux ou macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instala as dependências:

```bash
pip install -r requirements.txt
```

## Token para os comandos de rotinas

Os comandos `routines` e `routine` consultam rotinas públicas modelo do wger. Os dados ficam guardados em `cache_routines.json`.

Se esse ficheiro ainda não existir, é necessário definir `WGER_TOKEN` para a aplicação consultar a API. Se o cache já existir, os comandos usam-no sem voltar a consultar a API.

No PowerShell:

```powershell
$env:WGER_TOKEN="o_teu_token"
```

No Linux ou macOS:

```bash
export WGER_TOKEN="o_teu_token"
```

No CMD:

```bash
set WGER_TOKEN=o_teu_token
```

Não coloques o valor real do token no README nem o incluas num commit. Os comandos que consultam exercícios públicos não precisam de `WGER_TOKEN`. O token só é necessário para descarregar as rotinas quando `cache_routines.json` ainda não existe.

## Cache

A aplicação guarda os dados dos exercícios em `cache_exerciseinfo.json` e os dados das rotinas em `cache_routines.json`.

Os comandos normais carregam o cache dos exercícios. As rotinas só são carregadas quando se executa `routine` ou `routines`.

Para atualizar os dados dos exercícios, remove `cache_exerciseinfo.json` e executa novamente um comando normal. Para atualizar as rotinas, remove `cache_routines.json` e executa `routine` ou `routines`. Para descarregar novamente as rotinas, é necessário ter `WGER_TOKEN` definido.

## Estrutura do projeto

```text
ALPCD_2/
├── fitcli.py          # comandos da linha de comandos, definidos com Typer
├── main.py            # API, cache, pesquisa e classificação
├── requirements.txt   # dependências Python
└── README.md          # instruções e documentação
```

A separação permite que `fitcli.py` trate dos argumentos e da apresentação dos resultados, enquanto `main.py` contém a lógica de dados e de negócio.

## Comandos

| Comando | O que faz |
|---|---|
| `top N` | Mostra os N exercícios mais recentes do cache. |
| `search TERMO N` | Pesquisa por músculo ou categoria e mostra até N resultados em JSON. |
| `type ID` | Infere e mostra o tipo do exercício: `cardio`, `isolated`, `compound` ou `other`. |
| `info ID` | Mostra os detalhes do exercício, incluindo descrição, músculos e equipamento. |
| `equipment CATEGORIA` | Conta menções a termos de equipamento nas descrições dos exercícios dessa categoria. |
| `workout MÚSCULOS ESFORÇO N` | Gera um plano com até N exercícios por músculo. Aceita `compound`, `isolated` ou `any`. |
| `available` | Lista as categorias, os músculos, os equipamentos e os tipos disponíveis. |
| `routines EXERCISE_ID` | Lista rotinas públicas modelo do cache que incluem o exercício indicado. |
| `routine ROUTINE_ID` | Mostra o nome de uma rotina e os exercícios de cada dia. |

O comando `workout` também aceita `--equipment NOME` para filtrar pelo equipamento e `--csv FICHEIRO` para exportar o plano. As duas opções podem ser usadas em conjunto.

Para consultar as opções e a descrição de um comando:

```bash
python fitcli.py NOME_DO_COMANDO --help
```

Se executares a CLI sem argumentos, é apresentada a lista de comandos e a respetiva ajuda.

## Exemplos

```bash
# Mostrar os 10 exercícios mais recentes
python fitcli.py top 10

# Pesquisar até 5 exercícios relacionados com bíceps
python fitcli.py search biceps 5

# Consultar o tipo de um exercício existente no cache
python fitcli.py type 177
# Resultado esperado: cardio

# Consultar os detalhes de um exercício
python fitcli.py info 135

# Contar menções a equipamento nas descrições da categoria chest
python fitcli.py equipment chest

# Gerar um plano com até 5 exercícios compostos para bíceps e costas
python fitcli.py workout biceps,back compound 5

# Filtrar o plano por halteres
python fitcli.py workout biceps any 5 --equipment dumbbell

# Gerar um plano de exercícios isolados e exportá-lo para CSV
python fitcli.py workout chest,shoulders isolated 3 --csv treino.csv

# Consultar as categorias, músculos, equipamentos e tipos disponíveis
python fitcli.py available

# Mostra uma rotina e os exercícios de cada dia
python fitcli.py routines 84

# Lista rotinas públicas modelo que incluem o exercício indicado
python fitcli.py routine 50305
```

## Como funciona

### API

A aplicação consulta a API pública do wger. Pede os dados dos exercícios em inglês (`language=2`), envia um `User-Agent` que identifica o projeto e verifica erros HTTP com `raise_for_status()`. Quando a resposta indica que há mais páginas, segue o endereço `next` para recolher os restantes resultados.

### Classificação do tipo de exercício

A API não fornece diretamente os quatro tipos usados neste projeto. Por isso, a aplicação infere o tipo através do nome, da descrição, da categoria e dos músculos associados. A classificação segue esta ordem:

1. `cardio`: identifica termos de cardio no nome ou na descrição. Também pode usar pistas de esforço aeróbico ou de resistência quando a categoria é cardio.
2. `isolated`: identifica termos associados a exercícios isolados, como `curl`, `extension`, `lateral raise`, `front raise`, `butterfly` ou `hip adduction`.
3. `compound`: reconhece certos movimentos pelo nome, como `squat`, `deadlift`, `press`, `row`, `pull-up` e `kettlebell swing`. Também pode usar uma pista de movimento envolvendo joelhos e ancas, se a API associar pelo menos dois músculos.
4. `other`: aplica-se quando nenhuma das regras anteriores corresponde.

O número de músculos associado pela API não basta, por si só, para classificar um exercício como `compound`. Estas regras são heurísticas e podem falhar quando os nomes ou as descrições usam formas que ainda não estão contempladas.

### Equipamento

O comando `equipment` limpa o HTML das descrições, converte o texto para minúsculas e conta palavras inteiras como `barbell`, `dumbbell`, `cable`, `machine` e `bodyweight`, incluindo o plural simples. Os resultados são ordenados da contagem mais alta para a mais baixa.

Esta função conta menções nas descrições; não conta necessariamente o equipamento associado ao exercício no campo próprio da API. Já o filtro `workout --equipment` compara o nome indicado com o equipamento associado ao exercício.

### Plano de treino

O comando `workout` pesquisa exercícios para cada músculo indicado, filtra-os pelo tipo de esforço e, opcionalmente, pelo equipamento, e escolhe até N resultados por músculo. Pode mostrar o plano em JSON ou exportá-lo para CSV.

## Elementos do Grupo
|Nome|Número|
|---|---|
|Rafael Cobra|a114206|
|Carla Gonçalves|a17120|
|Mariana Policarpo|a114300|

