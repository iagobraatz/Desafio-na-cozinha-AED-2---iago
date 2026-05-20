from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Tuple
import pickle


@dataclass
class NoBTree:
    folha: bool = True
    chaves: List[Tuple[float, Any]] = field(default_factory=list)
    filhos: List["NoBTree"] = field(default_factory=list)

    def para_dicionario(self) -> dict:
        return {
            "folha": self.folha,
            "chaves": [self._serializar_par_chave_valor(chave, valor) for chave, valor in self.chaves],
            "filhos": [filho.para_dicionario() for filho in self.filhos],
        }

    @classmethod
    def de_dicionario(cls, dados: dict) -> "NoBTree":
        no = cls(folha=bool(dados.get("folha", True)))
        no.chaves = [cls._desserializar_par_chave_valor(item) for item in dados.get("chaves", [])]
        no.filhos = [cls.de_dicionario(filho) for filho in dados.get("filhos", [])]
        return no

    @staticmethod
    def _serializar_par_chave_valor(chave: float, valor: Any) -> dict:
        if hasattr(valor, "para_dicionario") and callable(getattr(valor, "para_dicionario")):
            valor_serializado = {
                "__tipo__": "objeto",
                "classe": valor.__class__.__name__,
                "dados": valor.para_dicionario(),
            }
        elif isinstance(valor, dict):
            valor_serializado = {
                "__tipo__": "dict",
                "dados": valor,
            }
        else:
            valor_serializado = {
                "__tipo__": "valor",
                "dados": valor,
            }

        return {
            "chave": chave,
            "valor": valor_serializado,
        }

    @staticmethod
    def _desserializar_par_chave_valor(item: dict) -> Tuple[float, Any]:
        chave = item["chave"]
        valor_info = item["valor"]
        tipo = valor_info.get("__tipo__")
        dados = valor_info.get("dados")

        if tipo == "objeto":
            try:
                from models.receita import Receita

                if valor_info.get("classe") == "Receita":
                    valor = Receita.a_partir_de_dicionario(dados)
                else:
                    valor = dados
            except Exception:
                valor = dados
        elif tipo == "dict":
            valor = dados
        else:
            valor = dados

        return chave, valor


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

        resultados = []
        while i < len(no.chaves) and chave == no.chaves[i][0]:
            resultados.append(no.chaves[i][1])
            i += 1

        if resultados:
            return resultados

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

    def _percorrer_em_ordem(self, no: NoBTree, resultado: List[Any]) -> None:
        for i, (chave, valor) in enumerate(no.chaves):
            if not no.folha:
                self._percorrer_em_ordem(no.filhos[i], resultado)
            resultado.append(valor)

        if not no.folha:
            self._percorrer_em_ordem(no.filhos[len(no.chaves)], resultado)

    def salvar_em_binario(self, caminho_arquivo: str | Path) -> None:
        caminho = Path(caminho_arquivo)
        caminho.parent.mkdir(parents=True, exist_ok=True)

        dados = {
            "grau_minimo": self.grau_minimo,
            "raiz": self.raiz.para_dicionario(),
        }

        with caminho.open("wb") as arquivo:
            pickle.dump(dados, arquivo, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def carregar_de_binario(cls, caminho_arquivo: str | Path) -> "ArvoreB":
        caminho = Path(caminho_arquivo)
        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo binário não encontrado: {caminho}")

        with caminho.open("rb") as arquivo:
            dados = pickle.load(arquivo)

        arvore = cls(grau_minimo=int(dados["grau_minimo"]))
        arvore.raiz = NoBTree.de_dicionario(dados["raiz"])
        return arvore

    def existe_arquivo_binario(self, caminho_arquivo: str | Path) -> bool:
        return Path(caminho_arquivo).exists()

    def limpar(self) -> None:
        self.raiz = NoBTree()

    def diagnostico(self) -> dict:
        quantidade_nos, quantidade_chaves, altura = self._coletar_diagnostico(self.raiz)
        return {
            "grau_minimo": self.grau_minimo,
            "quantidade_nos": quantidade_nos,
            "quantidade_chaves": quantidade_chaves,
            "altura": altura,
        }

    def _coletar_diagnostico(self, no: NoBTree) -> Tuple[int, int, int]:
        quantidade_nos = 1
        quantidade_chaves = len(no.chaves)
        altura = 1

        if not no.folha and no.filhos:
            alturas_filhos = []
            for filho in no.filhos:
                nos_filho, chaves_filho, altura_filho = self._coletar_diagnostico(filho)
                quantidade_nos += nos_filho
                quantidade_chaves += chaves_filho
                alturas_filhos.append(altura_filho)
            altura += max(alturas_filhos)

        return quantidade_nos, quantidade_chaves, altura