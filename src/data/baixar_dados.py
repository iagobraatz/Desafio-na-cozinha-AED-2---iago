import requests
import json
import string
import random

todas_receitas = []

for letra in string.ascii_lowercase:
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?f={letra}"
    response = requests.get(url)
    data = response.json()
    # IAGO KAINAN BUBOLZ BRAATZ

    if data["meals"]:
        for r in data["meals"]:
            ingredientes = []
            for i in range(1, 21):
                ing = r[f"strIngredient{i}"]
                if ing and ing.strip() != "":
                    ingredientes.append(ing)

            receita = {
                "id": r["idMeal"],
                "nome": r["strMeal"],
                "categoria": r["strCategory"],
                "ingredientes": ingredientes,
                "tempo": random.randint(10, 60),
                "custo": random.randint(10, 100),
                "avaliacao": round(random.uniform(3, 5), 1)
            }

            todas_receitas.append(receita)

with open("receitas.json", "w", encoding="utf-8") as f:
    json.dump(todas_receitas, f, indent=2, ensure_ascii=False)

print("Arquivo receitas.json criado!")