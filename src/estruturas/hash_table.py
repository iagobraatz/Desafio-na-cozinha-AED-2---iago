class TabelaHash:
    def __init__(self, tamanho=101):
        self.tamanho = tamanho
        self.tabela = [[] for _ in range(tamanho)]

    def funcao_hash(self, chave):
        return hash(chave) % self.tamanho

    def inserir(self, chave, valor):
        indice = self.funcao_hash(chave)
        bucket = self.tabela[indice]

        for i, (k, v) in enumerate(bucket):
            if k == chave:
                bucket[i] = (chave, valor)
                return

        bucket.append((chave, valor))

    def buscar(self, chave):
        indice = self.funcao_hash(chave)
        bucket = self.tabela[indice]

        for k, v in bucket:
            if k == chave:
                return v

        return None

    def remover(self, chave):
        indice = self.funcao_hash(chave)
        bucket = self.tabela[indice]

        for i, (k, v) in enumerate(bucket):
            if k == chave:
                del bucket[i]
                return True

        return False
# IAGO KAINAN BUBOLZ BRAATZ
    def listar_todos(self):
        elementos = []
        for bucket in self.tabela:
            for k, v in bucket:
                elementos.append((k, v))
        return elementos
