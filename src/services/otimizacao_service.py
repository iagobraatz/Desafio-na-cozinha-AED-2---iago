from typing import List, Optional, Set

from models.receita import Receita

UNIDADES_EQUIPE_POR_DIFICULDADE = {"baixa": 1, "media": 2, "alta": 3}
ORDEM_DIFICULDADE = {"baixa": 1, "media": 2, "alta": 3}


class OtimizacaoService:
    def calcular_peso_recurso(self, receita: Receita, recurso: str) -> int:
        if recurso == "orcamento":
            return int(round(receita.custo_estimado))
        if recurso == "tempo":
            return int(receita.tempo_preparo)
        raise ValueError(f"Recurso desconhecido: {recurso}")

    def calcular_valor_criterio(self, receita: Receita, criterio: str) -> float:
        if criterio == "lucro":
            return receita.lucro_estimado
        if criterio == "avaliacao":
            return receita.avaliacao_clientes
        raise ValueError(f"Critério desconhecido: {criterio}")

    def calcular_unidades_equipe(self, receita: Receita) -> int:
        return UNIDADES_EQUIPE_POR_DIFICULDADE.get(receita.dificuldade_logistica, 2)
    def _receita_usa_apenas_ingredientes_disponiveis(
        self, receita: Receita, ingredientes_disponiveis: Optional[Set[str]]
    ) -> bool:
        if ingredientes_disponiveis is None:
            return True

        disponiveis_normalizados = {ingrediente.strip().lower() for ingrediente in ingredientes_disponiveis}
        return all(
            ingrediente.strip().lower() in disponiveis_normalizados for ingrediente in receita.ingredientes
        )

    def otimizar_menu_vip(
        self,
        receitas: List[Receita],
        criterio: str = "lucro",
        recurso_principal: str = "orcamento",
        limite_recurso_principal: int = 0,
        limite_tempo: Optional[int] = None,
        limite_orcamento: Optional[int] = None,
        limite_ingredientes_raros: Optional[int] = None,
        capacidade_equipe: Optional[int] = None,
        ingredientes_disponiveis: Optional[Set[str]] = None,
    ) -> dict:
        if recurso_principal not in ("orcamento", "tempo"):
            raise ValueError("recurso_principal deve ser 'orcamento' ou 'tempo'.")
        if criterio not in ("lucro", "avaliacao"):
            raise ValueError("criterio deve ser 'lucro' ou 'avaliacao'.")
        if limite_recurso_principal < 0:
            raise ValueError("limite_recurso_principal não pode ser negativo.")

        candidatas = [
            receita
            for receita in receitas
             if 0 < self.calcular_peso_recurso(receita, recurso_principal) <= limite_recurso_principal
            and self._receita_usa_apenas_ingredientes_disponiveis(receita, ingredientes_disponiveis)
        ]

        selecionadas = self._resolver_knapsack(candidatas, criterio, recurso_principal, limite_recurso_principal)

        ajustado = False
        while selecionadas and not self._satisfaz_restricoes_secundarias(
            selecionadas, recurso_principal, limite_tempo, limite_orcamento,
            limite_ingredientes_raros, capacidade_equipe,
        ):
            pior = self._encontrar_item_menos_eficiente(selecionadas, criterio, recurso_principal)
            selecionadas.remove(pior)
            ajustado = True

        return self._montar_resultado_vip(selecionadas, criterio, recurso_principal, limite_recurso_principal, ajustado)

    def _resolver_knapsack(
        self, receitas: List[Receita], criterio: str, recurso_principal: str, capacidade: int
    ) -> List[Receita]:
        n = len(receitas)
        dp = [0.0] * (capacidade + 1)
        tomado = [[False] * (capacidade + 1) for _ in range(n)]

        for i, receita in enumerate(receitas):
            peso = self.calcular_peso_recurso(receita, recurso_principal)
            valor = self.calcular_valor_criterio(receita, criterio)

            for c in range(capacidade, peso - 1, -1):
                candidato = dp[c - peso] + valor
                if candidato > dp[c]:
                    dp[c] = candidato
                    tomado[i][c] = True

        selecionadas = []
        c = capacidade
        for i in range(n - 1, -1, -1):
            if tomado[i][c]:
                receita = receitas[i]
                selecionadas.append(receita)
                c -= self.calcular_peso_recurso(receita, recurso_principal)

        return selecionadas

    def _satisfaz_restricoes_secundarias(
        self,
        selecionadas: List[Receita],
        recurso_principal: str,
        limite_tempo: Optional[int],
        limite_orcamento: Optional[int],
        limite_ingredientes_raros: Optional[int],
        capacidade_equipe: Optional[int],
    ) -> bool:
        if recurso_principal != "tempo" and limite_tempo is not None:
            if sum(r.tempo_preparo for r in selecionadas) > limite_tempo:
                return False

        if recurso_principal != "orcamento" and limite_orcamento is not None:
            if sum(r.custo_estimado for r in selecionadas) > limite_orcamento:
                return False

        if limite_ingredientes_raros is not None:
            if sum(len(r.ingredientes_raros) for r in selecionadas) > limite_ingredientes_raros:
                return False

        if capacidade_equipe is not None:
            if sum(self.calcular_unidades_equipe(r) for r in selecionadas) > capacidade_equipe:
                return False

        return True

    def _encontrar_item_menos_eficiente(
        self, selecionadas: List[Receita], criterio: str, recurso_principal: str
    ) -> Receita:
        def pontuacao(receita: Receita) -> float:
            peso = self.calcular_peso_recurso(receita, recurso_principal)
            valor = self.calcular_valor_criterio(receita, criterio)
            return valor / peso if peso > 0 else valor

        return min(selecionadas, key=pontuacao)

    def _montar_resultado_vip(
        self,
        selecionadas: List[Receita],
        criterio: str,
        recurso_principal: str,
        limite_recurso_principal: int,
        ajustado: bool,
    ) -> dict:
        valor_total = sum(self.calcular_valor_criterio(r, criterio) for r in selecionadas)
        uso_recurso_principal = sum(self.calcular_peso_recurso(r, recurso_principal) for r in selecionadas)

        return {
            "receitas": selecionadas,
            "nomes": [r.nome for r in selecionadas],
            "criterio": criterio,
            "recurso_principal": recurso_principal,
            "limite_recurso_principal": limite_recurso_principal,
            "uso_recurso_principal": uso_recurso_principal,
            "valor_total": round(valor_total, 2),
            "tempo_total_min": sum(r.tempo_preparo for r in selecionadas),
            "orcamento_total": round(sum(r.custo_estimado for r in selecionadas), 2),
            "ingredientes_raros_usados": sum(len(r.ingredientes_raros) for r in selecionadas),
            "unidades_equipe_usadas": sum(self.calcular_unidades_equipe(r) for r in selecionadas),
            "ajustado_por_restricoes_secundarias": ajustado,
        }

    def _dificuldade_numerica(self, receita: Receita) -> int:
        return ORDEM_DIFICULDADE.get(receita.dificuldade_logistica, 2)

    def sugerir_menu_dia_dos_namorados(
        self,
        receitas: List[Receita],
        criterio: str = "lucro",
        tempo_maximo: Optional[int] = None,
        custo_maximo: Optional[float] = None,
        dificuldade_maxima: Optional[str] = None,
        ingredientes_disponiveis: Optional[Set[str]] = None,
    ) -> dict:
        if criterio not in ("lucro", "avaliacao", "tempo"):
            raise ValueError("criterio deve ser 'lucro', 'avaliacao' ou 'tempo'.")

        limite_dificuldade_numerica = ORDEM_DIFICULDADE.get(dificuldade_maxima, 3) if dificuldade_maxima else 3

        entradas = self._filtrar_candidatas_namorados(
            receitas, "entrada", tempo_maximo, custo_maximo, limite_dificuldade_numerica, ingredientes_disponiveis
        )
        principais = self._filtrar_candidatas_namorados(
            receitas, "principal", tempo_maximo, custo_maximo, limite_dificuldade_numerica, ingredientes_disponiveis
        )
        sobremesas = self._filtrar_candidatas_namorados(
            receitas, "sobremesa", tempo_maximo, custo_maximo, limite_dificuldade_numerica, ingredientes_disponiveis
        )

        if not entradas or not principais or not sobremesas:
            return {"encontrado": False}

        if tempo_maximo is None and custo_maximo is None:
            melhor_menu = self._melhor_trio_sem_restricao_cruzada(entradas, principais, sobremesas, criterio)
            melhor_pontuacao = self._pontuar_menu_namorados(melhor_menu, criterio)
        else:
            melhor_menu, melhor_pontuacao = self._melhor_trio_por_combinacao(
                entradas, principais, sobremesas, criterio, tempo_maximo, custo_maximo
            )

        if melhor_menu is None:
            return {"encontrado": False}

        return self._montar_resultado_namorados(melhor_menu, melhor_pontuacao, criterio, tempo_maximo, custo_maximo)
    
    def _filtrar_candidatas_namorados(
        self,
        receitas: List[Receita],
        classe_prato: str,
        tempo_maximo: Optional[int],
        custo_maximo: Optional[float],
        limite_dificuldade_numerica: int,
        ingredientes_disponiveis: Optional[Set[str]] = None,
    ) -> List[Receita]:
        candidatas = []
        for receita in receitas:
            if receita.classe_prato != classe_prato:
                continue
            if tempo_maximo is not None and receita.tempo_preparo > tempo_maximo:
                continue
            if custo_maximo is not None and receita.custo_estimado > custo_maximo:
                continue
            if self._dificuldade_numerica(receita) > limite_dificuldade_numerica:
                continue
            if not self._receita_usa_apenas_ingredientes_disponiveis(receita, ingredientes_disponiveis):
                continue
            candidatas.append(receita)
        return candidatas

    def _valor_individual_namorados(self, receita: Receita, criterio: str) -> float:
        if criterio == "lucro":
            return receita.lucro_estimado
        if criterio == "avaliacao":
            return receita.avaliacao_clientes
        if criterio == "tempo":
            return -receita.tempo_preparo
        raise ValueError(f"Critério desconhecido: {criterio}")

    def _melhor_trio_sem_restricao_cruzada(
        self, entradas: List[Receita], principais: List[Receita], sobremesas: List[Receita], criterio: str
    ) -> tuple:
        melhor_entrada = max(entradas, key=lambda r: self._valor_individual_namorados(r, criterio))
        melhor_principal = max(principais, key=lambda r: self._valor_individual_namorados(r, criterio))
        melhor_sobremesa = max(sobremesas, key=lambda r: self._valor_individual_namorados(r, criterio))
        return (melhor_entrada, melhor_principal, melhor_sobremesa)

    def _melhor_trio_por_combinacao(
        self,
        entradas: List[Receita],
        principais: List[Receita],
        sobremesas: List[Receita],
        criterio: str,
        tempo_maximo: Optional[int],
        custo_maximo: Optional[float],
    ) -> tuple:
        melhor_menu = None
        melhor_pontuacao = float("-inf")

        for entrada in entradas:
            for principal in principais:
                tempo_parcial = entrada.tempo_preparo + principal.tempo_preparo
                custo_parcial = entrada.custo_estimado + principal.custo_estimado

                if tempo_maximo is not None and tempo_parcial > tempo_maximo:
                    continue
                if custo_maximo is not None and custo_parcial > custo_maximo:
                    continue

                for sobremesa in sobremesas:
                    if tempo_maximo is not None and tempo_parcial + sobremesa.tempo_preparo > tempo_maximo:
                        continue
                    if custo_maximo is not None and custo_parcial + sobremesa.custo_estimado > custo_maximo:
                        continue

                    trio = (entrada, principal, sobremesa)
                    pontuacao = self._pontuar_menu_namorados(trio, criterio)
                    if pontuacao > melhor_pontuacao:
                        melhor_pontuacao = pontuacao
                        melhor_menu = trio

        return melhor_menu, melhor_pontuacao

    def _pontuar_menu_namorados(self, trio: tuple, criterio: str) -> float:
        if criterio == "lucro":
            return sum(r.lucro_estimado for r in trio)
        if criterio == "avaliacao":
            return sum(r.avaliacao_clientes for r in trio) / len(trio)
        if criterio == "tempo":
            return -sum(r.tempo_preparo for r in trio)
        raise ValueError(f"Critério desconhecido: {criterio}")

    def _montar_resultado_namorados(
        self, trio: tuple, pontuacao: float, criterio: str, tempo_maximo: Optional[int], custo_maximo: Optional[float]
    ) -> dict:
        entrada, principal, sobremesa = trio
        valor_total = sum(r.valor_venda for r in trio)
        custo_total = sum(r.custo_estimado for r in trio)
        tempo_total = sum(r.tempo_preparo for r in trio)
        avaliacao_media = sum(r.avaliacao_clientes for r in trio) / 3
        dificuldade_final = max(trio, key=self._dificuldade_numerica).dificuldade_logistica

        return {
            "encontrado": True,
            "entrada": entrada.nome,
            "prato_principal": principal.nome,
            "sobremesa": sobremesa.nome,
            "valor_total_venda": round(valor_total, 2),
            "custo_estimado": round(custo_total, 2),
            "lucro_estimado": round(valor_total - custo_total, 2),
            "tempo_total_preparo_min": tempo_total,
            "avaliacao_media": round(avaliacao_media, 2),
            "dificuldade_logistica": dificuldade_final,
            "pontuacao": round(pontuacao, 2),
            "justificativa": self._gerar_justificativa_namorados(trio, criterio, tempo_maximo, custo_maximo),
        }

    def _gerar_justificativa_namorados(
        self, trio: tuple, criterio: str, tempo_maximo: Optional[int], custo_maximo: Optional[float]
    ) -> str:
        lucro_total = sum(r.lucro_estimado for r in trio)
        avaliacao_media = sum(r.avaliacao_clientes for r in trio) / 3
        tempo_total = sum(r.tempo_preparo for r in trio)
        dificuldade_final = max(trio, key=self._dificuldade_numerica).dificuldade_logistica

        motivos_por_criterio = {
            "lucro": f"apresentar o maior lucro estimado entre as combinações viáveis (R$ {lucro_total:.2f})",
            "avaliacao": f"apresentar a maior avaliação média entre as combinações viáveis ({avaliacao_media:.1f})",
            "tempo": f"apresentar o menor tempo total de preparo entre as combinações viáveis ({tempo_total} minutos)",
        }

        restricoes_respeitadas = []
        if tempo_maximo is not None:
            restricoes_respeitadas.append(f"o limite de {tempo_maximo} minutos de preparo")
        if custo_maximo is not None:
            restricoes_respeitadas.append(f"o limite de custo de R$ {custo_maximo:.2f}")

        texto = f"O menu foi escolhido por {motivos_por_criterio[criterio]}"
        if restricoes_respeitadas:
            texto += ", respeitando " + " e ".join(restricoes_respeitadas)

        if criterio == "avaliacao":
            texto += f". Dificuldade logística {dificuldade_final}."
        else:
            texto += f". Avaliação média de {avaliacao_media:.1f} e dificuldade logística {dificuldade_final}."

        return texto