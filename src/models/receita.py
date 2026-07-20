from dataclasses import dataclass, field
from typing import List


@dataclass
class Receita:
    id_receita: str
    nome: str
    categoria: str
    ingredientes: List[str] = field(default_factory=list)
    tempo_preparo: int = 0
    custo_estimado: float = 0.0
    avaliacao_clientes: float = 0.0
    classe_prato: str = "principal"
    valor_venda: float = 0.0
    ingredientes_raros: List[str] = field(default_factory=list)
    possui_ingrediente_raro: bool = False
    dificuldade_logistica: str = "media"

    def __post_init__(self) -> None:
        self.id_receita = str(self.id_receita)
        self.nome = str(self.nome).strip()
        self.categoria = str(self.categoria).strip()
        self.ingredientes = [str(ingrediente).strip() for ingrediente in self.ingredientes if str(ingrediente).strip()]
        self.tempo_preparo = int(self.tempo_preparo)
        self.custo_estimado = float(self.custo_estimado)
        self.avaliacao_clientes = float(self.avaliacao_clientes)
        self.classe_prato = str(self.classe_prato).strip().lower()
        self.valor_venda = float(self.valor_venda)
        self.ingredientes_raros = [str(ingrediente).strip() for ingrediente in self.ingredientes_raros if str(ingrediente).strip()]
        self.possui_ingrediente_raro = bool(self.possui_ingrediente_raro)
        self.dificuldade_logistica = str(self.dificuldade_logistica).strip().lower()

    @property
    def lucro_estimado(self) -> float:
        return round(self.valor_venda - self.custo_estimado, 2)

    @classmethod
    def a_partir_de_dicionario(cls, dados: dict) -> "Receita":
        return cls(
            id_receita=dados.get("id", ""),
            nome=dados.get("nome", ""),
            categoria=dados.get("categoria", ""),
            ingredientes=dados.get("ingredientes", []),
            tempo_preparo=dados.get("tempo", 0),
            custo_estimado=dados.get("custo", 0),
            avaliacao_clientes=dados.get("avaliacao", 0),
            classe_prato=dados.get("classe_prato", "principal"),
            valor_venda=dados.get("valor_venda", 0),
            ingredientes_raros=dados.get("ingredientes_raros", []),
            possui_ingrediente_raro=dados.get("possui_ingrediente_raro", False),
            dificuldade_logistica=dados.get("dificuldade_logistica", "media"),
        )

    def para_dicionario(self) -> dict:
        return {
            "id": self.id_receita,
            "nome": self.nome,
            "categoria": self.categoria,
            "ingredientes": list(self.ingredientes),
            "tempo": self.tempo_preparo,
            "custo": self.custo_estimado,
            "avaliacao": self.avaliacao_clientes,
            "classe_prato": self.classe_prato,
            "valor_venda": self.valor_venda,
            "ingredientes_raros": list(self.ingredientes_raros),
            "possui_ingrediente_raro": self.possui_ingrediente_raro,
            "dificuldade_logistica": self.dificuldade_logistica,
        }

    def __str__(self) -> str:
        ingredientes = ", ".join(self.ingredientes)
        return (
            f"Receita(id={self.id_receita}, nome={self.nome}, categoria={self.categoria}, "
            f"ingredientes=[{ingredientes}], tempo_preparo={self.tempo_preparo}, "
            f"custo_estimado={self.custo_estimado}, avaliacao_clientes={self.avaliacao_clientes})"
        )