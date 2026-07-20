import json
import random
import unicodedata
from pathlib import Path

CAMINHO_SAIDA = Path("rede_entrega.json")

SEED = 7

ESTACOES_BASE = [
    ("Cozinha Centro", 90),
    ("Cozinha Três Vendas", 60),
    ("Cozinha Fragata", 55),
    ("Cozinha Laranjal", 45),
]

ZONAS = {
    "centro": {
        "estacao": "Cozinha Centro",
        "topologia": "ciclo",
        "regioes": ["Centro", "Porto", "Areal", "São Gonçalo", "Parque Una"],
    },
    "norte": {
        "estacao": "Cozinha Três Vendas",
        "topologia": "ciclo",
        "regioes": ["Três Vendas", "Santa Terezinha", "Lindóia", "Pestano", "Cohab Tablada", "Obelisco"],
    },
    "oeste": {
        "estacao": "Cozinha Fragata",
        "topologia": "caminho",
        "regioes": ["Fragata", "Guabiroba", "Simões Lopes", "Jardim América", "Vila Princesa", "Bom Jesus"],
    },
    "leste": {
        "estacao": "Cozinha Laranjal",
        "topologia": "ciclo",
        "regioes": ["Laranjal", "Valverde", "Balneário dos Prazeres", "Recanto de Portugal", "Santo Antônio"],
    },
    "sul": {
        "estacao": "Cozinha Centro",
        "topologia": "ciclo",
        "regioes": ["Barragem", "Areal Sul", "Navegantes", "Balsa"],
    },
}

PONTES_ENTRE_ZONAS = [
    ("Centro", "Três Vendas"),
    ("Centro", "Fragata"),
    ("Centro", "Laranjal"),
    ("Centro", "Barragem"),
    ("São Gonçalo", "Valverde"),
    ("Bom Jesus", "Navegantes"),
]

REGIOES_SEM_CONEXAO_DIRETA_COM_ESTACAO = {"Balneário dos Prazeres"}

FROTA = {"quantidade_entregadores": 20, "entregas_por_entregador_hora": 4}
KITS_PROMOCIONAIS_DISPONIVEIS = 50


def gerar_id(prefixo: str, nome: str) -> str:
    nome_normalizado = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    slug = nome_normalizado.lower().replace(" ", "_")
    return f"{prefixo}_{slug}"


def montar_estacoes() -> list:
    return [
        {"id": gerar_id("estacao", nome), "nome": nome, "capacidade_producao_hora": capacidade}
        for nome, capacidade in ESTACOES_BASE
    ]


def montar_regioes() -> list:
    regioes = []
    for zona in ZONAS.values():
        for nome in zona["regioes"]:
            regioes.append({
                "id": gerar_id("regiao", nome),
                "nome": nome,
                "limite_pedidos_hora": random.randint(8, 20),
            })
    return regioes


def montar_conexao(origem_nome: str, destino_nome: str, prefixo_origem: str, prefixo_destino: str,
                    tempo_min: int, tempo_max: int) -> dict:
    tempo_estimado = random.randint(tempo_min, tempo_max)
    distancia_km = round(tempo_estimado * 0.4 + random.uniform(-0.5, 0.5), 1)
    return {
        "origem": gerar_id(prefixo_origem, origem_nome),
        "destino": gerar_id(prefixo_destino, destino_nome),
        "tempo_estimado_min": tempo_estimado,
        "distancia_km": max(distancia_km, 0.5),
    }


def montar_conexoes_estacao_regiao() -> list:
    conexoes = []
    for zona in ZONAS.values():
        for nome_regiao in zona["regioes"]:
            if nome_regiao in REGIOES_SEM_CONEXAO_DIRETA_COM_ESTACAO:
                continue
            conexoes.append(
                montar_conexao(zona["estacao"], nome_regiao, "estacao", "regiao", 5, 20)
            )
    return conexoes


def montar_conexoes_intra_zona() -> list:
    conexoes = []
    for zona in ZONAS.values():
        regioes = zona["regioes"]
        quantidade = len(regioes)

        for i in range(quantidade - 1):
            conexoes.append(
                montar_conexao(regioes[i], regioes[i + 1], "regiao", "regiao", 3, 12)
            )

        if zona["topologia"] == "ciclo":
            conexoes.append(
                montar_conexao(regioes[-1], regioes[0], "regiao", "regiao", 3, 12)
            )

        if quantidade >= 6:
            conexoes.append(
                montar_conexao(regioes[0], regioes[3], "regiao", "regiao", 3, 12)
            )

    return conexoes


def montar_conexoes_entre_zonas() -> list:
    return [
        montar_conexao(origem, destino, "regiao", "regiao", 15, 35)
        for origem, destino in PONTES_ENTRE_ZONAS
    ]


def montar_conexoes() -> list:
    return (
        montar_conexoes_estacao_regiao()
        + montar_conexoes_intra_zona()
        + montar_conexoes_entre_zonas()
    )


def calcular_graus(estacoes: list, regioes: list, conexoes: list) -> dict:
    graus = {v["id"]: 0 for v in estacoes + regioes}
    for conexao in conexoes:
        graus[conexao["origem"]] += 1
        graus[conexao["destino"]] += 1
    return graus


def imprimir_resumo(estacoes: list, regioes: list, conexoes: list) -> None:
    total_vertices = len(estacoes) + len(regioes)
    graus = calcular_graus(estacoes, regioes, conexoes)

    print(f"Estações: {len(estacoes)}")
    print(f"Regiões: {len(regioes)}")
    print(f"Total de vértices: {total_vertices}")
    print(f"Total de conexões (arestas): {len(conexoes)}")

    vertices_grau_um = [v for v, grau in graus.items() if grau == 1]
    print(f"Vértices com grau 1 (pontos únicos de falha): {vertices_grau_um}")

    producao_total = sum(e["capacidade_producao_hora"] for e in estacoes)
    capacidade_frota = FROTA["quantidade_entregadores"] * FROTA["entregas_por_entregador_hora"]
    limite_regioes_total = sum(r["limite_pedidos_hora"] for r in regioes)

    print(f"Produção total das estações: {producao_total} pedidos/hora")
    print(f"Capacidade agregada da frota: {capacidade_frota} pedidos/hora")
    print(f"Limite agregado das regiões: {limite_regioes_total} pedidos/hora")


def main() -> None:
    random.seed(SEED)

    estacoes = montar_estacoes()
    regioes = montar_regioes()
    conexoes = montar_conexoes()

    dados = {
        "estacoes": estacoes,
        "regioes": regioes,
        "conexoes": conexoes,
        "frota": FROTA,
        "kits_promocionais_disponiveis": KITS_PROMOCIONAIS_DISPONIVEIS,
    }

    with CAMINHO_SAIDA.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)

    imprimir_resumo(estacoes, regioes, conexoes)


if __name__ == "__main__":
    main()