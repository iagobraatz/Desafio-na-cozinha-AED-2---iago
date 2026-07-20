import heapq
import json
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from estruturas.grafo import Grafo
from estruturas.union_find import UniaoConjuntos


class LogisticaService:
    def __init__(self, caminho_arquivo: str | Path) -> None:
        self.caminho_arquivo = Path(caminho_arquivo)
        self.grafo_geografico = Grafo(direcionado=False)
        self.nomes: Dict[str, str] = {}
        self.estacoes: List[dict] = []
        self.regioes: List[dict] = []
        self.frota: dict = {}
        self.kits_promocionais_disponiveis: int = 0

        self._carregar_dados()

    def _carregar_dados(self) -> None:
        if not self.caminho_arquivo.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho_arquivo}")

        with self.caminho_arquivo.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        self.estacoes = dados.get("estacoes", [])
        self.regioes = dados.get("regioes", [])
        self.frota = dados.get("frota", {"quantidade_entregadores": 0, "entregas_por_entregador_hora": 0})
        self.kits_promocionais_disponiveis = dados.get("kits_promocionais_disponiveis", 0)

        for estacao in self.estacoes:
            self.grafo_geografico.adicionar_vertice(estacao["id"])
            self.nomes[estacao["id"]] = estacao["nome"]

        for regiao in self.regioes:
            self.grafo_geografico.adicionar_vertice(regiao["id"])
            self.nomes[regiao["id"]] = regiao["nome"]

        for conexao in dados.get("conexoes", []):
            self.grafo_geografico.adicionar_aresta(
                conexao["origem"], conexao["destino"], conexao["tempo_estimado_min"]
            )

        self.nomes["FONTE"] = "Fonte (produção agregada)"
        self.nomes["FROTA_ENTRADA"] = "Frota - entrada"
        self.nomes["FROTA_SAIDA"] = "Frota - saída"
        self.nomes["SORVEDOURO"] = "Sorvedouro (demanda agregada)"

    def obter_nome(self, vertice_id: str) -> str:
        return self.nomes.get(vertice_id, vertice_id)

    def arvore_geradora_minima(self) -> dict:
        arestas_ordenadas = sorted(self.grafo_geografico.listar_arestas(), key=lambda aresta: aresta[2])
        uniao = UniaoConjuntos()
        for vertice in self.grafo_geografico.listar_vertices():
            uniao.criar_conjunto(vertice)

        arestas_mst: List[Tuple[str, str, float]] = []
        peso_total = 0.0

        for origem, destino, peso in arestas_ordenadas:
            if uniao.unir(origem, destino):
                arestas_mst.append((origem, destino, peso))
                peso_total += peso

        quantidade_vertices = self.grafo_geografico.quantidade_vertices()

        return {
            "arestas": arestas_mst,
            "arestas_nomes": [
                (self.obter_nome(origem), self.obter_nome(destino), peso) for origem, destino, peso in arestas_mst
            ],
            "peso_total_min": peso_total,
            "quantidade_arestas_originais": len(arestas_ordenadas),
            "quantidade_arestas_mst": len(arestas_mst),
            "conecta_todos_os_pontos": len(arestas_mst) == quantidade_vertices - 1,
        }

    def menor_caminho(
        self, origem: str, destino: str, arestas_excluidas: Optional[Set[frozenset]] = None
    ) -> dict:
        if not self.grafo_geografico.existe_vertice(origem) or not self.grafo_geografico.existe_vertice(destino):
            raise ValueError("Vértice de origem ou destino não existe na rede.")

        arestas_excluidas = arestas_excluidas or set()

        distancias: Dict[str, float] = {origem: 0}
        predecessores: Dict[str, str] = {}
        visitados: Set[str] = set()
        fila: List[Tuple[float, str]] = [(0, origem)]

        while fila:
            distancia_atual, atual = heapq.heappop(fila)

            if atual in visitados:
                continue
            visitados.add(atual)

            if atual == destino:
                break

            for vizinho, peso in self.grafo_geografico.obter_adjacencias(atual):
                if frozenset((atual, vizinho)) in arestas_excluidas:
                    continue

                nova_distancia = distancia_atual + peso
                if vizinho not in distancias or nova_distancia < distancias[vizinho]:
                    distancias[vizinho] = nova_distancia
                    predecessores[vizinho] = atual
                    heapq.heappush(fila, (nova_distancia, vizinho))

        if destino not in distancias:
            return {"encontrado": False, "origem": origem, "destino": destino}

        caminho = self._reconstruir_caminho(predecessores, origem, destino)

        return {
            "encontrado": True,
            "origem": origem,
            "destino": destino,
            "caminho": caminho,
            "caminho_nomes": [self.obter_nome(vertice) for vertice in caminho],
            "tempo_total_min": distancias[destino],
        }

    def _reconstruir_caminho(self, predecessores: Dict[str, str], origem: str, destino: str) -> List[str]:
        caminho = [destino]
        atual = destino
        while atual != origem:
            atual = predecessores[atual]
            caminho.append(atual)
        caminho.reverse()
        return caminho

    def caminho_alternativo(self, origem: str, destino: str) -> dict:
        principal = self.menor_caminho(origem, destino)
        if not principal["encontrado"]:
            return {"caminho_principal": principal, "caminho_alternativo": {"encontrado": False}}

        arestas_do_principal = {
            frozenset((principal["caminho"][i], principal["caminho"][i + 1]))
            for i in range(len(principal["caminho"]) - 1)
        }

        alternativo = self.menor_caminho(origem, destino, arestas_excluidas=arestas_do_principal)

        return {"caminho_principal": principal, "caminho_alternativo": alternativo}

    def identificar_pontos_criticos(self) -> List[dict]:
        pontos_criticos = []

        for origem, destino, peso in self.grafo_geografico.listar_arestas():
            copia = self.grafo_geografico.copiar()
            copia.remover_aresta(origem, destino)

            if copia.esta_conectado():
                continue

            componentes = copia.componentes_conexos()
            menor_componente = min(componentes, key=len)

            pontos_criticos.append({
                "origem": origem,
                "destino": destino,
                "origem_nome": self.obter_nome(origem),
                "destino_nome": self.obter_nome(destino),
                "tempo_min": peso,
                "vertices_isolados": menor_componente,
                "vertices_isolados_nomes": [self.obter_nome(v) for v in menor_componente],
            })

        return pontos_criticos

    def _construir_rede_fluxo(
        self, quantidade_entregadores: Optional[int] = None, entregas_por_entregador_hora: Optional[int] = None
    ) -> Grafo:
        rede = Grafo(direcionado=True)
        rede.adicionar_vertice("FONTE")
        rede.adicionar_vertice("FROTA_ENTRADA")
        rede.adicionar_vertice("FROTA_SAIDA")
        rede.adicionar_vertice("SORVEDOURO")

        entregadores = quantidade_entregadores if quantidade_entregadores is not None else self.frota["quantidade_entregadores"]
        entregas_hora = entregas_por_entregador_hora if entregas_por_entregador_hora is not None else self.frota["entregas_por_entregador_hora"]
        capacidade_frota = entregadores * entregas_hora

        rede.adicionar_aresta("FROTA_ENTRADA", "FROTA_SAIDA", capacidade_frota)

        for estacao in self.estacoes:
            rede.adicionar_vertice(estacao["id"])
            rede.adicionar_aresta("FONTE", estacao["id"], estacao["capacidade_producao_hora"])
            rede.adicionar_aresta(estacao["id"], "FROTA_ENTRADA", estacao["capacidade_producao_hora"])

        for regiao in self.regioes:
            rede.adicionar_vertice(regiao["id"])
            rede.adicionar_aresta("FROTA_SAIDA", regiao["id"], regiao["limite_pedidos_hora"])
            rede.adicionar_aresta(regiao["id"], "SORVEDOURO", regiao["limite_pedidos_hora"])

        return rede

    def _bfs_caminho_aumentante(self, residual: Grafo, fonte: str, sorvedouro: str) -> Optional[List[Tuple[str, str]]]:
        visitados = {fonte}
        fila = deque([fonte])
        predecessor: Dict[str, str] = {}

        while fila:
            atual = fila.popleft()

            if atual == sorvedouro:
                break

            for vizinho, capacidade in residual.obter_adjacencias(atual):
                if vizinho not in visitados and capacidade > 0:
                    visitados.add(vizinho)
                    predecessor[vizinho] = atual
                    fila.append(vizinho)

        if sorvedouro not in visitados:
            return None

        caminho = []
        atual = sorvedouro
        while atual != fonte:
            anterior = predecessor[atual]
            caminho.append((anterior, atual))
            atual = anterior
        caminho.reverse()
        return caminho

    def _alcancaveis_no_residual(self, residual: Grafo, fonte: str) -> Set[str]:
        visitados = {fonte}
        fila = deque([fonte])

        while fila:
            atual = fila.popleft()
            for vizinho, capacidade in residual.obter_adjacencias(atual):
                if vizinho not in visitados and capacidade > 0:
                    visitados.add(vizinho)
                    fila.append(vizinho)

        return visitados

    def calcular_fluxo_maximo(
        self, quantidade_entregadores: Optional[int] = None, entregas_por_entregador_hora: Optional[int] = None
    ) -> dict:
        rede_original = self._construir_rede_fluxo(quantidade_entregadores, entregas_por_entregador_hora)
        residual = rede_original.copiar()

        for origem, destino, _ in rede_original.listar_arestas():
            if not residual.existe_aresta(destino, origem):
                residual.adicionar_aresta(destino, origem, 0)

        fluxo_total = 0

        while True:
            caminho = self._bfs_caminho_aumentante(residual, "FONTE", "SORVEDOURO")
            if caminho is None:
                break

            gargalo = min(residual.obter_peso(u, v) for u, v in caminho)

            for u, v in caminho:
                residual.adicionar_aresta(u, v, residual.obter_peso(u, v) - gargalo)
                residual.adicionar_aresta(v, u, residual.obter_peso(v, u) + gargalo)

            fluxo_total += gargalo

        alcancaveis = self._alcancaveis_no_residual(residual, "FONTE")
        arestas_corte = []

        for origem, destino, capacidade in rede_original.listar_arestas():
            if origem in alcancaveis and destino not in alcancaveis:
                arestas_corte.append({
                    "origem": origem,
                    "destino": destino,
                    "origem_nome": self.obter_nome(origem),
                    "destino_nome": self.obter_nome(destino),
                    "capacidade": capacidade,
                })

        capacidade_producao_total = sum(e["capacidade_producao_hora"] for e in self.estacoes)
        capacidade_frota_total = (
            (quantidade_entregadores if quantidade_entregadores is not None else self.frota["quantidade_entregadores"])
            * (entregas_por_entregador_hora if entregas_por_entregador_hora is not None else self.frota["entregas_por_entregador_hora"])
        )
        capacidade_regioes_total = sum(r["limite_pedidos_hora"] for r in self.regioes)

        return {
            "fluxo_maximo_pedidos_hora": fluxo_total,
            "arestas_gargalo": arestas_corte,
            "capacidade_producao_total": capacidade_producao_total,
            "capacidade_frota_total": capacidade_frota_total,
            "capacidade_regioes_total": capacidade_regioes_total,
            "recurso_gargalo": self._identificar_camada_gargalo(arestas_corte),
        }

    def _identificar_camada_gargalo(self, arestas_corte: List[dict]) -> str:
        camadas = set()
        for aresta in arestas_corte:
            if aresta["origem"] == "FONTE":
                camadas.add("producao")
            elif aresta["origem"] == "FROTA_ENTRADA" and aresta["destino"] == "FROTA_SAIDA":
                camadas.add("frota")
            elif aresta["destino"] == "SORVEDOURO":
                camadas.add("regioes")

        if not camadas:
            return "nenhum"

        return " e ".join(sorted(camadas))

    def diagnostico(self) -> dict:
        return {
            "quantidade_estacoes": len(self.estacoes),
            "quantidade_regioes": len(self.regioes),
            "quantidade_vertices": self.grafo_geografico.quantidade_vertices(),
            "quantidade_arestas": self.grafo_geografico.quantidade_arestas(),
            "grafo_conectado": self.grafo_geografico.esta_conectado(),
            "capacidade_producao_total": sum(e["capacidade_producao_hora"] for e in self.estacoes),
            "capacidade_frota_total": self.frota["quantidade_entregadores"] * self.frota["entregas_por_entregador_hora"],
            "capacidade_regioes_total": sum(r["limite_pedidos_hora"] for r in self.regioes),
        }