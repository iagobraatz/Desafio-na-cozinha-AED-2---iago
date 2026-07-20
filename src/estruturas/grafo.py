from typing import Any, Dict, List, Optional, Tuple
from collections import deque


class Grafo:
    def __init__(self, direcionado: bool = False):
        self.direcionado = direcionado
        self.vertices: Dict[Any, Dict[Any, float]] = {}

    def adicionar_vertice(self, vertice: Any) -> None:
        if vertice not in self.vertices:
            self.vertices[vertice] = {}

    def remover_vertice(self, vertice: Any) -> None:
        if vertice not in self.vertices:
            return

        del self.vertices[vertice]

        for adjacencias in self.vertices.values():
            adjacencias.pop(vertice, None)

    def existe_vertice(self, vertice: Any) -> bool:
        return vertice in self.vertices

    def adicionar_aresta(self, origem: Any, destino: Any, peso: float = 1.0) -> None:
        self.adicionar_vertice(origem)
        self.adicionar_vertice(destino)

        self.vertices[origem][destino] = peso

        if not self.direcionado:
            self.vertices[destino][origem] = peso

    def remover_aresta(self, origem: Any, destino: Any) -> None:
        if origem in self.vertices:
            self.vertices[origem].pop(destino, None)

        if not self.direcionado and destino in self.vertices:
            self.vertices[destino].pop(origem, None)

    def existe_aresta(self, origem: Any, destino: Any) -> bool:
        return origem in self.vertices and destino in self.vertices[origem]

    def obter_peso(self, origem: Any, destino: Any) -> Optional[float]:
        if not self.existe_aresta(origem, destino):
            return None
        return self.vertices[origem][destino]

    def obter_vizinhos(self, vertice: Any) -> List[Any]:
        return list(self.vertices.get(vertice, {}).keys())

    def obter_adjacencias(self, vertice: Any) -> List[Tuple[Any, float]]:
        return list(self.vertices.get(vertice, {}).items())

    def obter_predecessores(self, vertice: Any) -> List[Any]:
        predecessores = []

        for origem, adjacencias in self.vertices.items():
            if vertice in adjacencias:
                predecessores.append(origem)

        return predecessores

    def listar_vertices(self) -> List[Any]:
        return list(self.vertices.keys())

    def listar_arestas(self) -> List[Tuple[Any, Any, float]]:
        arestas = []
        visitadas = set()

        for origem, adjacencias in self.vertices.items():
            for destino, peso in adjacencias.items():
                if self.direcionado:
                    arestas.append((origem, destino, peso))
                else:
                    chave = frozenset((origem, destino))
                    if chave not in visitadas:
                        visitadas.add(chave)
                        arestas.append((origem, destino, peso))

        return arestas

    def grau_saida(self, vertice: Any) -> int:
        return len(self.vertices.get(vertice, {}))

    def grau_entrada(self, vertice: Any) -> int:
        if not self.direcionado:
            return self.grau_saida(vertice)

        grau = 0
        for adjacencias in self.vertices.values():
            if vertice in adjacencias:
                grau += 1

        return grau

    def grau(self, vertice: Any) -> int:
        if self.direcionado:
            return self.grau_entrada(vertice) + self.grau_saida(vertice)
        return self.grau_saida(vertice)

    def quantidade_vertices(self) -> int:
        return len(self.vertices)

    def quantidade_arestas(self) -> int:
        return len(self.listar_arestas())

    def busca_em_largura(self, origem: Any) -> List[Any]:
        if origem not in self.vertices:
            return []

        visitados = {origem}
        ordem = [origem]
        fila = deque([origem])

        while fila:
            atual = fila.popleft()
            for vizinho in self.obter_vizinhos(atual):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    ordem.append(vizinho)
                    fila.append(vizinho)

        return ordem

    def busca_em_profundidade(self, origem: Any) -> List[Any]:
        if origem not in self.vertices:
            return []

        visitados = set()
        ordem = []
        pilha = [origem]

        while pilha:
            atual = pilha.pop()
            if atual in visitados:
                continue

            visitados.add(atual)
            ordem.append(atual)

            for vizinho in reversed(self.obter_vizinhos(atual)):
                if vizinho not in visitados:
                    pilha.append(vizinho)

        return ordem

    def existe_caminho(self, origem: Any, destino: Any) -> bool:
        if origem not in self.vertices or destino not in self.vertices:
            return False

        if origem == destino:
            return True

        return destino in self.busca_em_largura(origem)

    def componentes_conexos(self) -> List[List[Any]]:
        visitados = set()
        componentes = []

        for vertice in self.vertices:
            if vertice not in visitados:
                componente = self.busca_em_largura(vertice)
                visitados.update(componente)
                componentes.append(componente)

        return componentes

    def esta_conectado(self) -> bool:
        if not self.vertices:
            return True
        return len(self.componentes_conexos()) == 1

    def copiar(self) -> "Grafo":
        novo_grafo = Grafo(direcionado=self.direcionado)

        for vertice, adjacencias in self.vertices.items():
            novo_grafo.adicionar_vertice(vertice)
            for destino, peso in adjacencias.items():
                novo_grafo.vertices[vertice][destino] = peso

        return novo_grafo