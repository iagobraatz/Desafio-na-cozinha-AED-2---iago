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

## Justificativa das escolhas

### Tabela Hash

Foi escolhida porque permite acesso rápido por identificador único, o que atende bem à busca por ID.

### Árvore Trie

Foi escolhida por ser eficiente para buscas por prefixo e por nome parcial.

### Árvore B

Foi usada para organizar receitas por um atributo numérico, possibilitando consultas ordenadas.

### Algoritmo guloso

Foi utilizado no módulo de recomendação, pois o objetivo é selecionar receitas iterativamente a partir de um critério de prioridade, como custo, tempo ou avaliação.

### Hash de integridade

Foi adotado um hash SHA-256 baseado no conteúdo da receita para detectar alterações indevidas, receitas duplicadas e conflitos entre versões.

## Observações

* O projeto foi desenvolvido em Python.
* O sistema foi pensado para execução local, sem depender da API durante a apresentação.
* O arquivo `receitas.json` deve permanecer na pasta `data` para o funcionamento correto.

## Repositório

Link do repositório: [https://github.com/iagobraatz/Desafio-na-cozinha-AED-2---iago](https://github.com/iagobraatz/Desafio-na-cozinha-AED-2---iago)

## Integrantes

* Iago Kainan Bubolz Braatz

## Data de entrega

18 de maio de 2026
