# fitcli ALPCD_2
Trabalho prático 1 de ALPCD (2026/2027, Ciência de Dados, Universidade do Minho).

A fitcli é uma CLI que criamos para buscar dados de exercícios físico à API pública wger. Algumas funcionalidades são: pesquisar exercícios por músculo e categoria, ver qual o tipo de esforço, contar ocorrências de equipamentos, gerar um workout, etc.

Utilizamos o 'typer' (CLI), 'requests' (API) e 're' (limpeza de texto e classificação).

## Como correr

Necessário ter Python 3.10 ou mais recente.

```bash
# 1. clonar o repo e entrar na pasta
git clone <link-do-repo>
cd ALPCD_2
 
# 2. criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / Mac
 
# 3. instalar as dependências
pip install -r requirements.txt
```

**Nota sobre o token:** os comandos `routines` e `routine` (os nossos extras) usam o endpoint `/routine/` da wger, que pede um token. Antes de correr, define a variável de ambiente `WGER_TOKEN`:
 
```powershell
$env:WGER_TOKEN="o_teu_token"      # PowerShell
```
```bash
export WGER_TOKEN="o_teu_token"    # Linux / Mac
```

Na primeira execução da CLI, são descarregados todos os dados da API e guardados em 2 ficheiros cache diferentes (um para o exercício e outro para as routines). Caso queira atualizar os dados, será necessário apagar os ficheiro cache e voltar a executar a CLI.

## Estrutura do projeto

```
ALPCD_2/
├── fitcli.py          # a CLI (comandos do typer)
├── main.py            # a lógica toda: API, cache, classificação, etc.
├── requirements.txt
└── README.md
```

Separámos assim para a CLI ficar só com a parte de receber argumentos e mostrar resultados, e o `main.py` tratar do resto. Isto também fez com que o `workout` fosse só juntar funções que já existiam.

## Comandos

| Comando | O que faz |
|---|---|
| `top N` | mostra os N exercícios mais recentes |
| `search TERMO N` | pesquisa por músculo ou categoria, com limite de N resultados |
| `type ID` | diz se o exercício é `compound`, `isolated`, `cardio` ou `other` |
| `equipment CATEGORIA` | conta quantas vezes cada equipamento aparece nas descrições dessa categoria |
| `workout MÚSCULOS ESFORÇO N` | gera um plano de treino (opção `--csv` para exportar) |
| `available` | lista as categorias, músculos e equipamentos que existem |
| `routines ID` | (extra) routines que usam um dado exercício |
| `routine ID` | (extra) mostra uma routine com os nomes dos exercícios |
 
Para ver a ajuda de qualquer comando: `python fitcli.py <comando> --help`.

## Exemplos

```bash
# os 10 exercícios mais recentes
python fitcli.py top 10
 
# 5 exercícios de bíceps
python fitcli.py search biceps 5
 
# tipo de esforço do exercício 192
python fitcli.py type 192
 
# equipamento mais mencionado na categoria chest
python fitcli.py equipment chest
 
# plano com até 5 exercícios compostos de bíceps e costas
python fitcli.py workout biceps,back compound 5
 
# plano com 3 exercícios isolados de peito e ombros, exportado para CSV
python fitcli.py workout chest,shoulders isolated 3 --csv treino.csv
 
# ver o que podemos pesquisar
python fitcli.py available
```
## Como funciona

**API:** usamos sempre `language=2` (inglês), um `User-Agent` que identifica o grupo, `raise_for_status()` para apanhar erros e seguimos o campo `next` de cada página até acabar, para ter todos os exercícios e não só os primeiros 100.
 
**Cache:** guardamos as respostas em JSON para não estar sempre a chamar a API. É muito mais rápido e é mais simpático para o servidor deles.
 
**`type`:** não há nenhum campo na API que diga se um exercício é composto ou isolado, por isso inferimos com regex pelo nome, pela descrição, pela categoria e pelo número de músculos. A ordem é esta:
1. `cardio`: o nome ou a descrição fala de correr, bicicleta, natação, etc.
2. `isolated`: aparecem palavras como *curl*, *extension*, *lateral raise*, *calf raise*...
3. `compound`: aparecem palavras como *squat*, *deadlift*, *press*, *row*, *pull-up*... ou o exercício trabalha 2 ou mais músculos
4. `other`: tudo o que sobra

**`equipment`:** limpamos o HTML das descrições com `re`, passamos tudo para minúsculas e contamos quantas vezes aparece cada palavra (`barbell`, `dumbbell`, `cable`, `machine`, `bodyweight`). No fim ordenamos de forma decrescente.
 
**`workout`:** para cada músculo da lista chama o `search`, filtra pelo tipo de esforço pedido e fica com os primeiros N.

## Extras

- `available`: mostra o que dá para pesquisar, para não estarmos a adivinhar nomes de músculos
- `routines` e `routine`: ligam os exercícios às routines públicas da wger, ou seja, encontras um exercício e vês em que routines ele aparece

## Quem fez o quê

- **Rafael:**
- **Mariana:** 
- **Carla:** 




