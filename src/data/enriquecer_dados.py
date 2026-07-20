import json
import random
import shutil
from collections import Counter
from pathlib import Path

CAMINHO_RECEITAS = Path("receitas.json")
CAMINHO_BACKUP = Path("receitas_backup.json")

CATEGORIA_PARA_CLASSE = {
    "dessert": "sobremesa",
    "starter": "entrada",
    "side": "entrada",
}

FATOR_MARKUP_MINIMO = 1.6
FATOR_MARKUP_MAXIMO = 2.4


def carregar_receitas(caminho: Path) -> list:
    with caminho.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def calcular_frequencia_ingredientes(receitas: list) -> Counter:
    frequencia = Counter()
    for receita in receitas:
        for ingrediente in receita["ingredientes"]:
            frequencia[ingrediente.strip().lower()] += 1
    return frequencia


def definir_classe_prato(categoria: str) -> str:
    return CATEGORIA_PARA_CLASSE.get(categoria.strip().lower(), "principal")


def calcular_valor_venda(custo_estimado: float) -> float:
    fator = random.uniform(FATOR_MARKUP_MINIMO, FATOR_MARKUP_MAXIMO)
    return round(custo_estimado * fator, 2)


def identificar_ingredientes_raros(ingredientes: list, frequencia: Counter) -> list:
    return [
        ingrediente
        for ingrediente in ingredientes
        if frequencia[ingrediente.strip().lower()] == 1
    ]


def normalizar(valor: float, minimo: float, maximo: float) -> float:
    if maximo == minimo:
        return 0.0
    return (valor - minimo) / (maximo - minimo)


def calcular_pontuacao_dificuldade(receitas: list) -> list:
    tempos = [receita["tempo"] for receita in receitas]
    quantidades_ingredientes = [len(receita["ingredientes"]) for receita in receitas]

    tempo_minimo, tempo_maximo = min(tempos), max(tempos)
    ingredientes_minimo, ingredientes_maximo = min(quantidades_ingredientes), max(quantidades_ingredientes)

    pontuacoes = []
    for receita in receitas:
        tempo_normalizado = normalizar(receita["tempo"], tempo_minimo, tempo_maximo)
        ingredientes_normalizado = normalizar(
            len(receita["ingredientes"]), ingredientes_minimo, ingredientes_maximo
        )
        pontuacoes.append(tempo_normalizado + ingredientes_normalizado)

    return pontuacoes


def definir_limiares_tercis(pontuacoes: list) -> tuple:
    pontuacoes_ordenadas = sorted(pontuacoes)
    n = len(pontuacoes_ordenadas)
    limiar_baixa = pontuacoes_ordenadas[n // 3]
    limiar_media = pontuacoes_ordenadas[(2 * n) // 3]
    return limiar_baixa, limiar_media


def classificar_dificuldade(pontuacao: float, limiar_baixa: float, limiar_media: float) -> str:
    if pontuacao <= limiar_baixa:
        return "baixa"
    if pontuacao <= limiar_media:
        return "media"
    return "alta"


def enriquecer_receita(receita: dict, frequencia: Counter, dificuldade_logistica: str) -> dict:
    ingredientes_raros = identificar_ingredientes_raros(receita["ingredientes"], frequencia)

    receita["classe_prato"] = definir_classe_prato(receita["categoria"])
    receita["valor_venda"] = calcular_valor_venda(receita["custo"])
    receita["ingredientes_raros"] = ingredientes_raros
    receita["possui_ingrediente_raro"] = len(ingredientes_raros) > 0
    receita["dificuldade_logistica"] = dificuldade_logistica

    return receita


def enriquecer_receitas(receitas: list) -> list:
    frequencia = calcular_frequencia_ingredientes(receitas)
    pontuacoes = calcular_pontuacao_dificuldade(receitas)
    limiar_baixa, limiar_media = definir_limiares_tercis(pontuacoes)

    receitas_enriquecidas = []
    for receita, pontuacao in zip(receitas, pontuacoes):
        dificuldade = classificar_dificuldade(pontuacao, limiar_baixa, limiar_media)
        receitas_enriquecidas.append(enriquecer_receita(receita, frequencia, dificuldade))

    return receitas_enriquecidas


def salvar_receitas(receitas: list, caminho: Path) -> None:
    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(receitas, arquivo, indent=2, ensure_ascii=False)


def imprimir_resumo(receitas: list) -> None:
    classes = Counter(receita["classe_prato"] for receita in receitas)
    dificuldades = Counter(receita["dificuldade_logistica"] for receita in receitas)
    com_raro = sum(1 for receita in receitas if receita["possui_ingrediente_raro"])

    print("Distribuição por classe de prato:")
    for classe, quantidade in classes.items():
        print(f"  {classe}: {quantidade}")

    print("Distribuição por dificuldade logística:")
    for dificuldade, quantidade in dificuldades.items():
        print(f"  {dificuldade}: {quantidade}")

    print(f"Receitas com ingrediente raro: {com_raro} de {len(receitas)}")


def main() -> None:
    random.seed(42)

    if not CAMINHO_BACKUP.exists():
        shutil.copyfile(CAMINHO_RECEITAS, CAMINHO_BACKUP)

    receitas = carregar_receitas(CAMINHO_RECEITAS)
    receitas_enriquecidas = enriquecer_receitas(receitas)
    salvar_receitas(receitas_enriquecidas, CAMINHO_RECEITAS)
    imprimir_resumo(receitas_enriquecidas)


if __name__ == "__main__":
    main()