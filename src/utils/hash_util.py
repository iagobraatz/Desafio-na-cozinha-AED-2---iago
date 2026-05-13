import hashlib


class HashUtil:
    @staticmethod
    def gerar_hash(texto: str) -> str:
        texto = str(texto)
        return hashlib.sha256(texto.encode("utf-8")).hexdigest()

    @staticmethod
    def gerar_hash_receita(receita) -> str:
        dados = (
            f"{receita.id_receita}|{receita.nome}|{receita.categoria}|"
            f"{','.join(receita.ingredientes)}|{receita.tempo_preparo}|"
            f"{receita.custo_estimado}|{receita.avaliacao_clientes}"
        )
        return HashUtil.gerar_hash(dados)

    @staticmethod
    def gerar_hash_dicionario(dados: dict) -> str:
        partes = []
        for chave in sorted(dados.keys()):
            partes.append(f"{chave}={dados[chave]}")
        texto = "|".join(partes)
        return HashUtil.gerar_hash(texto)
# IAGO KAINAN BUBOLZ BRAATZ