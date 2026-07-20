import json
import unicodedata
from pathlib import Path

CAMINHO_SAIDA = Path("dependencias_preparo.json")


def gerar_id(nome: str) -> str:
    nome_normalizado = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    return nome_normalizado.lower().replace(" ", "_").replace("(", "").replace(")", "")


PREPAROS_NIVEL_1 = [
    ("Caldo de Carne", 40),
    ("Caldo de Legumes", 30),
    ("Caldo de Frango", 35),
    ("Molho de Tomate", 25),
    ("Molho Branco", 15),
    ("Massa de Pizza", 20),
    ("Massa Folhada", 30),
    ("Massa de Panqueca", 10),
    ("Massa de Macarrão Fresca", 25),
    ("Creme de Confeiteiro", 20),
    ("Calda de Caramelo", 15),
    ("Massa de Torta", 20),
    ("Marinada de Ervas", 10),
]

PREPAROS_NIVEL_2 = [
    ("Molho Bolonhesa", 45, ["Molho de Tomate", "Caldo de Carne"]),
    ("Purê de Batata", 20, ["Caldo de Legumes"]),
    ("Base de Curry", 25, ["Caldo de Frango"]),
    ("Recheio de Frutas Cozidas", 20, ["Calda de Caramelo"]),
    ("Molho Barbecue", 15, ["Molho de Tomate"]),
]

PREPAROS_NIVEL_3 = [
    ("Recheio de Lasanha Completo", 15, ["Molho Bolonhesa", "Molho Branco"]),
]

PREPAROS_CICLO_INCONSISTENTE = [
    ("Massa Recheada", 20, ["Recheio Especial"]),
    ("Recheio Especial", 20, ["Massa Recheada"]),
]

RECEITAS_DEPENDENTES = [
    ("52844", "Lasagne", ["Recheio de Lasanha Completo", "Massa de Macarrão Fresca"]),
    ("52775", "Vegan Lasagna", ["Molho de Tomate", "Massa de Macarrão Fresca"]),
    ("52770", "Spaghetti Bolognese", ["Molho Bolonhesa", "Massa de Macarrão Fresca"]),
    ("52982", "Spaghetti alla Carbonara", ["Massa de Macarrão Fresca"]),
    ("53014", "Pizza Express Margherita", ["Massa de Pizza", "Molho de Tomate"]),
    ("53330", "Cassava pizza", ["Molho de Tomate"]),
    ("52803", "Beef Wellington", ["Massa Folhada", "Caldo de Carne"]),
    ("52876", "Minced Beef Pie", ["Massa Folhada", "Caldo de Carne"]),
    ("52881", "Steak and Kidney Pie", ["Massa Folhada", "Caldo de Carne"]),
    ("52802", "Fish pie", ["Purê de Batata", "Molho Branco"]),
    ("53000", "Vegetable Shepherds Pie", ["Purê de Batata", "Caldo de Legumes"]),
    ("53006", "Moussaka", ["Molho Branco", "Molho de Tomate"]),
    ("52765", "Chicken Enchilada Casserole", ["Molho de Tomate", "Caldo de Frango"]),
    ("52781", "Irish stew", ["Caldo de Carne"]),
    ("53354", "Jamaican Curry Goat", ["Base de Curry"]),
    ("52820", "Katsu Chicken curry", ["Base de Curry", "Caldo de Frango"]),
    ("52868", "Kidney Bean Curry", ["Base de Curry", "Caldo de Legumes"]),
    ("52854", "Pancakes", ["Massa de Panqueca"]),
    ("52855", "Banana Pancakes", ["Massa de Panqueca"]),
    ("52859", "Key Lime Pie", ["Massa de Torta", "Creme de Confeiteiro"]),
    ("52857", "Pumpkin Pie", ["Massa de Torta"]),
    ("53046", "Portuguese custard tarts", ["Massa Folhada", "Creme de Confeiteiro"]),
    ("52909", "Tarte Tatin", ["Massa Folhada", "Recheio de Frutas Cozidas"]),
    ("52916", "Pear Tarte Tatin", ["Massa Folhada", "Recheio de Frutas Cozidas"]),
    ("52772", "Teriyaki Chicken Casserole", ["Caldo de Frango", "Molho Teriyaki"]),
]


def montar_preparos() -> list:
    preparos = []

    for nome, tempo in PREPAROS_NIVEL_1:
        preparos.append({"id": gerar_id(nome), "nome": nome, "tempo_preparo": tempo, "depende_de": []})

    for nome, tempo, dependencias in PREPAROS_NIVEL_2:
        preparos.append({
            "id": gerar_id(nome),
            "nome": nome,
            "tempo_preparo": tempo,
            "depende_de": [gerar_id(d) for d in dependencias],
        })

    for nome, tempo, dependencias in PREPAROS_NIVEL_3:
        preparos.append({
            "id": gerar_id(nome),
            "nome": nome,
            "tempo_preparo": tempo,
            "depende_de": [gerar_id(d) for d in dependencias],
        })

    for nome, tempo, dependencias in PREPAROS_CICLO_INCONSISTENTE:
        preparos.append({
            "id": gerar_id(nome),
            "nome": nome,
            "tempo_preparo": tempo,
            "depende_de": [gerar_id(d) for d in dependencias],
        })

    return preparos


def montar_receitas_dependentes() -> list:
    receitas = []

    for id_receita, nome_receita, dependencias in RECEITAS_DEPENDENTES:
        receitas.append({
            "id_receita": id_receita,
            "nome_receita": nome_receita,
            "depende_de": [gerar_id(d) for d in dependencias],
        })

    return receitas


def validar_referencias(preparos: list, receitas: list) -> list:
    ids_preparos_existentes = {preparo["id"] for preparo in preparos}
    referencias_invalidas = []

    for preparo in preparos:
        for dependencia in preparo["depende_de"]:
            if dependencia not in ids_preparos_existentes:
                referencias_invalidas.append((preparo["id"], dependencia))

    for receita in receitas:
        for dependencia in receita["depende_de"]:
            if dependencia not in ids_preparos_existentes:
                referencias_invalidas.append((receita["id_receita"], dependencia))

    return referencias_invalidas


def imprimir_resumo(preparos: list, receitas: list, referencias_invalidas: list) -> None:
    total_arestas_preparo = sum(len(p["depende_de"]) for p in preparos)
    total_arestas_receita = sum(len(r["depende_de"]) for r in receitas)

    print(f"Preparos cadastrados: {len(preparos)}")
    print(f"Receitas dependentes cadastradas: {len(receitas)}")
    print(f"Total de vértices: {len(preparos) + len(receitas)}")
    print(f"Arestas preparo->preparo: {total_arestas_preparo}")
    print(f"Arestas receita->preparo: {total_arestas_receita}")
    print(f"Total de arestas declaradas: {total_arestas_preparo + total_arestas_receita}")
    print(f"Referências quebradas encontradas (esperado: 1, proposital): {len(referencias_invalidas)}")
    for origem, destino_inexistente in referencias_invalidas:
        print(f"  {origem} -> {destino_inexistente} (não cadastrado)")


def main() -> None:
    preparos = montar_preparos()
    receitas = montar_receitas_dependentes()
    referencias_invalidas = validar_referencias(preparos, receitas)

    dados = {"preparos": preparos, "receitas_dependentes": receitas}

    with CAMINHO_SAIDA.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)

    imprimir_resumo(preparos, receitas, referencias_invalidas)


if __name__ == "__main__":
    main()