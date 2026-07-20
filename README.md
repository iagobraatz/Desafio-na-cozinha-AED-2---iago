# Desafio na Cozinha

Projeto desenvolvido para a disciplina **Algoritmos e Estruturas de Dados II**.

Este repositório contém o **Trabalho 1** (organização, busca e recomendação de receitas) e o **Trabalho 2** (dependências de produção, otimização de menus, logística de delivery e roteirização), que reutiliza e expande a base construída no T1.

## Sumário

* [Sobre o trabalho](#sobre-o-trabalho)
* [Fonte de dados](#fonte-de-dados)
* [Estruturas de dados implementadas](#estruturas-de-dados-implementadas)
* [Funcionalidades do sistema](#funcionalidades-do-sistema)
* [Organização do projeto](#organização-do-projeto)
* [Como executar](#como-executar)
* [Menu do sistema](#menu-do-sistema)
* [Justificativa das escolhas](#justificativa-das-escolhas)
* [Bibliotecas utilizadas](#bibliotecas-utilizadas)
* [Análise de complexidade](#análise-de-complexidade)
* [Dimensões das redes utilizadas](#dimensões-das-redes-utilizadas)
* [Observações](#observações)
* [Recuperação P1 (T1)](#recuperação-p1)
* [Trabalho 2](#trabalho-2)
* [Repositório](#repositório)
* [Integrantes](#integrantes)
* [Data de entrega](#data-de-entrega)

## Sobre o trabalho

O sistema foi criado para organizar receitas de forma eficiente, permitir buscas rápidas, recomendar pratos com base em restrições e verificar a integridade dos dados armazenados (T1). No T2, o sistema foi expandido para modelar dependências entre preparações, otimizar menus sob múltiplas restrições, planejar a logística de um serviço de delivery e roteirizar entregas — sempre reaproveitando as receitas, estruturas e serviços já existentes.

A proposta segue os enunciados dos dois trabalhos, que exigem o uso de estruturas de dados como **Tabela Hash**, **Árvore Trie**, **Árvore B** e **Grafo**, além de algoritmos como **guloso**, **programação dinâmica**, **ordenação topológica**, **árvore geradora mínima**, **caminho mínimo**, **fluxo máximo** e uma **heurística de otimização combinatória**.

## Fonte de dados

### Receitas (T1)

A base utilizada foi obtida a partir da **TheMealDB API** e salva localmente em um arquivo JSON.

**Arquivos:** `data/receitas.json`, `data/baixar_dados.py`

A API foi consultada para obter receitas com nome, categoria e ingredientes. Como a TheMealDB não fornece diretamente todos os campos numéricos necessários, foram adicionados localmente:

* tempo de preparo
* custo estimado
* avaliação dos clientes

Esses dados foram salvos em JSON para permitir execução local sem depender da API durante a apresentação. A base final possui **606 receitas** em **14 categorias**.

### Enriquecimento das receitas (T2)

Para os Módulos 6 e o desafio extra, `receitas.json` foi enriquecido localmente (sem nova consulta à API) com 5 campos novos, calculados a partir dos dados já existentes:

**Arquivo:** `data/enriquecer_dados.py` (gera backup automático em `data/receitas_backup.json` antes de sobrescrever)

| Campo | Como foi calculado |
|---|---|
| `classe_prato` | Mapeamento a partir da categoria: `Dessert` → sobremesa; `Starter` + `Side` → entrada; demais categorias → principal |
| `valor_venda` | `custo_estimado × fator`, fator sorteado entre 1.6 e 2.4 (markup de 60% a 140%), com seed fixa (42) para reprodutibilidade |
| `ingredientes_raros` / `possui_ingrediente_raro` | Um ingrediente é considerado raro se aparece em **apenas 1** das 606 receitas da base (frequência real calculada sobre os dados, não sorteada) |
| `dificuldade_logistica` | Pontuação normalizada (tempo de preparo + quantidade de ingredientes) dividida em tercis reais da base (baixa/média/alta, ~33% cada) |

Resultado: 428 receitas principais, 50 entradas, 128 sobremesas; 234 receitas (38,6%) com pelo menos um ingrediente raro; dificuldade dividida em 203/202/201 (baixa/média/alta).

### Dependências de preparo (Módulo 5)

A TheMealDB não modela preparações intermediárias (molhos, massas, caldos), então essa rede foi **construída manualmente**, ligando preparações genéricas reais de cozinha profissional a receitas reais da base (por ID).

**Arquivos:** `data/dependencias_preparo.json`, `data/gerar_dependencias_preparo.py`

Contém 21 preparações (13 de nível básico como caldos e molhos-base, 5 de nível 2 dependendo de preparações básicas, 1 de nível 3) e 25 receitas reais dependentes, formando um grafo direcionado com **46 vértices e 52 arestas válidas**. Foram incluídas propositalmente duas inconsistências para exercitar o Modo Investigação:

* um **ciclo** isolado entre dois preparos fictícios (`Massa Recheada` ↔ `Recheio Especial`), simulando um erro de cadastro;
* uma **referência quebrada**: a receita `Teriyaki Chicken Casserole` depende de um preparo (`Molho Teriyaki`) nunca cadastrado.

### Rede de entrega (Módulo 7)

Também construída manualmente, já que não existe base pública para isso. Representa uma rede de distribuição fictícia sobre **bairros reais de Pelotas/RS**, organizados em 5 zonas (Centro, Três Vendas, Fragata, Laranjal, Barragem), cada uma com uma cozinha/estação de produção associada.

**Arquivos:** `data/rede_entrega.json`, `data/gerar_rede_entrega.py`

Contém 4 estações de produção e 26 regiões de entrega, ligadas por 58 conexões ponderadas por tempo estimado (minutos) — **30 vértices e 58 arestas**, acima do mínimo de 30 vértices/50 arestas exigido pelo enunciado. Também define a capacidade de produção de cada estação, o limite de pedidos por região e o tamanho da frota de entregadores (usados no fluxo máximo do Módulo 7).

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

Utilizado no modo Chef, para recomendar receitas com base em critérios como menor custo, menor tempo e melhores avaliações.

Arquivo: `src/services/recomendacao_service.py`

### 5. Grafo (genérico)

Estrutura nova do T2: lista de adjacência própria, com suporte a grafos direcionados/não-direcionados e ponderados. É a base de todos os Módulos 5, 7 e 8.

Arquivo: `src/estruturas/grafo.py`

### 6. Union-Find (Disjoint Set)

Estrutura de apoio para o algoritmo de Kruskal, com união por rank e compressão de caminho.

Arquivo: `src/estruturas/union_find.py`

### 7. Programação Dinâmica (Mochila 0/1)

Utilizada no Módulo 6 para otimização de menus sob restrição de orçamento ou tempo.

Arquivo: `src/services/otimizacao_service.py`

## Funcionalidades do sistema

### Módulo 1 — Livro de Receitas

Carregamento, armazenamento e listagem das receitas.

### Módulo 2 — Busca Rápida no Cardápio

Busca por nome, ID, categoria ou prefixo.

### Módulo 3 — Organização dos Ingredientes

Consulta de receitas por ingrediente específico.

### Módulo 4 — Recomendação do Chef

Sugestão de receitas com base em restrições e critérios definidos (algoritmo guloso).

### Módulo 5 — Oficina de Produção

Modela dependências entre preparações como um grafo direcionado (DAG). Permite: verificar se existe uma sequência de produção viável; detectar dependências inválidas e ciclos; calcular a sequência de produção de um menu; e listar quais preparos precisam ser concluídos antes de uma receita específica.

Arquivo: `src/services/producao_service.py`

### Módulo 6 — Menu Degustação VIP

Seleciona o subconjunto de receitas que maximiza lucro ou avaliação, respeitando orçamento, tempo, limite de ingredientes raros, capacidade de equipe e, opcionalmente, um estoque de ingredientes disponíveis informado pelo usuário (a receita só entra na otimização se puder ser feita inteiramente com os ingredientes informados), usando **programação dinâmica** (mochila 0/1).

> **Nota de escopo:** dos critérios de otimização citados no enunciado ("lucro esperado, avaliação média, popularidade, diversidade gastronômica"), implementamos **lucro** e **avaliação**. "Popularidade" não tem fonte de dado real na base (a TheMealDB não fornece esse campo, e o T1 também nunca o teve). "Diversidade gastronômica" exigiria uma otimização não-aditiva sobre o conjunto escolhido, incompatível com a formulação de mochila 0/1 sem explodir o espaço de estados então decidi não implementar por ora. Essa é uma decisão consciente de escopo, não uma lacuna despercebida.

Arquivo: `src/services/otimizacao_service.py`

### Módulo 7 — Pesadelo Logístico

Modela a rede de delivery como um grafo geográfico (estações + regiões). Permite: calcular a menor rede de conexões (árvore geradora mínima); consultar rotas e tempo estimado (Dijkstra); encontrar caminhos alternativos; identificar regiões isoladas e pontos críticos (pontes) da rede; e calcular a capacidade máxima de atendimento simultâneo via fluxo máximo, apontando o gargalo operacional (produção, frota ou regiões).

> **Nota de escopo:** dos quatro tipos de capacidade citados no enunciado (produção das estações, número de entregadores, limite por região, quantidade de kits promocionais), os três primeiros estão modelados como camadas da rede de fluxo. O campo `kits_promocionais_disponiveis` é carregado a partir de `rede_entrega.json`, mas não foi conectado a nenhum cálculo ele representaria um recurso paralelo e mais específico (só parte dos pedidos usa kit), o que exigiria uma segunda topologia de fluxo dedicada. Ficou fora do escopo desta entrega por decisão consciente, não por descuido.

Arquivo: `src/services/logistica_service.py`

### Módulo 8 — Laboratório de Inovação (roteirização)

Desafio escolhido: **planejamento de rotas de entrega com múltiplas paradas**. Constrói uma rota inicial com o algoritmo guloso do Vizinho Mais Próximo e refina com a heurística **2-opt**, reaproveitando o grafo e o Dijkstra já implementados no Módulo 7.

Arquivo: `src/services/inovacao_service.py`

### Desafio Extra Opcional — Menu Dia dos Namorados

Seleciona a melhor combinação de entrada + prato principal + sobremesa sob restrições de tempo, custo, dificuldade e, opcionalmente, estoque de ingredientes disponíveis, com justificativa textual gerada automaticamente. Reaproveita a mesma base de receitas e o mesmo `otimizacao_service.py` do Módulo 6.

### Modos de Interação

* **Modo Investigação** — verificação de integridade das receitas (T1: duplicidade, conflitos por nome) **+** detecção de erros de dependência de preparo (Módulo 5) **+** identificação de gargalos, regiões isoladas e pontos críticos da rede de entrega (Módulo 7).
* **Modo Chef** — recomendações gulosas (T1) **+** sequência de produção de um menu (Módulo 5) **+** otimização VIP por programação dinâmica, com restrição opcional de estoque (Módulo 6) **+** Menu Dia dos Namorados (desafio extra).
* **Modo Logística** *(novo no T2)* — árvore geradora mínima, consulta de rotas, caminhos alternativos, capacidade máxima de atendimento e roteirização de entregas (Módulos 7 e 8).
* **Modo Consulta Rápida** — recuperação eficiente de receitas por nome, ID, categoria, prefixo ou ingrediente (T1, inalterado).

## Organização do projeto

```txt
src/
├── data/
│   ├── receitas.json
│   ├── receitas_backup.json
│   ├── baixar_dados.py
│   ├── enriquecer_dados.py
│   ├── dependencias_preparo.json
│   ├── gerar_dependencias_preparo.py
│   ├── rede_entrega.json
│   ├── gerar_rede_entrega.py
│   └── arvore_b.bin
├── estruturas/
│   ├── __init__.py
│   ├── hash_table.py
│   ├── trie.py
│   ├── btree.py
│   ├── grafo.py
│   └── union_find.py
├── models/
│   ├── __init__.py
│   └── receita.py
├── services/
│   ├── __init__.py
│   ├── busca_service.py
│   ├── integridade_service.py
│   ├── recomendacao_service.py
│   ├── receita_service.py
│   ├── producao_service.py
│   ├── otimizacao_service.py
│   ├── logistica_service.py
│   └── inovacao_service.py
├── utils/
│   ├── __init__.py
│   └── hash_util.py
└── main.py
```

## Como executar

### Requisitos

* Python 3.10+ instalado (o projeto usa a sintaxe `str | None` em algumas assinaturas)
* Nenhuma biblioteca externa obrigatória para rodar o sistema principal
* Apenas o `requests` é necessário caso o script `baixar_dados.py` seja executado

### Execução do sistema

Abra o terminal na pasta `src` e execute:

```bash
python main.py
```

Todos os arquivos de dados (`receitas.json`, `dependencias_preparo.json`, `rede_entrega.json`) já estão prontos em `data/` — **não é necessário rodar nenhum script gerador antes de usar o sistema.**

### Regenerar os dados do zero (opcional)

Só é necessário se quiser reconstruir os dados a partir do início:

```bash
cd data
python baixar_dados.py               # baixa as receitas da TheMealDB
python enriquecer_dados.py           # adiciona classe_prato, valor_venda, ingredientes_raros, dificuldade_logistica
python gerar_dependencias_preparo.py # gera o grafo de dependências de preparo (Módulo 5)
python gerar_rede_entrega.py         # gera a rede de entrega (Módulo 7)
```

## Menu do sistema

```
--- Consulta Rápida ---
1 - Listar todas as receitas
2 - Buscar receita por ID
3 - Buscar receita por nome/prefixo
4 - Buscar receitas por categoria
5 - Buscar por ingrediente

--- Modos de Interação ---
6 - Modo Investigação
7 - Modo Chef
8 - Modo Logística

--- Outros ---
9 - Recuperação P1: Árvore B em binário
0 - Sair
```

Cada Modo de Interação abre um submenu com opções 1..N e `0` para voltar:

```
--- Modo Investigação ---
1 - Receitas repetidas e conflitos por nome
2 - Existe erro de dependência de preparo?
3 - Quais preparos faltam para uma receita?
4 - Existe gargalo operacional na rede de entrega?
5 - Quais são as Regiões isoladas e pontos críticos da rede de entrega?

--- Modo Chef ---
1 - Menu econômico (algoritmo guloso)
2 - Menu rápido (algoritmo guloso)
3 - Melhores avaliadas (algoritmo guloso)
4 - Sequência de produção do menu do dia
5 - Menu Degustação VIP (programação dinâmica)
6 - Menu Especial Dia dos Namorados

--- Modo Logística ---
1 - Listar pontos da rede de entrega
2 - Menor rede de conexões (árvore geradora mínima)
3 - Consultar rota entre dois pontos
4 - Consultar caminho alternativo
5 - Capacidade máxima de atendimento
6 - Roteirizar entrega com múltiplas paradas

--- Recuperação P1: Árvore B em Binário ---
1 - Salvar Árvore B em binário
2 - Carregar Árvore B do binário
3 - Diagnóstico da Árvore B
4 - Buscar na Árvore B carregada
```

As subopções 3 e 4 do Modo Investigação/Modo Chef que pedem ID de receita, e as subopções do Modo Logística que pedem ID de ponto, imprimem primeiro a lista de IDs válidos, para o usuário não precisar adivinhar. As subopções 5 e 6 do Modo Chef também perguntam, de forma opcional (Enter para pular), um estoque de ingredientes disponíveis para restringir a busca. As antigas opções 8/9/10/11 do T1 (salvar/carregar/diagnóstico/buscar na Árvore B binária) agora são as subopções 1/2/3/4 da opção **9**, sem nenhuma mudança de comportamento.

## Justificativa das escolhas

### Tabela Hash

Foi escolhida porque permite acesso rápido por identificador único, o que atende bem à busca por ID.

### Árvore Trie

Foi escolhida por ser eficiente para buscas por prefixo e por nome parcial.

### Árvore B

Foi usada para organizar receitas por um atributo numérico, possibilitando consultas ordenadas. Na recuperação da P1, foi expandida com persistência em arquivo binário, simulando páginas de memória secundária.

### Algoritmo guloso

Foi utilizado no módulo de recomendação (T1) e no Módulo 8 (Nearest Neighbor), pois em ambos os casos o objetivo é construir uma solução iterativamente a partir de um critério de prioridade local.

### Hash de integridade

Foi adotado um hash SHA-256 baseado no conteúdo da receita para detectar alterações indevidas, receitas duplicadas e conflitos entre versões.

### Grafo genérico

Optamos por uma estrutura de grafo única e genérica (lista de adjacência, direcionada/não-direcionada, ponderada) em vez de estruturas específicas para cada módulo, porque os Módulos 5, 7 e 8 compartilham as mesmas operações fundamentais (inserir vértice/aresta, vizinhos, busca em largura/profundidade, componentes conexos). Isso evitou duplicação de código e permitiu testar a estrutura isoladamente antes de implementar os algoritmos que dependem dela.

### Módulo 5 — Ordenação topológica (Kahn)

A ordenação topológica pelo algoritmo de Kahn foi escolhida porque resolve, com o mesmo algoritmo, as três consultas exigidas: a sequência de produção é a própria ordem topológica; a viabilidade da sequência é equivalente à ausência de vértices presos com grau de entrada residual maior que zero (detecção de ciclo "de graça"); e os preparos necessários para uma receita são os predecessores dela no grafo, obtidos por busca reversa.

### Módulo 6 — Programação Dinâmica (Mochila 0/1)

A mochila 0/1 clássica foi aplicada sobre o recurso principal escolhido pelo usuário (orçamento **ou** tempo), garantindo solução **ótima** para essa restrição — diferente do guloso do T1, que não garante otimalidade. As demais restrições (o outro recurso, ingredientes raros, capacidade de equipe) são tratadas como filtros de viabilidade aplicados sobre o resultado ótimo, com poda gulosa caso alguma seja violada. Uma DP multidimensional sobre todas as restrições simultaneamente foi descartada por explosão combinatória de estados (curse of dimensionality) — a solução adotada equilibra corretude formal (comprovada contra força bruta) com viabilidade computacional.

### Módulo 7 — MST, Dijkstra e Fluxo Máximo

* **Kruskal + Union-Find** para a árvore geradora mínima, por ser direto de implementar e de explicar a partir de uma lista de arestas ordenada.
* **Dijkstra** para caminho mínimo, por não haver pesos negativos no domínio (tempo de deslocamento).
* **Fluxo máximo (Edmonds-Karp)** para capacidade de atendimento, usando um nó único de frota compartilhada (técnica de *vertex splitting*) para modelar o número de entregadores como um recurso agregado, exatamente como o enunciado separa "capacidade de produção", "número de entregadores" e "limite por região" como três restrições distintas.

### Módulo 8 — TSP heurístico (Nearest Neighbor + 2-opt)

TSP é NP-difícil; para o tamanho de rota esperado (poucas dezenas de paradas por viagem) uma heurística construtiva (Nearest Neighbor) seguida de melhoria local (2-opt) encontra soluções de boa qualidade em tempo polinomial. Validamos empiricamente contra força bruta em instâncias pequenas e o resultado bateu exato com o ótimo.

## Bibliotecas utilizadas

O enunciado permite bibliotecas de apoio desde que não substituam as estruturas centrais exigidas, com justificativa. Além do `json`, `pathlib` e `dataclasses` (manipulação de arquivo e organização de código, já usados no T1), o T2 usa apenas duas bibliotecas padrão do Python:

* **`heapq`** — fila de prioridade binária usada no Dijkstra (`logistica_service.py`), para sempre expandir o vértice de menor distância acumulada em O(log V) por operação. Não é uma estrutura de dados central do trabalho (que são Tabela Hash, Trie, Árvore B e Grafo, todas implementadas do zero); é uma peça de apoio padrão para a implementação eficiente do Dijkstra, do mesmo jeito que `json` apoia a leitura de arquivos.
* **`collections.deque`** — fila FIFO com O(1) de inserção/remoção nas duas pontas, usada nas buscas em largura (BFS) da estrutura `Grafo` e no Edmonds-Karp (`logistica_service.py`). Uma lista comum do Python teria O(n) para remover do início; o `deque` evita essa degradação de desempenho sem exigir implementar uma fila do zero, que não é o foco do trabalho.

Nenhuma biblioteca de grafos, otimização ou algoritmos prontos (ex: `networkx`, `scipy.optimize`) foi usada — todos os algoritmos (Grafo, Union-Find, Kahn, Dijkstra, Kruskal, Edmonds-Karp, mochila 0/1, Nearest Neighbor, 2-opt) foram implementados pelo grupo.

## Análise de complexidade

| Algoritmo | Complexidade | Onde é usado |
|---|---|---|
| Tabela Hash (inserir/buscar) | O(1) médio | Busca por ID |
| Árvore Trie (busca por prefixo) | O(k + r), k=tamanho do termo, r=resultados | Busca por nome/prefixo |
| Árvore B (busca/inserção) | O(log n) | Busca por tempo de preparo |
| Guloso (recomendação) | O(n log n) | Menu econômico/rápido/avaliação |
| Kahn (ordenação topológica) | O(V + E) | Sequência de produção, detecção de ciclo |
| Busca de ancestrais (DFS) | O(V + E) | Preparos necessários para uma receita |
| Mochila 0/1 (DP) | O(n × capacidade) | Menu VIP |
| Menu Dia dos Namorados | O(1) por categoria quando não há restrição cruzada; O(E×P×S) com restrição de tempo/custo | Desafio extra |
| Kruskal (MST) | O(E log E) | Menor rede de conexões |
| Union-Find (find/union) | O(α(n)) amortizado | Suporte ao Kruskal |
| Dijkstra (heap binário) | O((V+E) log V) | Rotas e tempo estimado |
| Detecção de pontos críticos | O(E × (V+E)) | Pontes da rede de entrega |
| Edmonds-Karp (fluxo máximo) | O(V·E²) | Capacidade máxima de atendimento |
| Nearest Neighbor (TSP) | O(V²) | Rota inicial de entrega |
| 2-opt (TSP) | O(V²) por iteração até convergir | Refinamento da rota |

## Dimensões das redes utilizadas

| Rede | Vértices | Arestas |
|---|---|---|
| Dependências de preparo (Módulo 5) | 46 (21 preparos + 25 receitas) | 52 válidas (+ 1 referência quebrada proposital) |
| Rede de entrega (Módulo 7) | 30 (4 estações + 26 regiões) | 58 |

Ambas acima do mínimo de 30 vértices / 50 arestas exigido no enunciado do T2.

## Observações

* O projeto foi desenvolvido em Python (3.10+).
* O sistema foi pensado para execução local, sem depender de API durante a apresentação.
* Os arquivos `receitas.json`, `dependencias_preparo.json` e `rede_entrega.json` devem permanecer na pasta `data` para o funcionamento correto.
* Todos os algoritmos novos do T2 (ordenação topológica, mochila 0/1, Kruskal, Dijkstra, Edmonds-Karp, Nearest Neighbor + 2-opt) foram validados durante o desenvolvimento contra implementações independentes ou força bruta (quando o tamanho da instância permitia), não apenas testados manualmente.
* O `baixar_dados.py` (T1) não usa seed fixa para os campos aleatórios (`tempo`, `custo`, `avaliacao`); se ele for executado novamente, esses valores mudam e todo o restante da base derivada (`valor_venda`, `dificuldade_logistica`, etc., via `enriquecer_dados.py`) muda em cascata. Isso é um comportamento herdado do T1 e não afeta a entrega, desde que os arquivos em `data/` não sejam regenerados sem necessidade.
* Duas decisões de escopo foram tomadas conscientemente e estão documentadas nos módulos correspondentes: os critérios "popularidade" e "diversidade gastronômica" do Módulo 6 não foram implementados (sem fonte de dado real / fora do escopo de uma mochila 0/1), e o campo `kits_promocionais_disponiveis` do Módulo 7 é carregado mas não entra no cálculo de fluxo máximo atual.

## Recuperação P1

### Opção escolhida

Eu escolhi a **Opção C — Árvores B e Simulação de Memória Secundária (I/O)**.

### Dificuldade principal na prova

A maior dificuldade encontrada foi montar corretamente a **Árvore B** após as inserções, principalmente entender as divisões de nós e desenhar a estrutura final depois de todas as inserções. Também houve dificuldade na questão de remoção de elementos e reorganização da árvore.

### O que foi adicionado no T1

Para a recuperação, a Árvore B deixou de viver apenas na memória RAM e passou a ter persistência em arquivo binário. O sistema agora salva a estrutura em `data/arvore_b.bin` e consegue carregá-la depois, simulando páginas/blocos de disco. Também foi adicionada uma rotina de diagnóstico para verificar o estado da árvore e uma busca de teste realizada diretamente na árvore carregada do binário.

### Como testar a funcionalidade

> **Nota:** no T2 o menu foi reorganizado (veja [Menu do sistema](#menu-do-sistema)). As opções abaixo foram atualizadas para o caminho atual; o comportamento é idêntico ao da entrega original do T1.

1. Executar o sistema com `python main.py`.
2. No menu, escolher a opção **9** (Recuperação P1) e depois a subopção **1** para salvar a Árvore B em binário.
3. Fechar o programa.
4. Abrir o sistema novamente com `python main.py`.
5. Escolher **9** e depois **2** para carregar a Árvore B do arquivo binário.
6. Escolher **9** e depois **3** para visualizar o diagnóstico da Árvore B.
7. Escolher **9** e depois **4** para simular a RAM limpa, recarregar a Árvore B do binário e fazer a busca.
8. Digitar um valor de tempo de preparo existente, por exemplo 43.

## Trabalho 2

### Módulos implementados

Os quatro módulos obrigatórios (5, 6, 7 e 8) foram implementados, mais o desafio extra opcional (Menu Dia dos Namorados). Ver [Funcionalidades do sistema](#funcionalidades-do-sistema) para detalhes de cada um.

### Desafio escolhido para o Módulo 8

Optamos por **planejamento de rotas de entrega com múltiplas paradas** (TSP heurístico), por reaproveitar diretamente o grafo e o Dijkstra já implementados no Módulo 7, sem precisar de uma modelagem paralela nova, e por ser uma técnica de otimização combinatória genuinamente distinta de tudo que havia sido usado antes no projeto (DP, guloso, MST, fluxo máximo).

### Dificuldades encontradas

* Modelar o número de entregadores como uma restrição de fluxo máximo exigiu a técnica de *vertex splitting* (um nó único de frota compartilhada), já que ele não é uma aresta natural entre estação e região, e sim um recurso agregado do sistema todo.
* Garantir que a programação dinâmica do Módulo 6 permanecesse ótima ao mesmo tempo em que respeitava restrições secundárias (ingredientes raros, capacidade de equipe) exigiu decidir explicitamente quais restrições entram na DP e quais são tratadas como poda posterior, para evitar explosão de estados.
* No TSP do Módulo 8, o cálculo de distância entre dois pontos quaisquer da rede depende do caminho mínimo entre eles (nem todo par de pontos tem conexão direta), então foi necessário calcular o fecho métrico (todas as distâncias via Dijkstra) antes de aplicar o Nearest Neighbor e o 2-opt.

### Limitações e possíveis melhorias (Módulo 8)

* **2-opt é uma heurística local**: para instâncias maiores que as testadas (dezenas de pontos), pode ficar preso em um ótimo local. Uma melhoria natural seria adicionar *Or-opt* (mover um único ponto de posição, não só inverter segmentos) ou reinícios com pontos de partida diferentes.
* **A rota não considera janelas de tempo**: hoje o sistema busca o menor tempo total, mas não modela horários de entrega específicos por cliente (ex: "entregar entre 12h e 13h"). Um TSP com janelas de tempo (TSP-TW) seria uma extensão natural.
* **Recalcula a matriz de distâncias a cada chamada**: para uso repetido com os mesmos pontos, cachear os resultados de Dijkstra evitaria recomputação — irrelevante na escala atual (30 vértices), mas relevante se a rede crescer.
* **Não há replanejamento dinâmico**: se uma rota já em andamento precisasse ser recalculada (ponto bloqueado, novo pedido urgente), o sistema recalcularia do zero, sem reaproveitar decisões já tomadas.

### Como testar cada módulo

**Módulo 5 (Oficina de Produção):** opção 6 (Modo Investigação), subopções 2 e 3; ou opção 7 (Modo Chef), subopção 4.

**Módulo 6 (Menu VIP):** opção 7 (Modo Chef), subopção 5. Exemplo: critério lucro, recurso orçamento, limite 500. Para testar o filtro de estoque, informe uma lista curta de ingredientes (ex: `Salt, Sugar, Butter, Flour, Eggs`) quando perguntado — o menu retornará só receitas que usam exclusivamente esses ingredientes.

**Módulo 7 (Logística):** opção 8 (Modo Logística), todas as subopções. Para ver o gargalo operacional (frota), use a subopção 5 sem alterar o número de entregadores; para ver a produção virar o gargalo, simule com 70 entregadores ou mais.

**Módulo 8 (Roteirização):** opção 8 (Modo Logística), subopção 6. Informe um ponto de partida (ex: `estacao_cozinha_centro`) e uma lista de regiões separadas por vírgula.

**Desafio extra (Menu Dia dos Namorados):** opção 7 (Modo Chef), subopção 6.

## Repositório

Link do repositório: [Desafio na Cozinha - AED II](https://github.com/iagobraatz/Desafio-na-cozinha-AED-2---iago)

## Integrantes

* Iago Kainan Bubolz Braatz

## Data de entrega

20 de julho de 2026