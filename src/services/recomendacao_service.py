from typing import List, Literal

from models.receita import Receita


class RecomendacaoService:
    def recomendar_por_criterio(
        self,
        receitas: List[Receita],
        criterio: Literal["custo", "tempo", "avaliacao"] = "custo",
        limite_custo: float | None = None,
        limite_tempo: int | None = None,
        quantidade_maxima: int | None = None,
    ) -> List[Receita]:
        if criterio == "custo":
            receitas_ordenadas = sorted(receitas, key=lambda receita: receita.custo_estimado)
        elif criterio == "tempo":
            receitas_ordenadas = sorted(receitas, key=lambda receita: receita.tempo_preparo)
        elif criterio == "avaliacao":
            receitas_ordenadas = sorted(receitas, key=lambda receita: receita.avaliacao_clientes, reverse=True)
        else:
            raise ValueError("Critério inválido. Use 'custo', 'tempo' ou 'avaliacao'.")

        selecionadas = []
        custo_total = 0.0
        tempo_total = 0

        for receita in receitas_ordenadas:
            if quantidade_maxima is not None and len(selecionadas) >= quantidade_maxima:
                break

            novo_custo_total = custo_total + receita.custo_estimado
            novo_tempo_total = tempo_total + receita.tempo_preparo

            if limite_custo is not None and novo_custo_total > limite_custo:
                continue

            if limite_tempo is not None and novo_tempo_total > limite_tempo:
                continue

            selecionadas.append(receita)
            custo_total = novo_custo_total
            tempo_total = novo_tempo_total

        return selecionadas

    def recomendar_menu_economico(self, receitas: List[Receita], limite_custo: float) -> List[Receita]:
        return self.recomendar_por_criterio(
            receitas=receitas,
            criterio="custo",
            limite_custo=limite_custo,
        )

    def recomendar_menu_rapido(self, receitas: List[Receita], limite_tempo: int) -> List[Receita]:
        return self.recomendar_por_criterio(
            receitas=receitas,
            criterio="tempo",
            limite_tempo=limite_tempo,
        )

    def recomendar_melhores_avaliadas(self, receitas: List[Receita], quantidade_maxima: int = 5) -> List[Receita]:
        return self.recomendar_por_criterio(
            receitas=receitas,
            criterio="avaliacao",
            quantidade_maxima=quantidade_maxima,
        )
