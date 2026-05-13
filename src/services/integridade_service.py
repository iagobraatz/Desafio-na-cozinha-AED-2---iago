import hashlib
from typing import List, Dict

from models.receita import Receita


class IntegridadeService:
    def gerar_assinatura(self, receita: Receita) -> str:
        dados = (
            f"{receita.id_receita}|{receita.nome}|{receita.categoria}|"
            f"{','.join(receita.ingredientes)}|{receita.tempo_preparo}|"
            f"{receita.custo_estimado}|{receita.avaliacao_clientes}"
        )
        return hashlib.sha256(dados.encode("utf-8")).hexdigest()
# IAGO KAINAN BUBOLZ BRAATZ
    def verificar_receita(self, receita_original: Receita, receita_atual: Receita) -> bool:
        assinatura_original = self.gerar_assinatura(receita_original)
        assinatura_atual = self.gerar_assinatura(receita_atual)
        return assinatura_original == assinatura_atual

    def detectar_repetidas(self, receitas: List[Receita]) -> List[Dict[str, object]]:
        assinaturas = {}
        repetidas = []

        for receita in receitas:
            assinatura = self.gerar_assinatura(receita)

            if assinatura in assinaturas:
                repetidas.append({
                    "receita_original": assinaturas[assinatura],
                    "receita_repetida": receita,
                })
            else:
                assinaturas[assinatura] = receita

        return repetidas

    def detectar_conflitos_por_nome(self, receitas: List[Receita]) -> List[Dict[str, object]]:
        receitas_por_nome = {}
        conflitos = []

        for receita in receitas:
            nome_normalizado = receita.nome.lower().strip()
            assinatura = self.gerar_assinatura(receita)

            if nome_normalizado not in receitas_por_nome:
                receitas_por_nome[nome_normalizado] = {
                    "assinaturas": {assinatura},
                    "receitas": [receita],
                }
            else:
                dados = receitas_por_nome[nome_normalizado]
                if assinatura not in dados["assinaturas"]:
                    dados["assinaturas"].add(assinatura)
                    dados["receitas"].append(receita)

        for nome, dados in receitas_por_nome.items():
            if len(dados["assinaturas"]) > 1:
                conflitos.append({
                    "nome": nome,
                    "receitas": dados["receitas"],
                })

        return conflitos
