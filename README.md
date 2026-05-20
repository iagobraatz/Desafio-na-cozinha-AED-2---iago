# Desafio na Cozinha

Projeto desenvolvido para a disciplina **Algoritmos e Estruturas de Dados II**.

## Sobre o trabalho

O sistema foi criado para organizar receitas de forma eficiente, permitir buscas rápidas, recomendar pratos com base em restrições e verificar a integridade dos dados armazenados.

A proposta segue o enunciado do trabalho, que exige o uso de estruturas de dados como **Tabela Hash**, **Árvore Trie** e **Árvore B**, além da implementação de **pelo menos um algoritmo guloso**.

## Fonte de dados

A base utilizada foi obtida a partir da **TheMealDB API** e salva localmente em um arquivo JSON.

### Arquivos de dados

* `data/receitas.json`
* `data/baixar_dados.py`

### Como os dados foram tratados

A API foi consultada para obter receitas com nome, categoria e ingredientes. Em seguida, os dados foram adaptados para o formato utilizado no projeto. Como a TheMealDB não fornece diretamente todos os campos numéricos necessários para o trabalho, foram adicionados localmente os seguintes atributos:

* tempo de preparo
* custo estimado
* avaliação dos clientes

Esses dados foram salvos em JSON para permitir execução local sem depender da conexão com a API durante a apresentação.

## Estruturas de dados implementadas

### 1. Tabela Hash

Utilizada para busca rápida por **ID** da receita.

Arquivo: `src/estruturas/hash_table.py`

### 2. Árvore Trie

Utilizada para busca por **nome** e por **prefixo** de receitas.

Arquivo: `src/estruturas/trie.py`

### 3. Árvore B

Utilizada para organização e busca por critérios numéricos, como **tempo de preparo**.

Arquivo: `src/estruturas/btree.py`

### 4. Algoritmo Guloso

Utilizado no modo Chef, para recomendar receitas com base em critérios como:

* menor custo
* menor tempo
* melhores avaliações

Arquivo: `src/services/recomendacao_service.py`

## Funcionalidades do sistema

### Módulo 1 — Livro de Receitas

Carregamento, armazenamento e listagem das receitas.

### Módulo 2 — Busca Rápida no Cardápio

Busca por:

* nome
* ID
* categoria
* prefixo

### Módulo 3 — Organização dos Ingredientes

Consulta de receitas por ingrediente específico.

### Módulo 4 — Recomendação do Chef

Sugestão de receitas com base em restrições e critérios definidos.

### Modo Investigação

Verificação de integridade das receitas armazenadas, com detecção de:

* alterações de conteúdo
* receitas duplicadas
* conflitos entre versões

### Modo Consulta Rápida

Recuperação eficiente de receitas por diferentes critérios.

## Organização do projeto

```txt
src/
├── data/
│   ├── receitas.json
│   └── baixar_dados.py
├── estruturas/
│   ├── __init__.py
│   ├── hash_table.py
│   ├── trie.py
│   └── btree.py
├── models/
│   ├── __init__.py
│   └── receita.py
├── services/
│   ├── __init__.py
│   ├── busca_service.py
│   ├── integridade_service.py
│   ├── recomendacao_service.py
│   └── receita_service.py
├── utils/
│   ├── __init__.py
│   └── hash_util.py
└── main.py
```

## Como executar

### Requisitos

* Python 3 instalado
* Nenhuma biblioteca externa obrigatória para rodar o sistema principal
* Apenas o `requests` é necessário caso seja executado o script de coleta de dados

### Instalação do `requests`

```bash
pip install requests
```

### Execução do sistema

Abra o terminal na pasta `src` e execute:

```bash
python main.py
```

Se necessário, também pode usar:

```bash
python3 main.py
```

### Execução do script de coleta de dados

Se quiser recriar o arquivo JSON local a partir da API:

```bash
python data/baixar_dados.py
```

## Menu do sistema

O sistema possui as seguintes opções:

* listar todas as receitas
* buscar por ID
* buscar por nome ou prefixo
* buscar por categoria
* modo investigação
* modo chef
* buscar por ingrediente
* salvar Árvore B em arquivo binário
* carregar Árvore B do arquivo binário para a memoria
* diagnóstico da Árvore B
* busca utilizando a Árvore B carregada do binário
* sair

## Justificativa das escolhas

### Tabela Hash

Foi escolhida porque permite acesso rápido por identificador único, o que atende bem à busca por ID.

### Árvore Trie

Foi escolhida por ser eficiente para buscas por prefixo e por nome parcial.

### Árvore B

Foi usada para organizar receitas por um atributo numérico, possibilitando consultas ordenadas. Além disso, na atividade de recuperação da P1, a estrutura foi expandida com persistência em arquivo binário, permitindo salvar e carregar a Árvore B diretamente do disco, simulando páginas de memória secundária e realizando buscas sem necessidade de reconstrução completa da árvore na RAM.

### Algoritmo guloso

Foi utilizado no módulo de recomendação, pois o objetivo é selecionar receitas iterativamente a partir de um critério de prioridade, como custo, tempo ou avaliação.

### Hash de integridade

Foi adotado um hash SHA-256 baseado no conteúdo da receita para detectar alterações indevidas, receitas duplicadas e conflitos entre versões.

## Observações

* O projeto foi desenvolvido em Python.
* O sistema foi pensado para execução local, sem depender da API durante a apresentação.
* O arquivo `receitas.json` deve permanecer na pasta `data` para o funcionamento correto.

## [RECUPERAÇÃO P1]

### Opção escolhida

Eu escolhi a **Opção C — Árvores B e Simulação de Memória Secundária (I/O)**.

### Dificuldade principal na prova

A maior dificuldade encontrada foi montar corretamente a **Árvore B** após as inserções, principalmente entender as divisões de nós e desenhar a estrutura final depois de todas as inserções. Também houve dificuldade na questão de remoção de elementos e reorganização da árvore.

### O que foi adicionado no T1

Para a recuperação, a Árvore B deixou de viver apenas na memória RAM e passou a ter persistência em arquivo binário. O sistema agora salva a estrutura em `data/arvore_b.bin` e consegue carregá-la depois, simulando páginas/blocos de disco. Também foi adicionada uma rotina de diagnóstico para verificar o estado da árvore e uma busca de teste realizada diretamente na árvore carregada do binário.

### Como testar a funcionalidade

1. Executar o sistema com:

```bash
python main.py
```

2. No menu, escolher a opção 8 para salvar a Árvore B em binário.
3. Fechar o programa.
4. Abrir o sistema novamente com:
   python main.py
5. No menu, escolher a opção 9 para carregar a Árvore B do arquivo binário.   
6. No menu, escolher a opção 10 para visualizar o diagnóstico da Árvore B.
7. No menu, escolher a opção 11 para simular a RAM limpa, carregar a Árvore B do arquivo binário e fazer a busca.
8. Digitar um valor de tempo de preparo existente, por exemplo 43.

## Repositório

Link do repositório: [Desafio na Cozinha - AED II](https://github.com/iagobraatz/Desafio-na-cozinha-AED-2---iago)

## Integrantes

* Iago Kainan Bubolz Braatz

## Data de entrega

25 de maio de 2026
