from typing import List, Optional

from models.receita import Receita
from estruturas.hash_table import TabelaHash
from estruturas.trie import ArvoreTrie
from estruturas.btree import ArvoreB


class BuscaService:
    def __init__(
        self,
        tabela_hash: TabelaHash,
        arvore_trie: ArvoreTrie,
        arvore_b: ArvoreB,
    ) -> None:
        self.tabela_hash = tabela_hash
        self.arvore_trie = arvore_trie
        self.arvore_b = arvore_b

    def buscar_por_id(self, id_receita: str) -> Optional[Receita]:
        return self.tabela_hash.buscar(id_receita)

    def buscar_por_nome_exato(self, nome: str) -> List[Receita]:
        return self.arvore_trie.buscar_exato(nome)

    def buscar_por_prefixo(self, prefixo: str) -> List[Receita]:
        return self.arvore_trie.buscar_prefixo(prefixo)

    def buscar_por_categoria(self, categoria: str, receitas: List[Receita]) -> List[Receita]:
        categoria_normalizada = categoria.strip().lower()
        return [
            receita
            for receita in receitas
            if receita.categoria.lower() == categoria_normalizada
        ]

    def buscar_por_ingrediente(self, ingrediente: str, receitas: List[Receita]) -> List[Receita]:
        ingrediente_normalizado = ingrediente.strip().lower()
        resultado = []

        for receita in receitas:
            for ing in receita.ingredientes:
                if ingrediente_normalizado in ing.lower():
                    resultado.append(receita)
                    break

        return resultado

    def buscar_por_tempo(self, tempo_preparo: int) -> List[Receita]:
        return self.arvore_b.buscar(tempo_preparo)

    def buscar_por_custo(self, custo_estimado: float) -> List[Receita]:
        return self.arvore_b.buscar(custo_estimado)
# IAGO KAINAN BUBOLZ BRAATZ
    def buscar_por_avaliacao(self, avaliacao_clientes: float) -> List[Receita]:
        return self.arvore_b.buscar(avaliacao_clientes)