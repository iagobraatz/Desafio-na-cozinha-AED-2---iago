import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

from estruturas.grafo import Grafo


class ProducaoService:
    def __init__(self, caminho_arquivo: str | Path) -> None:
        self.caminho_arquivo = Path(caminho_arquivo)
        self.grafo = Grafo(direcionado=True)
        self.nomes: Dict[str, str] = {}
        self.tempos_preparo: Dict[str, int] = {}
        self.ids_preparos: Set[str] = set()
        self.ids_receitas: Set[str] = set()
        self.referencias_invalidas: List[Tuple[str, str]] = []

        self._carregar_dados()

    def _carregar_dados(self) -> None:
        if not self.caminho_arquivo.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho_arquivo}")

        with self.caminho_arquivo.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        preparos = dados.get("preparos", [])
        receitas_dependentes = dados.get("receitas_dependentes", [])

        for preparo in preparos:
            self.grafo.adicionar_vertice(preparo["id"])
            self.nomes[preparo["id"]] = preparo["nome"]
            self.tempos_preparo[preparo["id"]] = preparo.get("tempo_preparo", 0)
            self.ids_preparos.add(preparo["id"])

        for receita in receitas_dependentes:
            self.grafo.adicionar_vertice(receita["id_receita"])
            self.nomes[receita["id_receita"]] = receita["nome_receita"]
            self.ids_receitas.add(receita["id_receita"])

        for preparo in preparos:
            for dependencia in preparo["depende_de"]:
                if dependencia in self.ids_preparos:
                    self.grafo.adicionar_aresta(dependencia, preparo["id"])
                else:
                    self.referencias_invalidas.append((preparo["id"], dependencia))

        for receita in receitas_dependentes:
            for dependencia in receita["depende_de"]:
                if dependencia in self.ids_preparos:
                    self.grafo.adicionar_aresta(dependencia, receita["id_receita"])
                else:
                    self.referencias_invalidas.append((receita["id_receita"], dependencia))

    def obter_nome(self, vertice_id: str) -> str:
        return self.nomes.get(vertice_id, vertice_id)

    def ordenacao_topologica(self) -> Tuple[List[str], List[str]]:
        grau_entrada = {vertice: self.grafo.grau_entrada(vertice) for vertice in self.grafo.listar_vertices()}
        fila = [vertice for vertice, grau in grau_entrada.items() if grau == 0]
        ordem: List[str] = []

        while fila:
            fila.sort(key=self.obter_nome)
            atual = fila.pop(0)
            ordem.append(atual)

            for vizinho in self.grafo.obter_vizinhos(atual):
                grau_entrada[vizinho] -= 1
                if grau_entrada[vizinho] == 0:
                    fila.append(vizinho)

        presos = [vertice for vertice, grau in grau_entrada.items() if grau > 0]
        return ordem, presos

    def existe_sequencia_viavel(self) -> bool:
        _, presos = self.ordenacao_topologica()
        return len(presos) == 0 and len(self.referencias_invalidas) == 0

    def identificar_inconsistencias(self) -> dict:
        _, presos = self.ordenacao_topologica()

        return {
            "referencias_invalidas": [
                {"origem": origem, "dependencia_inexistente": dependencia}
                for origem, dependencia in self.referencias_invalidas
            ],
            "referencias_invalidas_nomes": [
                {"origem": self.obter_nome(origem), "dependencia_inexistente": dependencia}
                for origem, dependencia in self.referencias_invalidas
            ],
            "vertices_em_ciclo": presos,
            "vertices_em_ciclo_nomes": [self.obter_nome(vertice) for vertice in presos],
        }

    def _coletar_ancestrais(self, vertice: str) -> Set[str]:
        visitados: Set[str] = set()
        pilha = list(self.grafo.obter_predecessores(vertice))

        while pilha:
            atual = pilha.pop()
            if atual in visitados:
                continue
            visitados.add(atual)
            pilha.extend(self.grafo.obter_predecessores(atual))

        return visitados

    def preparos_necessarios_para(self, id_receita: str) -> dict:
        if not self.grafo.existe_vertice(id_receita):
            raise ValueError(f"Receita não cadastrada nas dependências de preparo: {id_receita}")

        ancestrais = self._coletar_ancestrais(id_receita)
        ordem_completa, _ = self.ordenacao_topologica()
        ordem_ancestrais = [vertice for vertice in ordem_completa if vertice in ancestrais]

        return {
            "id_receita": id_receita,
            "nome_receita": self.obter_nome(id_receita),
            "preparos_necessarios": ordem_ancestrais,
            "preparos_necessarios_nomes": [self.obter_nome(vertice) for vertice in ordem_ancestrais],
            "tempo_total_estimado_min": sum(self.tempos_preparo.get(v, 0) for v in ordem_ancestrais),
        }

    def sequencia_producao_menu(self, ids_receitas_menu: List[str]) -> dict:
        for id_receita in ids_receitas_menu:
            if id_receita not in self.ids_receitas:
                raise ValueError(f"Receita não cadastrada nas dependências de preparo: {id_receita}")

        necessarios: Set[str] = set(ids_receitas_menu)
        for id_receita in ids_receitas_menu:
            necessarios.update(self._coletar_ancestrais(id_receita))

        ordem_completa, presos = self.ordenacao_topologica()
        sequencia = [vertice for vertice in ordem_completa if vertice in necessarios]
        bloqueados = [vertice for vertice in presos if vertice in necessarios]

        return {
            "sequencia": sequencia,
            "sequencia_nomes": [self.obter_nome(vertice) for vertice in sequencia],
            "bloqueados": bloqueados,
            "bloqueados_nomes": [self.obter_nome(vertice) for vertice in bloqueados],
            "tempo_total_estimado_min": sum(self.tempos_preparo.get(v, 0) for v in sequencia),
            "viavel": len(bloqueados) == 0,
        }

    def diagnostico(self) -> dict:
        return {
            "quantidade_preparos": len(self.ids_preparos),
            "quantidade_receitas": len(self.ids_receitas),
            "quantidade_vertices": self.grafo.quantidade_vertices(),
            "quantidade_arestas": self.grafo.quantidade_arestas(),
            "quantidade_referencias_invalidas": len(self.referencias_invalidas),
            "sequencia_viavel_para_tudo": self.existe_sequencia_viavel(),
        }