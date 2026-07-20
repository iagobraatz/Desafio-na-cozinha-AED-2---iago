from typing import Dict, List, Tuple


class InovacaoService:
    def __init__(self, logistica_service) -> None:
        self.logistica_service = logistica_service

    def obter_nome(self, vertice: str) -> str:
        return self.logistica_service.obter_nome(vertice)

    def _construir_matriz_distancias(self, pontos: List[str]) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], List[str]]]:
        matriz: Dict[Tuple[str, str], float] = {}
        caminhos: Dict[Tuple[str, str], List[str]] = {}

        for origem in pontos:
            for destino in pontos:
                if origem == destino:
                    matriz[(origem, destino)] = 0
                    caminhos[(origem, destino)] = [origem]
                    continue

                resultado = self.logistica_service.menor_caminho(origem, destino)
                if not resultado["encontrado"]:
                    raise ValueError(f"Não há rota entre {origem} e {destino} na rede de entrega.")

                matriz[(origem, destino)] = resultado["tempo_total_min"]
                caminhos[(origem, destino)] = resultado["caminho"]

        return matriz, caminhos

    def _rota_vizinho_mais_proximo(
        self, ponto_partida: str, pontos_visita: List[str], matriz: Dict[Tuple[str, str], float]
    ) -> List[str]:
        nao_visitados = set(pontos_visita)
        rota = [ponto_partida]
        atual = ponto_partida

        while nao_visitados:
            proximo = min(nao_visitados, key=lambda ponto: matriz[(atual, ponto)])
            rota.append(proximo)
            nao_visitados.remove(proximo)
            atual = proximo

        return rota

    def _custo_rota(self, rota: List[str], matriz: Dict[Tuple[str, str], float]) -> float:
        return sum(matriz[(rota[i], rota[i + 1])] for i in range(len(rota) - 1))

    def _melhorar_com_2opt(
        self, rota: List[str], matriz: Dict[Tuple[str, str], float], fixar_final: bool
    ) -> Tuple[List[str], float]:
        melhor_rota = rota[:]
        melhor_custo = self._custo_rota(melhor_rota, matriz)
        limite_j = len(melhor_rota) - 2 if fixar_final else len(melhor_rota) - 1

        if limite_j < 2:
            return melhor_rota, melhor_custo

        melhorou = True
        while melhorou:
            melhorou = False
            for i in range(1, limite_j):
                for j in range(i + 1, limite_j + 1):
                    nova_rota = melhor_rota[:i] + melhor_rota[i:j + 1][::-1] + melhor_rota[j + 1:]
                    novo_custo = self._custo_rota(nova_rota, matriz)

                    if novo_custo < melhor_custo - 1e-9:
                        melhor_rota = nova_rota
                        melhor_custo = novo_custo
                        melhorou = True

        return melhor_rota, melhor_custo

    def _expandir_rota_com_caminhos(
        self, rota: List[str], caminhos: Dict[Tuple[str, str], List[str]]
    ) -> List[str]:
        expandida = [rota[0]]
        for i in range(len(rota) - 1):
            segmento = caminhos[(rota[i], rota[i + 1])]
            expandida.extend(segmento[1:])
        return expandida

    def calcular_rota_entrega(
        self, ponto_partida: str, pontos_visita: List[str], retornar_ao_inicio: bool = False
    ) -> dict:
        if not pontos_visita:
            raise ValueError("É necessário informar ao menos um ponto de visita.")

        pontos = [ponto_partida] + list(pontos_visita)
        for ponto in pontos:
            if not self.logistica_service.grafo_geografico.existe_vertice(ponto):
                raise ValueError(f"Ponto não existe na rede de entrega: {ponto}")

        matriz, caminhos = self._construir_matriz_distancias(pontos)

        rota_inicial = self._rota_vizinho_mais_proximo(ponto_partida, pontos_visita, matriz)
        if retornar_ao_inicio:
            rota_inicial = rota_inicial + [ponto_partida]

        custo_inicial = self._custo_rota(rota_inicial, matriz)
        rota_otimizada, custo_otimizado = self._melhorar_com_2opt(rota_inicial, matriz, retornar_ao_inicio)
        rota_detalhada = self._expandir_rota_com_caminhos(rota_otimizada, caminhos)

        return {
            "rota": rota_otimizada,
            "rota_nomes": [self.obter_nome(ponto) for ponto in rota_otimizada],
            "rota_detalhada_nomes": [self.obter_nome(ponto) for ponto in rota_detalhada],
            "tempo_total_min": round(custo_otimizado, 1),
            "tempo_rota_inicial_min": round(custo_inicial, 1),
            "melhoria_2opt_min": round(custo_inicial - custo_otimizado, 1),
            "quantidade_paradas": len(pontos_visita),
            "retorna_ao_inicio": retornar_ao_inicio,
        }