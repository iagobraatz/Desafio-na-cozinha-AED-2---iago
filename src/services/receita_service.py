import json
from pathlib import Path
from typing import List

from models.receita import Receita


class ReceitaService:
    def __init__(self, caminho_arquivo: str) -> None:
        self.caminho_arquivo = Path(caminho_arquivo)

    def carregar_receitas(self) -> List[Receita]:
        if not self.caminho_arquivo.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho_arquivo}")

        with self.caminho_arquivo.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if not isinstance(dados, list):
            raise ValueError("O arquivo JSON deve conter uma lista de receitas.")

        receitas = []
        for item in dados:
            if isinstance(item, dict):
                receitas.append(Receita.a_partir_de_dicionario(item))

        return receitas

    def listar_receitas(self) -> List[Receita]:
        return self.carregar_receitas()

    def buscar_por_id(self, id_receita: str) -> Receita | None:
        for receita in self.carregar_receitas():
            if receita.id_receita == str(id_receita):
                return receita
        return None

    def buscar_por_categoria(self, categoria: str) -> List[Receita]:
        categoria_busca = categoria.strip().lower()
        return [
            receita
            for receita in self.carregar_receitas()
            if receita.categoria.lower() == categoria_busca
        ]
