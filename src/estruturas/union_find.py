from typing import Any, Dict


class UniaoConjuntos:
    def __init__(self):
        self.pai: Dict[Any, Any] = {}
        self.rank: Dict[Any, int] = {}

    def criar_conjunto(self, elemento: Any) -> None:
        if elemento not in self.pai:
            self.pai[elemento] = elemento
            self.rank[elemento] = 0

    def encontrar(self, elemento: Any) -> Any:
        self.criar_conjunto(elemento)
        if self.pai[elemento] != elemento:
            self.pai[elemento] = self.encontrar(self.pai[elemento])
        return self.pai[elemento]

    def unir(self, a: Any, b: Any) -> bool:
        raiz_a = self.encontrar(a)
        raiz_b = self.encontrar(b)

        if raiz_a == raiz_b:
            return False

        if self.rank[raiz_a] < self.rank[raiz_b]:
            raiz_a, raiz_b = raiz_b, raiz_a

        self.pai[raiz_b] = raiz_a
        if self.rank[raiz_a] == self.rank[raiz_b]:
            self.rank[raiz_a] += 1

        return True

    def mesmo_conjunto(self, a: Any, b: Any) -> bool:
        return self.encontrar(a) == self.encontrar(b)