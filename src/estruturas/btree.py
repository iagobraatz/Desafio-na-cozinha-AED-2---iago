from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple


@dataclass
class NoBTree:
    folha: bool = True
    chaves: List[Tuple[float, Any]] = field(default_factory=list)
    filhos: List["NoBTree"] = field(default_factory=list)


class ArvoreB:
    def __init__(self, grau_minimo: int = 2):
        if grau_minimo < 2:
            raise ValueError("O grau mínimo da Árvore B deve ser maior ou igual a 2.")

        self.grau_minimo = grau_minimo
        self.raiz = NoBTree()

    def buscar(self, chave: float) -> List[Any]:
        return self._buscar_no(self.raiz, chave)

    def _buscar_no(self, no: NoBTree, chave: float) -> List[Any]:
        i = 0
        while i < len(no.chaves) and chave > no.chaves[i][0]:
            i += 1

        if i < len(no.chaves) and chave == no.chaves[i][0]:
            valores = [no.chaves[i][1]]
            j = i + 1
            while j < len(no.chaves) and no.chaves[j][0] == chave:
                valores.append(no.chaves[j][1])
                j += 1
            return valores

        if no.folha:
            return []

        return self._buscar_no(no.filhos[i], chave)

    def inserir(self, chave: float, valor: Any) -> None:
        raiz = self.raiz

        if len(raiz.chaves) == (2 * self.grau_minimo) - 1:
            nova_raiz = NoBTree(folha=False, filhos=[raiz])
            self._dividir_filho(nova_raiz, 0)
            self.raiz = nova_raiz
            self._inserir_nao_cheio(nova_raiz, chave, valor)
        else:
            self._inserir_nao_cheio(raiz, chave, valor)

    def _inserir_nao_cheio(self, no: NoBTree, chave: float, valor: Any) -> None:
        i = len(no.chaves) - 1

        if no.folha:
            no.chaves.append((0, None))

            while i >= 0 and chave < no.chaves[i][0]:
                no.chaves[i + 1] = no.chaves[i]
                i -= 1

            no.chaves[i + 1] = (chave, valor)
            return

        while i >= 0 and chave < no.chaves[i][0]:
            i -= 1
        i += 1

        if len(no.filhos[i].chaves) == (2 * self.grau_minimo) - 1:
            self._dividir_filho(no, i)
            if chave > no.chaves[i][0]:
                i += 1

        self._inserir_nao_cheio(no.filhos[i], chave, valor)

    def _dividir_filho(self, pai: NoBTree, indice_filho: int) -> None:
        grau = self.grau_minimo
        filho = pai.filhos[indice_filho]
        novo_filho = NoBTree(folha=filho.folha)

        chave_mediana = filho.chaves[grau - 1]

        novo_filho.chaves = filho.chaves[grau:]
        filho.chaves = filho.chaves[: grau - 1]

        if not filho.folha:
            novo_filho.filhos = filho.filhos[grau:]
            filho.filhos = filho.filhos[:grau]

        pai.filhos.insert(indice_filho + 1, novo_filho)
        pai.chaves.insert(indice_filho, chave_mediana)

    def listar_em_ordem(self) -> List[Any]:
        resultado = []
        self._percorrer_em_ordem(self.raiz, resultado)
        return resultado
# IAGO KAINAN BUBOLZ BRAATZ
    def _percorrer_em_ordem(self, no: NoBTree, resultado: List[Any]) -> None:
        for i, (chave, valor) in enumerate(no.chaves):
            if not no.folha:
                self._percorrer_em_ordem(no.filhos[i], resultado)
            resultado.append(valor)

        if not no.folha:
            self._percorrer_em_ordem(no.filhos[len(no.chaves)], resultado)
